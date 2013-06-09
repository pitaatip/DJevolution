import pickle
from deap import base, tools
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
    def __init__(self,monitoring,problem,configuration,iter_spacing,parallel, rank=None):
        self.monitoring = monitoring
        # retrieve problem from problem
        self.f_problem = getattr(problems, problem)
        self.configuration = configuration
        self.iter_spacing = iter_spacing
        self.comp_prop = dict()
        self.rank = rank
        self.parallel = parallel
        # init toolbox
        self.toolbox = base.Toolbox()
        self.temp_spacing = []

    def set_globals(self):
        raise NotImplementedError("Implement this in concrete algorithm")

    def compute(self):

        self.parse_and_execute_configuration()
        self.set_globals()
        self.toolbox.register("eval_ind", self.f_problem)

        if not self.parallel:
            self.toolbox.register("evaluate", parallel_tools.eval_population, self.toolbox.eval_ind)

        elif self.parallel == "MPI_MS":
            self.toolbox.register("evaluate", parallel_tools.evaluate_individuals_in_groups,
                self.toolbox.eval_ind, self.rank)
        elif self.parallel == "MPI_DEMES":
            self.toolbox.register("evaluate", parallel_tools.eval_population, self.toolbox.eval_ind)
            self.node = parallel_tools.Node()
            self.migration_rate = 100
            self.toolbox.register("migrate", parallel_tools.migRingMPI, k=10, node=self.node,
                selection=tools.selBest, rank=self.rank, replacement=random.sample)
        elif self.parallel == "PIPES_DEMES":
            self.migration_rate = 5
            self.toolbox.register("evaluate", parallel_tools.eval_population, self.toolbox.eval_ind)
            self.toolbox.register("migrate", parallel_tools.migRingPipe, k=5, pipein=self.rank[0],
                pipeout=self.rank[1], selection=tools.selBest, replacement=random.sample)
            queue = self.rank[2]

        # main computation body, each algorithm implements it
        # init population
        pop = self.toolbox.population(n=self.comp_prop["N"])

        # init list for partial results and partial spacing
        self.partial_res = []
        self.partial_spacing = []

        # main computation body, each algorithm implements it
        if not self.parallel or not "MS" in self.parallel or not self.rank:
            self.main_computation_body(pop, self.toolbox)
        else:
            self.main_computation_body_slave(pop, self.toolbox)
            return

        objectives = len(self.final_front[0].fitness.values)
        sorted_individuals = sorted(self.final_front, key=lambda x: x.fitness.values[0])
        fitness_values = [[ind.fitness.values[i] for i in xrange(objectives)] for ind in sorted_individuals]
        computed_spacing = self.compute_spacing(sorted_individuals)

        answer_to_return = sorted_individuals, fitness_values, self.partial_res, computed_spacing, self.partial_spacing

        if self.parallel == "PIPES_DEMES":
            queue.put(answer_to_return)
            return

        return answer_to_return

    def compute_spacing(self,pop):
        d_vects = []
        for ind in pop:
            try:
                fs = ind.fitness.values
            except ValueError as e:
                fs = [-1]
                print e
            all = []
            for ind2 in pop:
                if not ind is ind2:
                    try:
                        fs_p = ind2.fitness.values
                    except ValueError as e:
                        fs_p = [1]
                        print e
                    all.append( sum( [abs(f - f_p) for f,f_p in zip(fs,fs_p)]))
            if len(all) > 0:
                d_vects.append(min(all))
        if len(d_vects) == 0:
            return  -1
        d_mean = sum(d_vects) / len(d_vects)
        part = sum( [math.pow(d_mean - d_vect,2) for d_vect in d_vects] )
        return math.sqrt( ( 1.0 / (len(d_vects) - 1.0) ) * part )

    def parse_and_execute_configuration(self):
        configuration_executor.execute(self.configuration, self.toolbox, self.comp_prop)

    def monitor(self,generation,pop):
        if self.monitoring and generation % self.monitoring == 0:
            pop_ = [[i for i in ind.fitness.values] for ind in pop]
            self.partial_res.append(sorted(pop_,key=lambda x:x[0]))

    def compute_partial_spacing(self, curr_gen, pop):
        if self.iter_spacing and curr_gen > 0 and (curr_gen % 10 == 0):
            self.temp_spacing.remove(max(self.temp_spacing))
            self.partial_spacing.append(sum(self.temp_spacing)/len(self.temp_spacing))
            self.temp_spacing = []
        elif self.iter_spacing:
            self.temp_spacing.append(self.compute_spacing(pop))
#
#        if self.iter_spacing and not curr_gen % self.iter_spacing:
#            self.partial_spacing.append([curr_gen, self.compute_spacing(pop)])

    def main_computation_body(self,pop,toolbox):
        raise NotImplementedError("Implement this in concrete algorithm")

    def main_computation_body_slave(self, pop, toolbox):
        raise NotImplementedError("Implement this in concrete algorithm")