'''
Created on 22-04-2012

@author: pita
'''

import array
import random

from deap import benchmarks, algorithms
from deap import base
from deap import tools
from utils import configuration_executor, problems, alg_helper

class SimpleGeneticAlgorithm(object):
    def __init__(self,monitoring,problem,configuration,is_part_spacing):
        self.monitoring = monitoring
        # retrieve problem from benchmarks
        self.f_problem = getattr(problems, problem)
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
            self.HOF_SIZE = self.comp_prop["HOF_SIZE"]
            self.GEN = self.comp_prop["GEN"]

        else:
            self.L = 32
            self.U = -4.0
            self.V = 4.0
            self.DIM = 20
            self.POP = 300
            self.HOF_SIZE = 1
            self.GEN = 100

    def compute(self):
        # init toolbox
        toolbox = base.Toolbox()
        configuration_executor.execute(self.configuration, toolbox, self.comp_prop)
        self.set_globals()
        # toolbox.register("evaluate", self.f_problem)
        # before tests, only rastrigin
        toolbox.register("evaluate", self.problem_arg)

        # init population
        pop = toolbox.population(n=self.POP)
        hof = tools.HallOfFame(maxsize=self.HOF_SIZE)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", tools.mean)
        stats.register("std", tools.std)
        stats.register("min", min)
        stats.register("max", max)

        population, partial_res = alg_helper.eaSimple(pop, toolbox, cxpb=0.8, mutpb=1, ngen=self.GEN,monitoring=self.monitoring,
            is_partial_spacing=self.is_part_spacing, stats=stats, halloffame=hof, verbose=True)

        print "Best individual:  " + str(self.convertArrToFloat(hof[0]))
        print "Rastrigin value: " + str(hof[0].fitness.values) + "\n\n\n"
        sorted_individuals = [self.convertArrToFloat(ind) for ind in hof]
        fitness_values = [ind.fitness.values[0] for ind in hof]
        stats_results = [stats.data[name][0][self.GEN][-1] for name in stats.functions]
        stats_part_results = [[stats.data[name][0][i][-1] for name in stats.functions] for i in xrange(self.GEN)]

        return sorted_individuals,fitness_values, partial_res, stats_results, stats_part_results

    def problem_arg(self,sol):
        return self.f_problem(self.convertArrToFloat(sol))

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