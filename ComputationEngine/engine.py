import random

from collections import deque
from multiprocessing import Event, Pipe, Process
from datetime import datetime
from time import sleep
import simple_genetic_algorithm
import nsgaII_algorithm
import spea2_algorithm
import demes_fromsite_PIPES

__author__ = 'pita'

import pymongo

def compute(computation):
    size_ = computation['population_size']
    a = datetime.now()
    pop,stats,hof = simple_genetic_algorithm.main(size_)
    b = datetime.now()
    c = b - a
    computation['restrigin_val'] = simple_genetic_algorithm.rastrigin_arg0(hof[-1])[0]
    computation['results'] = simple_genetic_algorithm.convertArrToFloat(hof[-1])
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."


def compute_pipes(computation, computations):
    size_ = computation['population_size']
    random.seed(64)

    NBR_DEMES = 3

    pipes = [Pipe(False) for _ in range(NBR_DEMES)]
    pipes_in = deque(p[0] for p in pipes)
    pipes_out = deque(p[1] for p in pipes)
    pipes_in.rotate(1)
    pipes_out.rotate(-1)

    e = Event()

    processes = [Process(target=demes_fromsite_PIPES.main, args=(i, ipipe, opipe, e, computation, computations, random.random())) for i, (ipipe, opipe) in enumerate(zip(pipes_in, pipes_out))]

    for proc in processes:
        proc.start()

    for proc in processes:
        proc.join()


def compute_nsga(computation):
    problem_ = computation['problem']
    configuration_ = computation['configuration']
    monitor = computation['monitoring']
    repeat = computation['repeat']
    a = datetime.now()
    results = [nsgaII_algorithm.main(monitor,problem_,configuration_) for _ in xrange(repeat)]
    b = datetime.now()
    c = b - a
    computation['new_result'] = [x for (x,_) in results]
    computation['partial_result'] = [x for (_,x) in results]
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."


def compute_spea(computation):
    problem_ = computation['problem']
    configuration_ = computation['configuration']
    monitor = computation['monitoring']
    repeat = computation['repeat']
    a = datetime.now()
    results = [spea2_algorithm.main(monitor,problem_,configuration_) for _ in xrange(repeat)]
    b = datetime.now()
    c = b - a
    computation['new_result'] = [x for (x,_) in results]
    computation['partial_result'] = [x for (_,x) in results]
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."


def main():
    # initialize connection to database
    connection = pymongo.Connection()
    db = connection['djevolution_db']
    while True:
        computations_ = db['VisualControllerApp_computation']
        for computation in computations_.find({"computed": False}):
            print computation
            if computation['algorithm'] == "NSGA":
                compute_nsga(computation)
                computations_.save(computation)
            elif computation['algorithm'] == "SPEA":
                compute_spea(computation)
                computations_.save(computation)
            else:
                if computation['parallel'] == "None":
                    compute(computation)
                    computations_.save(computation)
                elif computation['parallel'] == "Demes pipe model":
                    compute_pipes(computation, computations_)
                else:
                    print "ERROR: MPI Model not implemented yet."
        print 'finished pooling computations. Waiting...'
        sleep(5)




if __name__ == '__main__':
    main()
