from datetime import datetime
from time import sleep
import simple_genetic_algorithm
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


def main():
    # initialize connection to database
    connection = pymongo.Connection()
    db = connection['djevolution_db']
    while True:
        computations_ = db['VisualControllerApp_computation']
        for computation in computations_.find({"computed": False}):
            compute(computation)
            computations_.save(computation)
        print 'finished pooling computations. Waiting...'
        sleep(5)




if __name__ == '__main__':
    main()
