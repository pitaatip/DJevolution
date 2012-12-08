from deap import benchmarks, algorithms, base, creator, tools
import random
import sys

'''
Created on 13-11-2012

@author: wysek
'''

N = 80
Nbar = 40
GEN = 100
U = 0
V = 1

def my_rand():
    return random.random() * (V - U) - (V + U) / 2

def main(pop_n=None,problem="zdt3",configuration = None):
    if pop_n:
        N = pop_n
        Nbar = pop_n

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

    # Step 1 Initialization
    pop = toolbox.population(n=N)
    archive = []
    curr_gen = 1

    while True:
        # Step 2 Fitness assignement
        for ind in pop:
            ind.fitness.values = toolbox.evaluate(ind)

        for ind in archive:
            ind.fitness.values = toolbox.evaluate(ind)

        # Step 3 Environmental selection
        archive  = toolbox.select(pop + archive, k=Nbar)

        # Step 4 Termination
        if curr_gen >= GEN:
            final_set = archive
            break

        # Step 5 Mating Selection
        mating_pool = toolbox.selectTournament(archive, k=N)
        offspring_pool = map(toolbox.clone, mating_pool)

        # Step 6 Variation
        # crossover 100% and mutation 6%
        for child1, child2 in zip(offspring_pool[::2], offspring_pool[1::2]):
            toolbox.mate(child1, child2)

        for mutant in offspring_pool:
            if random.random() < 0.06:
                toolbox.mutate(mutant)

        pop = offspring_pool

        curr_gen += 1

    set_ = [(ind.fitness.values[0], ind.fitness.values[1]) for ind in final_set]
    return sorted(set_,  key=lambda x:x[0])

if __name__ == '__main__':
    main()