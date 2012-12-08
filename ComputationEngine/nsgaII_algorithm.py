from deap import benchmarks, algorithms, base, creator, tools
import random
import sys

'''
Created on 06-06-2012

@author: pita
'''

N=100
GEN=200
U=0
V=1

def my_rand():
    return random.random()*(V-U) - (V+U)/2

def main(pop_n = None, problem="zdt2",configuration = None):
    if pop_n:
        N =pop_n
    print pop_n, N, problem
    f_problem = getattr(benchmarks, problem)
    toolbox = base.Toolbox()
    try:
        for command in configuration.split('\n'):
            if command:
                print "executing: ", command
                eval(command)
    except SyntaxError as e:
        print "Syntax error", e.filename, e.offset, e.lineno, e.text
        return []
    except NameError as e:
        print "Name error", e.message
        return []
    except:
        print "Unexpected error in evaluating configuration:", sys.exc_info()[0]
        print configuration
        return []

    toolbox.register("evaluate", f_problem)

    # init population
    pop = toolbox.population(n=N)
    for ind in pop:
        ind.fitness.values = toolbox.evaluate(ind)

    # sort using non domination sort (k is the same as n of population - only sort is applied)
    pop = toolbox.select(pop, k=N)

    for _ in xrange(GEN):
        #select parent pool with tournament dominated selection
        parent_pool = toolbox.selectTournament(pop, k=N)
        offspring_pool = map(toolbox.clone, parent_pool)

        # Apply crossover and mutation on the offspring
        for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
            if random.random() < 0.9:
                toolbox.mate(child1, child2)
        for mutant in offspring_pool:
            if random.random() < 0.1:
                toolbox.mutate(mutant)

        # evaluate offsprings
        for ind in offspring_pool:
            ind.fitness.values = toolbox.evaluate(ind)

        # extend base population with offsprings, pop is now 2N size
        pop.extend(offspring_pool)

        # sort and select new population
        pop = toolbox.select(pop, k=N)

    first_front = tools.sortFastND(pop, k=N)[0]
    front_ = [(ind.fitness.values[0], ind.fitness.values[1]) for ind in first_front]
    return sorted(front_,key=lambda x:x[0])

if __name__ == '__main__':
    main()
