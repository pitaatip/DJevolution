'''
Created on 22-04-2012

@author: pita
'''


import array
import random

from deap import benchmarks, algorithms
from deap import base
from deap import creator
from deap import tools
from alg_helper import eaSimple

L = 32
U = -4.0
V = 4.0
DIM = 20

def rastrigin_arg0(sol):
    return benchmarks.rastrigin(convertArrToFloat(sol))

def binListToInt(l):
    w=''
    for a in l:
        w=''.join([w,str(a)])
    return int(w,2)

def sliceIntGen(arr,slice_n):
    for i in xrange(0,len(arr)-slice_n,slice_n):
        yield binListToInt(arr[i:i+slice_n].tolist())

def convertArrToFloat(arr):
    x=[]
    for a in sliceIntGen(arr,L):
        x.append(U + (float(a) / (2**float(L) -1.0) )*(V - U))
    return x


def main(population_size):
    random.seed(64)
    
    creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax) #@UndefinedVariable
    
    toolbox = base.Toolbox()
    
    # Attribute generator
    toolbox.register("attr_bool", random.randint, 0, 1)
    
    # Structure initializers
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, DIM*L) #@UndefinedVariable
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    
    toolbox.register("evaluate", rastrigin_arg0)
    toolbox.register("mate", tools.cxTwoPoints)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.001)
    toolbox.register("select", tools.selTournament, tournsize=5)
    
    pop = toolbox.population(n=population_size)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", tools.mean)
    stats.register("std", tools.std)
    stats.register("min", min)
    stats.register("max", max)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=1, ngen=100, stats=stats,
                        halloffame=hof, verbose=True)
    
    return pop, stats, hof

if __name__ == "__main__":
        print "\nDimension: "+str(DIM)
        pop,stats,hof = main(300)
        print "Best individual:  " + str(convertArrToFloat(hof[-1]))
        print "Rastrigin value: " + str(rastrigin_arg0(hof[-1])[0]) + "\n\n\n"
    
#    for l in xrange(16,80,8):
#        L = l
#        print "\nDimension: "+str(DIM)
#        pop,stats,hof = main()
#        print "Best individual:  " + str(convertArrToFloat(hof[-1]))
#        print "Rastrigin value: " + str(rastrigin_arg0(hof[-1])[0]) + "\n\n\n"