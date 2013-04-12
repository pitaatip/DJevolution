from deap import   tools
import random
from algorithm.base_algorithm import BaseMultiAlgorithm
from datetime import datetime

'''
Created on 06-06-2012

@author: pita
'''

class NsgaIIAlgorithm(BaseMultiAlgorithm):
    def __init__(self, monitoring, problem, configuration, is_part_spacing, parallel=None, rank=None):
        BaseMultiAlgorithm.__init__(self, monitoring, problem, configuration, is_part_spacing, parallel, rank)

    def set_globals(self):
        if self.comp_prop:
            self.N = self.comp_prop["N"]
            self.GEN = self.comp_prop["GEN"]
        else:
            self.N = 100
            self.GEN = 200

    def main_computation_body(self, pop, toolbox):
        # init population
        toolbox.evaluate(pop, self.timer)

        a = datetime.now()
        # sort using non domination sort (k is the same as n of population - only sort is applied)
        pop = toolbox.select(pop, k=self.N)
        b = datetime.now()
        self.timer[-1] += b - a

        for g in xrange(self.GEN):
            c = datetime.now()
            if not self.rank:
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
            d = datetime.now()
            # evaluate offsprings
            toolbox.evaluate(offspring_pool, self.timer)

            e = datetime.now()
            # extend base population with offsprings, pop is now 2N size
            pop.extend(offspring_pool)

            # sort and select new population
            pop = toolbox.select(pop, k=self.N)

            self.monitor(g, pop)

            self.compute_partial_spacing(pop)
            f = datetime.now()

            self.timer[-1] += (d - c) + (e - d) + (f - e)


            if self.parallel and "DEMES" in self.parallel:
                if g % self.migration_rate == 0 and g > 0:
                    print "DEME MIGRATING"
                    toolbox.migrate(pop)

        self.final_front = tools.sortFastND(pop, k=self.N)[0]

    def main_computation_body_slave(self, pop, toolbox):
        #evaluation
        for x in xrange(self.GEN+1):
            toolbox.evaluate( pop)