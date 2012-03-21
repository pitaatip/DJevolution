'''
Created on 21-03-2012

@author: pita
'''
from deap import creator, base, tools, algorithms
import random
import logging
import sys

logging.basicConfig(level=logging.INFO, stream=sys.stdout)

MAX_ITEM = 50
MAX_WEIGHT = 50
NGEN = 10
MU = 50
LAMBDA = 100   


random.seed(64)
creator.create("FitnessMulti", base.Fitness, weights=(-1.0, 1.0))
creator.create("Individual", set, fitness=creator.FitnessMulti) #@UndefinedVariable


# The items' name is an integer, and value is a (weight, value) 2-tuple
items = dict([(i, (random.randint(1, 10), random.uniform(0, 100))) for i in xrange(100)])

toolbox = base.Toolbox()
toolbox.register("attr_item", random.choice, items.keys())

toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, n=30) #@UndefinedVariable
toolbox.register("population", tools.initRepeat, list, toolbox.individual) 



def evalKnapsack(individual):
    weight = 0.0
    value = 0.0
    for item in individual:
        weight += items[item][0]
        value += items[item][1]
    if(len(individual) > MAX_ITEM or weight > MAX_WEIGHT):
        return 1000,0
    return weight,value

def cxSet(ind1, ind2):
    """Apply a crossover operation on input sets. The first child is the
    intersection of the two sets, the second child is the difference of the
    two sets.
    """
    temp = set(ind1)                # Used in order to keep type
    ind1 &= ind2                    # Intersection (inplace)
    ind2 ^= temp                    # Symmetric Difference (inplace)
    
def mutSet(individual):
    """Mutation that pops or add an element."""
    if random.random() < 0.5:
        if len(individual) > 0:     # Can't pop from an empty set
            individual.pop()
    else:
        individual.add(random.choice(items.keys()))

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selSPEA2)

logging.info("Items to choose for knapsack are: %s\n", items)
for _ in range(4):
    logging.info("Number of steps in evolution: %s\n\n", NGEN)
    for _ in range(3):
        pop = toolbox.population(n=30)
        hof = tools.ParetoFront()
        
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("Avg", tools.mean)
        stats.register("Std", tools.std)
        stats.register("Min", min)
        stats.register("Max", max)
        
        
        algorithms.eaMuPlusLambda(toolbox, pop, MU, LAMBDA, 0.7, 0.2, NGEN, stats, halloffame=hof)
        
        logging.info("Best individual is %s, %s", 
                        (lambda x: sorted(list(x)))(hof[-1]), hof[-1].fitness.values)
    NGEN+=30



