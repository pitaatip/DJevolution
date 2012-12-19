from deap import benchmarks, algorithms, base, creator, tools
import random
import sys

'''
Created on 06-06-2012

@author: pita
'''

def my_rand(V=1,U=0):
    return random.random()*(V-U) - (V+U)/2

class BaseAlgorithm(object):
    def __init__(self,monitoring,problem,configuration):
        self.monitoring = monitoring
        self.problem = problem
        self.configuration = configuration

    def compute(self):
        # init toolbox
        toolbox = base.Toolbox()

        self.parse_and_execute_configuration(toolbox)

        # retrieve problem from benchmarks
        f_problem = getattr(benchmarks, self.problem)
        toolbox.register("evaluate", f_problem)

        # init population
        pop = toolbox.population(n=self.N)

        # init list for partial results
        self.partial_res = []

        # main computation body, each algorithm implements it
        self.main_computation_body(pop,toolbox)

        front_ = [(ind.fitness.values[0], ind.fitness.values[1]) for ind in self.final_front]
        return sorted(front_,key=lambda x:x[0]), self.partial_res

    def parse_and_execute_configuration(self,toolbox):
        try:
            # process each line in configuration
            for command in self.configuration.split('\n'):
                if command:
                    # if line is command
                    if " = " in command:
                        print "executing", command
                        exec command
                    # if line should be evaluated
                    else:
                        print "evaluating: ", command
                        eval(command)
        except SyntaxError as e:
            print "Syntax error", e.filename, e.offset, e.lineno, e.text
            return []
        except NameError as e:
            print "Name error", e.message
            return []
        except:
            print "Unexpected error in evaluating configuration:", sys.exc_info()[0]
            print self.configuration
            return []

    def monitor(self,generation,pop):
        if generation % self.monitoring == 0:
            self.partial_res.append(sorted([(ind.fitness.values[0], ind.fitness.values[1]) for ind in pop],key=lambda x:x[0]))

    def main_computation_body(self,pop,toolbox):
        raise NotImplementedError( "Implement this in concrete algorithm" )
