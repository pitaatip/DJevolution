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
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.05)
toolbox.register("select", tools.selTournament, tournsize=3)

def compute():
    random.seed(47)
    pop = toolbox.population(n=500)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
    
    algorithms.eaSimple(toolbox, pop, 0.8, 0.1, 100, halloffame=hof)
    #algorithms.eaMuPlusLambda(toolbox, pop, 500, 100, 0.8 , 0.1, 500, hof)
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof

def main():
    best_in=compute()
    logging.critical("Best individual is %s, %s", (lambda x: sorted(list(x)))(best_in)) 
    



if __name__ == '__main__':
    main()
