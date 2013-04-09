import random
from base_algorithm import BaseMultiAlgorithm

'''
Created on 13-11-2012

@author: wysek
'''

class Spea2Algorithm(BaseMultiAlgorithm):
    def __init__(self, monitoring, problem, configuration, is_part_spacing, parallel=None, rank=None):
        BaseMultiAlgorithm.__init__(self, monitoring, problem, configuration, is_part_spacing, parallel, rank)

    def set_globals(self):
        if self.comp_prop:
            self.N = self.comp_prop["N"]
            self.Nbar = self.comp_prop["Nbar"]
            self.GEN = self.comp_prop["GEN"]
        else:
            self.N = 80
            self.GEN = 100
            self.Nbar = 40

    def main_computation_body(self, pop, toolbox):
        # Step 1 Initialization
        archive = []
        curr_gen = 1

        while True:
            if not self.rank:
                print "CURRENT GEN: {}".format(curr_gen)

            # Step 2 Fitness assignement
            toolbox.evaluate(toolbox.eval_ind, pop)
            toolbox.evaluate(toolbox.eval_ind, archive)

            # Step 3 Environmental selection
            archive, archive_fitness = toolbox.select(pop + archive, k=self.Nbar)

            # Step 4 Termination
            if curr_gen >= self.GEN:
                final_set = archive
                break

            # Step 5 Mating Selection
            mating_pool = toolbox.selectTournament(archive, k=self.N, fitness=archive_fitness)
            offspring_pool = map(toolbox.clone, mating_pool)

            # Step 6 Variation
            # crossover 100% and mutation 6%
            for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
                toolbox.mate(child1, child2)

            for mutant in offspring_pool:
                if random.random() < 0.06:
                    toolbox.mutate(mutant)

            pop = offspring_pool

            self.monitor(curr_gen - 1, pop)

            self.compute_partial_spacing(archive)

            if self.parallel and "DEMES" in self.parallel:
                if curr_gen % self.migration_rate == 0 and curr_gen > 0:
                    print "DEME {} MIGRATING".format(self.rank)
                    toolbox.migrate(pop)

            curr_gen += 1

        self.final_front = final_set