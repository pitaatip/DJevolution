'''
Created on Apr 11, 2012

@author: wysek
'''

from deap import creator, tools, base, benchmarks, algorithms, dtm
import numpy
import sys
import logging
import random
import algorithms_helper

_logger = logging.getLogger("deap.algorithms")
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)


creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", numpy.ndarray, fitness=creator.FitnessMin) #@UndefinedVariable

toolbox = base.Toolbox()
toolbox.register("attr", lambda :numpy.random.random() * 10 - 5)

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr, n=100) #@UndefinedVariable
toolbox.register("population", tools.initRepeat, list, toolbox.individual) 

toolbox.register("evaluate", benchmarks.rastrigin)
#uniform lepszy od cxtwopoint
#blend the best 0.2 optimum
toolbox.register("mate", tools.cxBlend, alpha=0.2)
#toolbox.register("mate", tools.cxUniform, indpb=0.4)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.02)
toolbox.register("select", tools.selTournament, tournsize=7)


MU = 140
LAMBDA = 280
N_GEN = 220
DEMES_NR = 5
MIG_RATE = 20
MIG_RATIO = 0.1

toolbox.register("migrate", tools.migRing, k=int(MIG_RATIO * MU), selection=tools.selBest,
    replacement=tools.selRandom)

def evalDeme(deme):
    deme[:] = [toolbox.clone(ind) for ind in toolbox.select(deme, len(deme))]
    algorithms_helper.varLambda(toolbox, deme, LAMBDA, 0.3, 0.5)
    
    for ind in deme:
        ind.fitness.values = toolbox.evaluate(ind)
    
    return deme
                 
#computes eaMuPlusLambda for N_GEN generation
def compute():
    random.seed(47)
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
        
    algorithms.eaMuPlusLambda(toolbox, pop, MU, LAMBDA, 0.3 , 0.5, N_GEN, hof)
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof

def final(x):
    a = benchmarks.rastrigin(x)
    print "rastrigin: ",a
    return (a > 1)
    
#computes eaMuPlusLambda until func is smaller than 1    
def compute_till_best():
    random.seed(47)
#    pop = toolbox.population(n=MU)
    #demes = [toolbox.population(n=MU) for _ in xrange(NBR_DEMES)]
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
    
    
    #algorithms_helper.eaMuPlusLambda(toolbox, pop, 100, 100, 0.7 , 0.01, N_GEN, halloffame=hof, stats=stats,final_stop=final)
    
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof
    
#computes eaMuPlusLambda until func is smaller than 1    
def compute_till_best2():
    random.seed(47)
    pop = toolbox.population(n=MU)
    demes = [toolbox.population(n=MU) for _ in xrange(DEMES_NR)]
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values, DEMES_NR)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
    logger = tools.EvolutionLogger(["gen", "evals"] + stats.functions.keys())
    logger.logHeader()
    
    for idx, deme in enumerate(demes):
        for ind in deme:
            ind.fitness.values = toolbox.evaluate(ind)
        stats.update(deme, idx)
        hof.update(deme)
        logger.logGeneration(gen="0.%d" % idx, evals=len(deme), stats=stats, index=idx)
    
    stats.update(demes[0]+demes[1]+demes[2], 3)
    logger.logGeneration(gen=0, evals="-", stats=stats, index=3)
    
    gen = 1
    while gen <= N_GEN:
        
        # We map the evaluation loop
        demes[:] = map(evalDeme, demes)
        #emes[:] = dtm.map(evalDeme, demes)
        for idx, deme in enumerate(demes):
            # To remain a simple example, we do not parallelize stats evaluation (which would have
            # been possible, but imply some subtleties)
            stats.update(deme, idx)
            hof.update(deme)
            logger.logGeneration(gen="%d.%d" % (gen, idx), evals=len(deme), stats=stats, index=idx)
            
        if gen % MIG_RATE == 0:
            toolbox.migrate(demes)
        stats.update(demes[0]+demes[1]+demes[2], 3)
        logger.logGeneration(gen="%d" % gen, evals="-", stats=stats, index=3)
        gen += 1
    
        
    #algorithms_helper.eaMuPlusLambda(toolbox, pop, 100, 100, 0.4 , 0.3, N_GEN, stats=stats, halloffame=hof, final_stop=final)
    
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof

def main():
    best_in=compute_till_best2()
    logging.critical("Best individual is %s, %s", (lambda x: sorted(list(x)))(best_in)) 
    

if __name__ == '__main__':
    main()
