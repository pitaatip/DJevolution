'''
Created on 10-04-2012

@author: pita
'''
import sys
from deap import benchmarks, tools
from time import time
def rastrigin_arg0(sol):
    return benchmarks.rastrigin(sol)[0]

if __name__ == '__main__':
    if len(sys.argv) < 3 or len(sys.argv) %2 != 1:
        print "Use python test_all.py name_of_module1 name_of_func1 name_of_module2 name_of_func2"
        exit()
    for i in xrange(0,len(sys.argv)-2,2):
        module = __import__(sys.argv[i+1])
        func = getattr(module,sys.argv[i+2])
        print "-----"
        print "Executing %s.%s()..."%(sys.argv[i+1],sys.argv[i+2])
        start = time()
        list_of_ind = [func() for _ in xrange(10)]
        stop = time()
        print "It took you %s sek."%int(stop-start)
        if stop - start > 100:
            print "ERROR, TIME EXCEEDED!"
        list_of_val = map(rastrigin_arg0,list_of_ind)
        print "\nAVG: ",tools.mean(list_of_val)
        print "BEST: ",min(list_of_val)
        