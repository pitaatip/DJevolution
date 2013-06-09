import random
from datetime import datetime
from time import sleep
from algorithm.nsgaII_algorithm import NsgaIIAlgorithm
from algorithm.spea2_algorithm import Spea2Algorithm
from algorithm.simple_genetic_algorithm import SimpleGeneticAlgorithm
from mpi4py import MPI

__author__ = 'pita'

def prepareArgs(computation, rank):
    args = {}
    for arg in ['problem','configuration','monitoring','iter_spacing', 'parallel']:
        args[arg] = computation[arg]
    args['rank'] = rank
    args['parallel'] = "MPI_MS"

    return args

def compute(computation, algorithm, rank):
    args = prepareArgs(computation, rank)
    a = datetime.now()
    alg = eval(algorithm)(**args)
    results = [alg.compute() for _ in xrange(computation['repeat'])]

    if rank:
        return

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

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    empty_msg = None

    #master process
    if not rank:
        import pymongo
        connection = pymongo.Connection()
        db = connection['djevolution_db']

        while True:
#            comm.Barrier()
            computations_ = db['VisualControllerApp_computation']
            for computation in computations_.find({"computed": False}):
                comm.bcast(computation)
                compute(computation,computation['algorithm'], rank)
#                comm.Barrier()
                computations_.save(computation)

            comm.bcast(empty_msg)
            print 'finished pooling computations. Waiting...'
            sleep(5)

    #slave process
    else:
        while True:
#            comm.Barrier()
            computation = comm.bcast()
            if computation:
                print "Node", rank, "received a computation."
                compute(computation,computation['algorithm'], rank)
#                comm.Barrier()

            print "Node", rank, "sleeping..."
            sleep(5)

if __name__ == '__main__':
    main()