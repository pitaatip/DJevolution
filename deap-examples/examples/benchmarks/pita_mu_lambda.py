'''
Created on 09-04-2012

@author: pita
'''
from deap import creator, tools, base, benchmarks, algorithms
import logging
import numpy
import random
import sys

logging.basicConfig(level=logging.CRITICAL, stream=sys.stdout)

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin) #@UndefinedVariable

toolbox = base.Toolbox()
toolbox.register("attr", lambda :numpy.random.random() * 10 - 5)

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, n=20) #@UndefinedVariable
toolbox.register("population", tools.initRepeat, list, toolbox.individual) 

toolbox.register("evaluate", benchmarks.rastrigin)
#uniform lepszy od cxtwopoint
#blend the best 0.2 optimum
toolbox.register("mate", tools.cxBlend, alpha=0.2)
#toolbox.register("mate", tools.cxSimulatedBinary, nu=100)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.02)
toolbox.register("select", tools.selTournament, tournsize=5)

MU = 130
LAMBDA = 260
N_GEN = 210

def computePlus():
    random.seed(47)
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
        
    algorithms.eaMuPlusLambda(toolbox, pop, MU, LAMBDA, 0.3 , 0.5, N_GEN, hof)
    return sorted(list(hof[-1]))

def computeComma():
    random.seed(47)
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
    algorithms.eaMuCommaLambda(toolbox, pop, MU, LAMBDA, 0.3, 0.5, N_GEN,  hof)
    return sorted(list(hof[-1]))


def main():
    best_in=computePlus()
    logging.critical("Best individual is %s, %s", (lambda x: sorted(list(x)))(best_in)) 
    



if __name__ == '__main__':
    main()
