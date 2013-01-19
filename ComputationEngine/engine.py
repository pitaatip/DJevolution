import random

from collections import deque
from multiprocessing import Event, Pipe, Process
from datetime import datetime, time
from time import sleep
from nsgaII_algorithm import NsgaIIAlgorithm
from spea2_algorithm import Spea2Algorithm
import demes_fromsite_PIPES
import cloud

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
    for arg in ['problem','configuration','monitoring','is_part_spacing']:
        args[arg] = computation[arg]
    return args

def allDone(iterable):
    for element in iterable:
        if cloud.status(element) != 'done':
            return False
    return True

def compute(computation, algorithm):
    args = prepareArgs(computation)
    a = datetime.now()
    alg = algorithms[algorithm](**args)
    results = [alg.compute() for _ in xrange(computation['repeat'])]
    b = datetime.now()
    c = b - a
    changed_res = [ [u[i] for u in results] for i in xrange(4) ]
    computation['new_result'] = changed_res[0]
    computation['partial_result'] = changed_res[1]
    computation['final_space'] = changed_res[2]
    computation['partial_spacing'] = changed_res[3]
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."


def compute_on_picloud(computation, algorithm):
    args = prepareArgs(computation)
    a = datetime.now()
    alg = algorithms[algorithm](**args)

    # gather jids
    print 'making call to cloud'
    jids = [cloud.call(alg.compute) for _ in xrange(computation['repeat'])]
    print 'list of job ids: ' +str(jids)
    while not allDone(jids):
        print 'some of job has not been accomplished'
        sleep(1)

    print 'all jobs done, gathering results'
    results = [cloud.result(jid) for jid in jids]
    b = datetime.now()
    c = b - a
    changed_res = [ [u[i] for u in results] for i in xrange(4) ]
    computation['new_result'] = changed_res[0]
    computation['partial_result'] = changed_res[1]
    computation['final_space'] = changed_res[2]
    computation['partial_spacing'] = changed_res[3]
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
            elif computation['parallel'] == "picloud":
                compute_on_picloud(computation,computation['algorithm'])
                computations_.save(computation)
            elif computation['parallel'] == "Demes pipe model":
                compute_pipes(computation, computations_)
            else:
                print "ERROR: MPI Model not implemented yet."

        print 'finished pooling computations. Waiting...'
        sleep(5)

if __name__ == '__main__':
    main()
