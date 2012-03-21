'''
Created on 21-03-2012

@author: pita
'''
from deap import base, creator, tools
import random
'''
In this example knapsack is represented by dictionary of nr : (weight,value), and
individual is represented by list of boolean (1 if contains item in this field, 0 otherwise)

'''

KNAPSACK_ITEMS = 50
KNAPSACK_MAX_WEIGHT = 50

items = dict([(i, (random.randint(1, 10), random.uniform(0, 100))) for i in xrange(KNAPSACK_ITEMS)])

# Const for punishment
K = max(i[1] for i in items.values()) / min(i[0] for i in items.values())

creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax) #@UndefinedVariable

toolbox = base.Toolbox()

# probability of choosing 1 - 20%
choices = [1, 0, 0, 0, 0]

toolbox.register("attr_item", random.choice, choices)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, n=KNAPSACK_ITEMS) #@UndefinedVariable
toolbox.register("population", tools.initRepeat, list, toolbox.individual) 


def evalKnapsack(individual):
    i = 0
    sum_values = 0
    sum_weights = 0
    for item in individual:
        if (item):
            sum_values += items[i][1]
            sum_weights += items[i][0]
        i += 1
    
    return sum_values - K * max(sum_weights - KNAPSACK_MAX_WEIGHT, 0),

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.02)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("select", tools.selTournament, tournsize=3)


random.seed(64)
pop = toolbox.population(n=100)
CXPB, MUTPB, NGEN = 0.7, 0.2, 100
    
print "Start of evolution"
    
# Evaluate the entire population
fitnesses = map(toolbox.evaluate, pop)
for ind, fit in zip(pop, fitnesses):
    ind.fitness.values = fit
    
print "  Evaluated %i individuals" % len(pop)
    
# Begin the evolution
for g in range(NGEN):
    print "-- Generation %i --" % g
    
    # Select the next generation individuals
    offsprings = toolbox.select(pop, len(pop))
    # Clone the selected individuals
    offsprings = map(toolbox.clone, offsprings)

    # Apply crossover and mutation on the offsprings
    for child1, child2 in zip(offsprings[::2], offsprings[1::2]):
        if random.random() < CXPB:
            toolbox.mate(child1, child2)
            del child1.fitness.values
            del child2.fitness.values

    for mutant in offsprings:
        if random.random() < MUTPB:
            toolbox.mutate(mutant)
            del mutant.fitness.values

    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in offsprings if not ind.fitness.valid]
    fitnesses = map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit
    
    print "  Evaluated %i individuals" % len(invalid_ind)
    
    # Select best from pop and offsprings
    pop[:] = toolbox.select(pop + offsprings,100)
    
    # Gather all the fitnesses in one list and print the stats
    fits = [ind.fitness.values[0] for ind in pop]
    
    length = len(pop)
    mean = sum(fits) / length
    sum2 = sum(x * x for x in fits)
    std = abs(sum2 / length - mean ** 2) ** 0.5
    
    print "  Min %s" % min(fits)
    print "  Max %s" % max(fits)
    print "  Avg %s" % mean
    print "  Std %s" % std

print "-- End of (successful) evolution --"

best_ind = tools.selBest(pop, 1)[0]
print "Best individual is %s, %s" % (best_ind, best_ind.fitness.values)

