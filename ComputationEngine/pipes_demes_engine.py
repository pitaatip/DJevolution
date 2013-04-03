import pickle
import random

from collections import deque
from multiprocessing import Queue, Pipe, Process, Pool
from datetime import datetime
from time import sleep
from deap import base
from algorithm.nsgaII_algorithm import NsgaIIAlgorithm
from algorithm.spea2_algorithm import Spea2Algorithm
from algorithm.simple_genetic_algorithm import SimpleGeneticAlgorithm
import demes_fromsite_PIPES
import sys
from utils import configuration_executor

__author__ = 'pita'

import pymongo


def prepareArgs(computation):
    args = {}
    for arg in ['problem','configuration','monitoring','is_part_spacing']:
        args[arg] = computation[arg]

    args['rank'] = None
    args['parallel'] = "PIPES_DEMES"

    return args

def compute(computation, algorithm):
    args = prepareArgs(computation)

    NBR_DEMES = 2  # hardcoded for the moment because VM has only 3 threads
    pipes = [Pipe(False) for _ in range(NBR_DEMES)]
    pipes_in = deque(p[0] for p in pipes)
    pipes_out = deque(p[1] for p in pipes)
    pipes_in.rotate(1)
    pipes_out.rotate(-1)
    processes = list()
    results = list()

    a = datetime.now()
    queue = Queue()



    for iter in xrange(computation['repeat']):
        algs = list()
        processes = list()
        # in order to create all names in module, so deserialization runs painlessly
        configuration_executor.execute(args['configuration'], base.Toolbox(), dict())
        for deme in xrange(NBR_DEMES):
            args['rank'] = (pipes_in[deme], pipes_out[deme], queue)
            algs.append(eval(algorithm)(**args))
            processes.append(Process(target=algs[-1].compute))

        for proc in processes:
            proc.start()

        for deme in xrange(NBR_DEMES):
            results.append(queue.get())

        for proc in processes:
            proc.join()

    b = datetime.now()
    c = b - a
    changed_res = [ [u[i] for u in results] for i in xrange(5) ]
    computation['sorted_individuals'] = changed_res[0]
    computation['fitness_values'] = changed_res[1]
    computation['partial_result'] = changed_res[2]
    computation['final_space'] = changed_res[3]
    computation['partial_spacing'] = changed_res[4]
    computation['computed'] = True
    computation['computation_time'] = str(c.total_seconds()) + "s."

def main():
    connection = pymongo.Connection()
    db = connection['djevolution_db']
    while True:
        computations_ = db['VisualControllerApp_computation']
        for computation in computations_.find({"computed": False}):
                compute(computation,computation['algorithm'])
                computations_.save(computation)


        print 'finished pooling computations. Waiting...'
        sleep(5)

if __name__ == '__main__':
    main()
