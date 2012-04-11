'''
Created on 09-04-2012

@author: pita
'''
from deap import creator, tools, base, benchmarks, algorithms
import numpy
import sys
import logging
import random

_logger = logging.getLogger("deap.algorithms")
logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

def varLambda(toolbox, population, lambda_, cxpb, mutpb):
    assert (cxpb + mutpb) <= 1.0, ("The sum of the crossover and mutation "
        "probabilities must be smaller or equal to 1.0.")
        
    offsprings = []
    nb_offsprings = 0
    while nb_offsprings < lambda_:
        op_choice = random.random()
        if op_choice < cxpb:            # Apply crossover
            ind1, ind2 = random.sample(population, 2)
            ind1 = toolbox.clone(ind1)
            ind2 = toolbox.clone(ind2)
            toolbox.mate(ind1, ind2)
            del ind1.fitness.values, ind2.fitness.values
            offsprings.append(ind1)
            offsprings.append(ind2)
            nb_offsprings += 2
        elif op_choice < cxpb + mutpb:  # Apply mutation
            ind = random.choice(population) # select
            ind = toolbox.clone(ind) # clone
            toolbox.mutate(ind)
            del ind.fitness.values
            offsprings.append(ind)
            nb_offsprings += 1
        else:                           # Apply reproduction
            offsprings.append(random.choice(population))
            nb_offsprings += 1
    
    # Remove the exedant of offsprings
    if nb_offsprings > lambda_:
        del offsprings[lambda_:]
    
    return offsprings


#Modified by me eamuplus func
def eaMuPlusLambda(toolbox, population, mu, lambda_, cxpb, mutpb, ngen, stats=None, halloffame=None, final_stop=None):
    
    _logger.info("Start of evolution")

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    _logger.debug("Evaluated %i individuals", len(invalid_ind))

    if halloffame is not None:
        halloffame.update(population)
    if stats is not None:
        stats.update(population)
    gen = 0
    while(final_stop(sorted(list(halloffame[-1])))):
        _logger.debug("Evolving generation %i", gen)
        gen+=1
        
        # Variate the population
        offsprings = varLambda(toolbox, population, lambda_, cxpb, mutpb)
        
        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offsprings if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit
        
        _logger.debug("Evaluated %i individuals", len(invalid_ind))
        
        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offsprings)

        # Select the next generation population
        population[:] = toolbox.select(population + offsprings, mu)

        # Update the statistics with the new population
        if stats is not None:
            stats.update(population)
        
        # Log statistics on the current generation
        if stats is not None:
            _logger.debug(stats)
    
    _logger.critical(stats)
    _logger.info("End of (successful) evolution")
    return population

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
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
    eaMuPlusLambda(toolbox, pop, 100, 100, 0.7 , 0.01, N_GEN, halloffame=hof, stats=stats,final_stop=final)
    
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof
    
#computes eaMuPlusLambda until func is smaller than 1    
def compute_till_best2():
    random.seed(47)
    pop = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("Avg", tools.mean)
    stats.register("Std", tools.std)
    stats.register("Min", min)
    stats.register("Max", max)
        
    eaMuPlusLambda(toolbox, pop, 100, 100, 0.4 , 0.3, N_GEN, stats=stats, halloffame=hof, final_stop=final)
    
    return sorted(list(hof[-1]))
    
    #return pop, stats, hof

def main():
    best_in=compute_till_best()
    logging.critical("Best individual is %s, %s", (lambda x: sorted(list(x)))(best_in)) 
    

if __name__ == '__main__':
    main()
