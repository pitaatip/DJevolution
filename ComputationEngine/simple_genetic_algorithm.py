'''
Created on 22-04-2012

@author: pita
'''

import array
import random

from deap import benchmarks, algorithms
from deap import base
from deap import creator
from deap import tools
import configuration_executor
from alg_helper import eaSimple

class SimpleGeneticAlgorithm(object):
    def __init__(self,monitoring,problem,configuration,is_part_spacing):
        self.monitoring = monitoring
        # retrieve problem from benchmarks
        self.f_problem = getattr(benchmarks, problem)
        self.configuration = configuration
        self.is_part_spacing = is_part_spacing
        self.comp_prop = dict()

    def set_globals(self):
        if self.comp_prop:
            self.L = self.comp_prop["L"]
            self.U = self.comp_prop["U"]
            self.V = self.comp_prop["V"]
            self.DIM = self.comp_prop["DIM"]
            self.POP = self.comp_prop["POP"]
        else:
            self.L = 32
            self.U = -4.0
            self.V = 4.0
            self.DIM = 20
            self.POP = 300

    def compute(self):
        # init toolbox
        toolbox = base.Toolbox()
        configuration_executor.execute(self.configuration, toolbox, self.comp_prop)
        self.set_globals()
        # toolbox.register("evaluate", self.f_problem)
        # before tests, only rastrigin
        toolbox.register("evaluate", self.rastrigin_arg0)
        random.seed(64)

        # init population
        pop = toolbox.population(n=self.POP)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", tools.mean)
        stats.register("std", tools.std)
        stats.register("min", min)
        stats.register("max", max)

        algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=1, ngen=100, stats=stats,
            halloffame=hof, verbose=True)

        print "Best individual:  " + str(self.convertArrToFloat(hof[-1]))
        print "Rastrigin value: " + str(self.rastrigin_arg0(hof[-1])[0]) + "\n\n\n"

        return pop, stats, hof

    def rastrigin_arg0(self,sol):
        return benchmarks.rastrigin(self.convertArrToFloat(sol))

    def binListToInt(self,l):
        w=''
        for a in l:
            w=''.join([w,str(a)])
        return int(w,2)

    def sliceIntGen(self,arr):
        slice_n = self.L
        for i in xrange(0,len(arr)-slice_n,slice_n):
            yield self.binListToInt(arr[i:i+slice_n].tolist())

    def convertArrToFloat(self,arr):
        x=[]
        for a in self.sliceIntGen(arr):
            x.append(self.U + (float(a) / (2**float(self.L) -1.0) )*(self.V - self.U))
        return x