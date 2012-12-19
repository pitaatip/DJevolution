import random

from collections import deque
from multiprocessing import Event, Pipe, Process
from datetime import datetime
from time import sleep
from nsgaII_algorithm import NsgaIIAlgorithm
from spea2_algorithm import Spea2Algorithm
import demes_fromsite_PIPES

__author__ = 'pita'

import pymongo

algorithms = {"NSGA" : NsgaIIAlgorithm,
              "SPEA" : Spea2Algorithm}

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

def prepareArgs(computation):
    args = {}
    for arg in ['problem','configuration','monitoring']:
        args[arg] = computation[arg]
    return args

def compute(computation, algorithm):
    args = prepareArgs(computation)
    a = datetime.now()
    alg = algorithms[algorithm](**args)
    results = [alg.compute() for _ in xrange(computation['repeat'])]
    b = datetime.now()
    c = b - a
    computation['new_result'] = [x for (x,_) in results]
    computation['partial_result'] = [x for (_,x) in results]
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."

def main():
    connection = pymongo.Connection()
    db = connection['djevolution_db']
    while True:
        computations_ = db['VisualControllerApp_computation']
        for computation in computations_.find({"computed": False}):
            print computation
            if computation['parallel'] == "None":
                compute(computation,computation['algorithm'])
                computations_.save(computation)
            elif computation['parallel'] == "Demes pipe model":
                compute_pipes(computation, computations_)
            else:
                print "ERROR: MPI Model not implemented yet."

        print 'finished pooling computations. Waiting...'
        sleep(5)

if __name__ == '__main__':
    main()
