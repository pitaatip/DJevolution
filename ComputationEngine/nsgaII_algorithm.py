from deap import benchmarks, base, tools
import random
import sys
from base_algorithm import BaseAlgorithm, my_rand

'''
Created on 06-06-2012

@author: pita
'''

class NsgaIIAlgorithm(BaseAlgorithm):
    def __init__(self,monitoring,problem,configuration):
        BaseAlgorithm.__init__(self,monitoring,problem,configuration)
        self.N=100
        self.GEN=200

    def main_computation_body(self,pop,toolbox):

        # init population
        for ind in pop:
            ind.fitness.values = toolbox.evaluate(ind)

        # sort using non domination sort (k is the same as n of population - only sort is applied)
        pop = toolbox.select(pop, k=self.N)

        for g in xrange(self.GEN):
            #select parent pool with tournament dominated selection
            parent_pool = toolbox.selectTournament(pop, k=self.N)
            offspring_pool = map(toolbox.clone, parent_pool)

            # Apply crossover and mutation on the offspring
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                if random.random() < 0.9:
                    toolbox.mate(child1, child2)
            for mutant in offspring_pool:
                if random.random() < 0.1:
                    toolbox.mutate(mutant)

            # evaluate offsprings
            for ind in offspring_pool:
                ind.fitness.values = toolbox.evaluate(ind)

            # extend base population with offsprings, pop is now 2N size
            pop.extend(offspring_pool)

            # sort and select new population
            pop = toolbox.select(pop, k=self.N)

            self.monitor(g,pop)

        self.final_front = tools.sortFastND(pop, k=self.N)[0]