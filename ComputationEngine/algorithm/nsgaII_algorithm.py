from deap import   tools
import random
from algorithm.base_algorithm import BaseMultiAlgorithm

'''
Created on 06-06-2012

@author: pita
'''

class NsgaIIAlgorithm(BaseMultiAlgorithm):
    def __init__(self,monitoring,problem,configuration,iter_spacing,parallel, rank=None):
        BaseMultiAlgorithm.__init__(self,monitoring,problem,configuration,iter_spacing,parallel, rank)

    def set_globals(self):
        if self.comp_prop:
            self.N = self.comp_prop["N"]
            self.GEN = self.comp_prop["GEN"]
        else:
            self.N=100
            self.GEN=200

    def main_computation_body(self,pop,toolbox):
        # init population
        self.measurer.start('evaluate_pop')
        toolbox.evaluate(pop)
        self.measurer.stop('evaluate_pop')

        # sort using non domination sort (k is the same as n of population - only sort is applied)
        self.measurer.start('selection_pop')
        pop, main_front = toolbox.select(pop, k=self.N)
        self.measurer.stop('selection_pop')

        for g in xrange(self.GEN):
            if not self.rank:
                print "CURRENT GEN: " + str(g)
            #select parent pool with tournament dominated selection
            self.measurer.start('select_tournament')
            parent_pool = toolbox.selectTournament(pop, k=self.N)
            self.measurer.stop('select_tournament')
            offspring_pool = map(toolbox.clone, parent_pool)

            # Apply crossover and mutation on the offspring
            self.measurer.start('mate_mutate')
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                if random.random() < 0.9:
                    toolbox.mate(child1, child2)
            for mutant in offspring_pool:
                if random.random() < 0.1:
                    toolbox.mutate(mutant)
            self.measurer.stop('mate_mutate')

            # evaluate offsprings
            self.measurer.start('evaluate_off')
            toolbox.evaluate(offspring_pool)
            self.measurer.stop('evaluate_off')

            # extend base population with offsprings, pop is now 2N size
            pop.extend(offspring_pool)

            # sort and select new population
            self.measurer.start('select_new_pop')
            pop, main_front = toolbox.select(pop, k=self.N)
            self.measurer.stop('select_new_pop')

            self.monitor(g,pop)

            self.compute_partial_spacing(g, main_front)

            if self.parallel and "DEMES" in self.parallel:
                if g % self.migration_rate == 0 and g > 0:
                    print "DEME MIGRATING"
                    self.measurer.start('migration')
                    toolbox.migrate(pop)
                    self.measurer.stop('migration')

        self.measurer.start('sort_final_front')
        self.final_front = tools.sortFastND(pop, k=self.N)[0]
        self.measurer.stop('sort_final_front')

    def main_computation_body_slave(self, pop, toolbox):
        #evaluation
        for x in xrange(self.GEN+1):
            toolbox.evaluate( pop)