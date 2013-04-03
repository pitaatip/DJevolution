from multiprocessing import Pool
from deap import   tools
import random
from algorithm.base_algorithm import BaseMultiAlgorithm

'''
Created on 06-06-2012

@author: pita
'''

class NsgaIIAlgorithm(BaseMultiAlgorithm):
    def __init__(self,monitoring,problem,configuration,is_part_spacing,parallel):
        BaseMultiAlgorithm.__init__(self,monitoring,problem,configuration,is_part_spacing,parallel)

    def multi_map(self):
        pool = Pool(2)
        return pool.map

    def simple_map(self):
        return map

    def prepareToolbox(self,parallel,toolbox):
        map_fun = self.maps_fun[parallel]
        toolbox.register("map", map_fun)

    def set_globals(self):
        if self.comp_prop:
            self.N = self.comp_prop["N"]
            self.GEN = self.comp_prop["GEN"]
        else:
            self.N=100
            self.GEN=200

    def main_computation_body(self,pop,toolbox):

        # init population
        self.maps_fun = {"Multiprocess" : self.multi_map(),"None" : self.simple_map() }
        self.prepareToolbox(self.parallel,self.toolbox)
        fit_val = toolbox.map(toolbox.evaluate,pop)
        for ind,fit in zip(pop,fit_val):
            ind.fitness.values = fit
#        for ind in pop:
#            ind.fitness.values = toolbox.evaluate(ind)

        # sort using non domination sort (k is the same as n of population - only sort is applied)
        pop = toolbox.select(pop, k=self.N)

        for g in xrange(self.GEN):
            print "CURRENT GEN: " + str(g)
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
            fit_val = toolbox.map(toolbox.evaluate,offspring_pool)
            for ind,fit in zip(offspring_pool,fit_val):
                ind.fitness.values = fit
#            for ind in offspring_pool:
#                ind.fitness.values = toolbox.evaluate(ind)

            # extend base population with offsprings, pop is now 2N size
            pop.extend(offspring_pool)

            # sort and select new population
            pop = toolbox.select(pop, k=self.N)

            self.monitor(g,pop)

            self.compute_partial_spacing(pop)

        self.final_front = tools.sortFastND(pop, k=self.N)[0]