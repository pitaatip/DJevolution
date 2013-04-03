import random
from algorithm.base_algorithm import BaseMultiAlgorithm

'''
Created on 13-11-2012

@author: wysek
'''

def selTournamentSPEA2(individuals, k, tournsize):
    """Select *k* individuals from the input *individuals* using *k*
    tournaments of *tournsize* individuals. The list returned contains
    references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :returns: A list of selected individuals.

    This function uses the :func:`~random.choice` function from the python base
    :mod:`random` module.
    """
    chosen = []
    for i in xrange(k):
        chosen.append(random.choice(individuals))
        for j in xrange(tournsize - 1):
            aspirant = random.choice(individuals)
            if abs(sum(aspirant.fitness.wvalues)) > abs(sum(chosen[i].fitness.wvalues)):
                chosen[i] = aspirant

    return chosen

class Spea2Algorithm(BaseMultiAlgorithm):
    def __init__(self,monitoring,problem,configuration,is_part_spacing,parallel):
        BaseMultiAlgorithm.__init__(self,monitoring,problem,configuration,is_part_spacing,parallel)

    def set_globals(self):
        if self.comp_prop:
            self.N = self.comp_prop["N"]
            self.Nbar = self.comp_prop["Nbar"]
            self.GEN = self.comp_prop["GEN"]
        else:
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
            archive,archive_fitness  = toolbox.select(pop + archive, k=self.Nbar)

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

            self.monitor(curr_gen - 1,pop)

            self.compute_partial_spacing(archive)

            curr_gen += 1

        self.final_front = final_set