from deap import benchmarks, algorithms, base, creator, tools, dtm
import sys
import math
import configuration_executor

'''
Created on 06-06-2012

@author: pita
'''

class BaseMultiAlgorithm(object):
    def __init__(self,monitoring,problem,configuration,is_part_spacing):
        self.monitoring = monitoring
        # retrieve problem from benchmarks
        self.f_problem = getattr(benchmarks, problem)
        self.configuration = configuration
        self.is_part_spacing = is_part_spacing
        self.comp_prop = dict()
        # init toolbox
        self.toolbox = base.Toolbox()

    def set_globals(self):
        raise NotImplementedError( "Implement this in concrete algorithm" )

    def compute(self):

        self.parse_and_execute_configuration()
        self.set_globals()

        self.toolbox.register("evaluate", self.f_problem)

        # init population
        pop = self.toolbox.population(n=self.comp_prop["N"])

        # init list for partial results and partial spacing
        self.partial_res = []
        self.partial_spacing = []

        # prepare dtm
        self.toolbox.register("map", dtm.map)

        # main computation body, each algorithm implements it
        self.main_computation_body(pop,self.toolbox)

        front_ = [(ind.fitness.values[0], ind.fitness.values[1]) for ind in self.final_front]
        return sorted(front_,key=lambda x:x[0]), self.partial_res, self.compute_spacing(front_), self.partial_spacing

    def compute_spacing(self,pop):
        d_vects = []
        for ind in pop:
            f1, f2 = self.f_problem(ind)
            all = []
            for ind2 in pop:
                if not ind is ind2:
                    f1_p, f2_p = self.f_problem(ind2)
                    all.append(abs(f1_p - f1) + abs(f2_p - f2))
            d_vects.append(min(all))
        d_mean = sum(d_vects) / len(d_vects)
        part = sum( [math.pow(d_mean - d_vect,2) for d_vect in d_vects] )
        return math.sqrt( ( 1.0 / (len(d_vects) - 1.0) ) * part )

    def parse_and_execute_configuration(self):
        configuration_executor.execute(self.configuration, self.toolbox, self.comp_prop)

    def monitor(self,generation,pop):
        if generation % self.monitoring == 0:
            self.partial_res.append(sorted([(ind.fitness.values[0], ind.fitness.values[1]) for ind in pop],key=lambda x:x[0]))

    def compute_partial_spacing(self,pop):
        if self.is_part_spacing:
            self.partial_spacing.append(self.compute_spacing(pop))

    def main_computation_body(self,pop,toolbox):
        raise NotImplementedError( "Implement this in concrete algorithm" )
