import random

from datetime import datetime
from time import sleep
from algorithm.nsgaII_algorithm import NsgaIIAlgorithm
from algorithm.spea2_algorithm import Spea2Algorithm
from algorithm.simple_genetic_algorithm import SimpleGeneticAlgorithm

__author__ = 'pita'

import pymongo

def prepareArgs(computation):
    args = {}
    for arg in ['problem','configuration','monitoring', 'iter_spacing', 'parallel']:
        args[arg] = computation[arg]
    return args

def compute(computation, algorithm):
    args = prepareArgs(computation)
    a = datetime.now()
    alg = eval(algorithm)(**args)
#    alg = algorithms[algorithm](**args)
    results = [alg.compute() for _ in xrange(computation['repeat'])]
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
