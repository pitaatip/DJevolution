from deap import benchmarks, algorithms, base, creator, tools
import random
import sys
from base_algorithm import BaseMultiAlgorithm

'''
Created on 13-11-2012

@author: wysek
'''

class Spea2Algorithm(BaseMultiAlgorithm):
    def __init__(self,monitoring,problem,configuration,is_part_spacing):
        BaseMultiAlgorithm.__init__(self,monitoring,problem,configuration,is_part_spacing)
        self.N=80
        self.GEN=100
        self.Nbar = 40

    def main_computation_body(self,pop,toolbox):
        # Step 1 Initialization
        archive = []
        curr_gen = 1

        while True:
            print "CURRENT GEN: " + str(curr_gen)
            # Step 2 Fitness assignement
            for ind in pop:
                ind.fitness.values = toolbox.evaluate(ind)

            for ind in archive:
                ind.fitness.values = toolbox.evaluate(ind)

            # Step 3 Environmental selection
            archive  = toolbox.select(pop + archive, k=self.Nbar)

            # Step 4 Termination
            if curr_gen >= self.GEN:
                final_set = archive
                break

            # Step 5 Mating Selection
            mating_pool = toolbox.selectTournament(archive, k=self.N)
            offspring_pool = map(toolbox.clone, mating_pool)

            # Step 6 Variation
            # crossover 100% and mutation 6%
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                toolbox.mate(child1, child2)

            for mutant in offspring_pool:
                if random.random() < 0.06:
                    toolbox.mutate(mutant)

            pop = offspring_pool

            self.monitor(curr_gen - 1,pop)

            self.compute_partial_spacing(archive)

            curr_gen += 1

        self.final_front = final_set