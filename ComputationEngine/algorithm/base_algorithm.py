import pickle
from deap import benchmarks, base
import math
from numpy.numarray.util import MathDomainError
from utils import configuration_executor, problems
from utils import parallel_tools
from deap import tools
from collections import deque
from multiprocessing import Pipe, Process

import random

'''
Created on 06-06-2012

@author: pita
'''

class BaseMultiAlgorithm(object):
    def __init__(self, monitoring, problem, configuration, is_part_spacing, parallel, rank):
        self.monitoring = monitoring
        # retrieve problem from benchmarks
        self.f_problem = getattr(problems, problem)
        self.configuration = configuration
        self.is_part_spacing = is_part_spacing
        self.parallel = parallel
        self.rank = rank
        self.comp_prop = dict()
        # init toolbox
        self.toolbox = base.Toolbox()

    def set_globals(self):
        raise NotImplementedError("Implement this in concrete algorithm")

    def compute(self):
        self.parse_and_execute_configuration()
        self.set_globals()
        self.toolbox.register("eval_ind", self.f_problem)

        if not self.parallel:
            self.toolbox.register("evaluate", parallel_tools.eval_population)
        elif self.parallel == "MPI_MS":
            self.toolbox.register("evaluate", parallel_tools.evaluate_individuals_in_groups)
        elif self.parallel == "MPI_DEMES":
            self.toolbox.register("evaluate", parallel_tools.eval_population)
            self.node = parallel_tools.Node()
            self.migration_rate = 5
            self.toolbox.register("migrate", parallel_tools.migRingMPI, k=5, node=self.node,
                selection=tools.selBest, rank=self.rank, replacement=random.sample)
        elif self.parallel == "PIPES_DEMES":
            self.migration_rate = 5
            self.toolbox.register("evaluate", parallel_tools.eval_population)
            self.toolbox.register("migrate", parallel_tools.migRingPipe, k=5, pipein=self.rank[0],
                pipeout=self.rank[1], selection=tools.selBest, replacement=random.sample)
            queue = self.rank[2]

        # init population
        pop = self.toolbox.population(n=self.comp_prop["N"])

        # init list for partial results and partial spacing
        self.partial_res = []
        self.partial_spacing = []

        # main computation body, each algorithm implements it
        self.main_computation_body(pop, self.toolbox)
        objectives = len(self.final_front[0].fitness.values)
        sorted_individuals = sorted(self.final_front, key=lambda x: x.fitness.values[0])
        fitness_values = [[ind.fitness.values[i] for i in xrange(objectives)] for ind in sorted_individuals]
        computed_spacing = self.compute_spacing(sorted_individuals)

        answer_to_return = sorted_individuals, fitness_values, self.partial_res, computed_spacing, self.partial_spacing

        if self.parallel == "PIPES_DEMES":
            queue.put(answer_to_return)
            return

        return answer_to_return

    def compute_spacing(self, pop):
        d_vects = []
        for ind in pop:
            try:
                fs = self.f_problem(ind)
            except ValueError as e:
                fs = [-1]
                print e
            all = []
            for ind2 in pop:
                if not ind is ind2:
                    try:
                        fs_p = self.f_problem(ind2)
                    except ValueError as e:
                        fs_p = [1]
                        print e
                    all.append(sum([abs(f - f_p) for f, f_p in zip(fs, fs_p)]))
            d_vects.append(min(all))
        d_mean = sum(d_vects) / len(d_vects)
        part = sum([math.pow(d_mean - d_vect, 2) for d_vect in d_vects])
        return math.sqrt(( 1.0 / (len(d_vects) - 1.0) ) * part)

    def parse_and_execute_configuration(self):
        configuration_executor.execute(self.configuration, self.toolbox, self.comp_prop)

    def monitor(self, generation, pop):
        if generation % self.monitoring == 0:
            pop_ = [[i for i in ind.fitness.values] for ind in pop]
            self.partial_res.append(sorted(pop_, key=lambda x: x[0]))

    def compute_partial_spacing(self, pop):
        if self.is_part_spacing:
            self.partial_spacing.append(self.compute_spacing(pop))

    def main_computation_body(self, pop, toolbox):
        raise NotImplementedError("Implement this in concrete algorithm")
