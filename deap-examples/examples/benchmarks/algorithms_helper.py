'''
Created on 11-04-2012

@author: pita
'''
from deap import benchmarks
import logging
import random

_logger = logging.getLogger("deap.algorithms")
def rastrigin_arg0(sol):
    return benchmarks.rastrigin(sol)[0]

'''
This is eaMuPlusLabda function from deap0.7 modified so it stops after fulfilling final_stop method
'''
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
    
    _logger.info("End of (successful) evolution. Number of generations computed: %s"%gen)
    return population



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