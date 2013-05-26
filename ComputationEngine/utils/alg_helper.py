'''
Created on 22-04-2012

@author: pita
'''
from copy import deepcopy
from itertoolsmodule import chain
from operator import attrgetter
from deap import tools
import random
import math
from deap.tools import sortFastND, assignCrowdingDist


def my_rand(V=1,U=0):
    return random.random()*(V-U) - (V+U)/2

def varAnd(population, toolbox, cxpb, mutpb):
    """Part of an evolutionary algorithm applying only the variation part
    (crossover **and** mutation). The modified individuals have their
    fitness invalidated. The individuals are cloned so returned population is
    independent of the input population.
    
    :param population: A list of individuals to variate.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :returns: A list of varied individuals that are independent of their
              parents.
    
    The variator goes as follow. First, the parental population
    :math:`P_\mathrm{p}` is duplicated using the :meth:`toolbox.clone` method
    and the result is put into the offspring population :math:`P_\mathrm{o}`.
    A first loop over :math:`P_\mathrm{o}` is executed to mate consecutive
    individuals. According to the crossover probability *cxpb*, the
    individuals :math:`\mathbf{x}_i` and :math:`\mathbf{x}_{i+1}` are mated
    using the :meth:`toolbox.mate` method. The resulting children
    :math:`\mathbf{y}_i` and :math:`\mathbf{y}_{i+1}` replace their respective
    parents in :math:`P_\mathrm{o}`. A second loop over the resulting
    :math:`P_\mathrm{o}` is executed to mutate every individual with a
    probability *mutpb*. When an individual is mutated it replaces its not
    mutated version in :math:`P_\mathrm{o}`. The resulting
    :math:`P_\mathrm{o}` is returned.
    
    This variation is named *And* beceause of its propention to apply both
    crossover and mutation on the individuals. Note that both operators are
    not applied systematicaly, the resulting individuals can be generated from
    crossover only, mutation only, crossover and mutation, and reproduction
    according to the given probabilities. Both probabilities should be in
    :math:`[0, 1]`.
    """
    offspring = [toolbox.clone(ind) for ind in population]
    
    # Apply crossover and mutation on the offspring
    for ind1, ind2 in zip(offspring[::2], offspring[1::2]):
        if random.random() < cxpb:
            toolbox.mate(ind1, ind2)
            del ind1.fitness.values, ind2.fitness.values
    
    for ind in offspring:
        if random.random() < mutpb:
            toolbox.mutate(ind)
            del ind.fitness.values
    
    return offspring

def monitor(hof,monitoring,gen,partial_res):
    if gen % monitoring == 0:
        partial_res.append(hof[0].fitness.values[0])

def eaSimple(population, toolbox, cxpb, mutpb, ngen,monitoring, stats=None,
             halloffame=None, verbose=__debug__):
    """This algorithm reproduce the simplest evolutionary algorithm as
    presented in chapter 7 of [Back2000]_.

    :param population: A list of individuals.
    :param toolbox: A :class:`~deap.base.Toolbox` that contains the evolution
                    operators.
    :param cxpb: The probability of mating two individuals.
    :param mutpb: The probability of mutating an individual.
    :param ngen: The number of generation.
    :param stats: A :class:`~deap.tools.Statistics` object that is updated
                  inplace, optional.
    :param halloffame: A :class:`~deap.tools.HallOfFame` object that will
                       contain the best individuals, optional.
    :param verbose: Whether or not to log the statistics.
    :returns: The final population.

    It uses :math:`\lambda = \kappa = \mu` and goes as follow.
    It first initializes the population (:math:`P(0)`) by evaluating
    every individual presenting an invalid fitness. Then, it enters the
    evolution loop that begins by the selection of the :math:`P(g+1)`
    population. Then the crossover operator is applied on a proportion of
    :math:`P(g+1)` according to the *cxpb* probability, the resulting and the
    untouched individuals are placed in :math:`P'(g+1)`. Thereafter, a
    proportion of :math:`P'(g+1)`, determined by *mutpb*, is
    mutated and placed in :math:`P''(g+1)`, the untouched individuals are
    transferred :math:`P''(g+1)`. Finally, those new individuals are evaluated
    and the evolution loop continues until *ngen* generations are completed.
    Briefly, the operators are applied in the following order ::

        evaluate(population)
        for i in range(ngen):
            offspring = select(population)
            offspring = mate(offspring)
            offspring = mutate(offspring)
            evaluate(offspring)
            population = offspring

    This function expects :meth:`toolbox.mate`, :meth:`toolbox.mutate`,
    :meth:`toolbox.select` and :meth:`toolbox.evaluate` aliases to be
    registered in the toolbox.

    .. [Back2000] Back, Fogel and Michalewicz, "Evolutionary Computation 1 :
       Basic Algorithms and Operators", 2000.
    """
    # Evaluate the individuals with an invalid fitness
    invalid_ind = [ind for ind in population if not ind.fitness.valid]
    fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
    for ind, fit in zip(invalid_ind, fitnesses):
        ind.fitness.values = fit

    if halloffame is not None:
        halloffame.update(population)
    if stats is not None:
        stats.update(population)
    if verbose:
        column_names = ["gen", "evals"]
        if stats is not None:
            column_names += stats.functions.keys()
        logger = tools.EvolutionLogger(column_names)
        logger.logHeader()
        logger.logGeneration(evals=len(population), gen=0, stats=stats)
    partial_res = []
    # Begin the generational process
    for gen in range(1, ngen+1):
        # Select the next generation individuals
        offspring = toolbox.select(population, len(population))

        # Variate the pool of individuals
        offspring = varAnd(offspring, toolbox, cxpb, mutpb)

        # Evaluate the individuals with an invalid fitness
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = toolbox.map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        # Update the hall of fame with the generated individuals
        if halloffame is not None:
            halloffame.update(offspring)

        # monitor partial results
        monitor(halloffame,monitoring,gen,partial_res)

        # Replace the current population by the offspring
        population[:] = offspring

        # Update the statistics with the new population
        if stats is not None:
            stats.update(population)

        if verbose:
            logger.logGeneration(evals=len(invalid_ind), gen=gen, stats=stats)

    return population, partial_res



def selSPEA2(individuals, k):
    """Apply SPEA-II selection operator on the *individuals*. Usually, the
    size of *individuals* will be larger than *n* because any individual
    present in *individuals* will appear in the returned list at most once.
    Having the size of *individuals* equals to *n* will have no effect other
    than sorting the population according to a strength Pareto scheme. The
    list returned contains references to the input *individuals*. For more
    details on the SPEA-II operator see [Zitzler2001]_.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list of selected individuals.

    .. [Zitzler2001] Zitzler, Laumanns and Thiele, "SPEA 2: Improving the
       strength Pareto evolutionary algorithm", 2001.
    """
    N = len(individuals)
    L = len(individuals[0].fitness.values)
    K = math.sqrt(N)
    strength_fits = [0] * N
    fits = [0] * N
    dominating_inds = [list() for i in xrange(N)]

    for i in xrange(N):
        for j in xrange(i + 1, N):
            if tools.isDominated(individuals[i].fitness.wvalues, individuals[j].fitness.wvalues):
                strength_fits[j] += 1
                dominating_inds[i].append(j)
            elif tools.isDominated(individuals[j].fitness.wvalues, individuals[i].fitness.wvalues):
                strength_fits[i] += 1
                dominating_inds[j].append(i)

    for i in xrange(N):
        for j in dominating_inds[i]:
            fits[i] += strength_fits[j]

    # Choose all non-dominated individuals
    chosen_indices = [i for i in xrange(N) if fits[i] < 1]

    if len(chosen_indices) < k:     # The archive is too small
        for i in xrange(N):
            distances = [0.0] * N
            for j in xrange(i + 1, N):
                dist = 0.0
                for l in xrange(L):
                    val = individuals[i].fitness.values[l] -\
                          individuals[j].fitness.values[l]
                    dist += val * val
                distances[j] = dist
            kth_dist = tools._randomizedSelect(distances, 0, N - 1, K)
            density = 1.0 / (kth_dist + 2.0)
            fits[i] += density

        next_indices = [(fits[i], i) for i in xrange(N)\
                                     if not i in chosen_indices]
        next_indices.sort()
        #print next_indices
        chosen_indices += [i for _, i in next_indices[:k - len(chosen_indices)]]

    elif len(chosen_indices) > k:   # The archive is too large
        N = len(chosen_indices)
        distances = [[0.0] * N for i in xrange(N)]
        sorted_indices = [[0] * N for i in xrange(N)]
        for i in xrange(N):
            for j in xrange(i + 1, N):
                dist = 0.0
                for l in xrange(L):
                    val = individuals[chosen_indices[i]].fitness.values[l] -\
                          individuals[chosen_indices[j]].fitness.values[l]
                    dist += val * val
                distances[i][j] = dist
                distances[j][i] = dist
            distances[i][i] = -1

        # Insert sort is faster than quick sort for short arrays
        for i in xrange(N):
            for j in xrange(1, N):
                l = j
                while l > 0 and distances[i][j] < distances[i][sorted_indices[i][l - 1]]:
                    sorted_indices[i][l] = sorted_indices[i][l - 1]
                    l -= 1
                sorted_indices[i][l] = j

        size = N
        to_remove = []
        while size > k:
            # Search for minimal distance
            min_pos = 0
            for i in xrange(1, N):
                for j in xrange(1, size):
                    dist_i_sorted_j = distances[i][sorted_indices[i][j]]
                    dist_min_sorted_j = distances[min_pos][sorted_indices[min_pos][j]]

                    if dist_i_sorted_j < dist_min_sorted_j:
                        min_pos = i
                        break
                    elif dist_i_sorted_j > dist_min_sorted_j:
                        break

            # Remove minimal distance from sorted_indices
            for i in xrange(N):
                distances[i][min_pos] = float("inf")
                distances[min_pos][i] = float("inf")

                for j in xrange(1, size - 1):
                    if sorted_indices[i][j] == min_pos:
                        sorted_indices[i][j] = sorted_indices[i][j + 1]
                        sorted_indices[i][j + 1] = min_pos

            # Remove corresponding individual from chosen_indices
            to_remove.append(min_pos)
            size -= 1

        for index in reversed(sorted(to_remove)):
            del chosen_indices[index]

    return [individuals[i] for i in chosen_indices],[fits[i] for i in chosen_indices]



def selTournament(individuals, k, tournsize, fitness):
    """Select *k* individuals from the input *individuals* using *k*
    tournaments of *tournsize* individuals. The list returned contains
    references to the input *individuals*.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :param tournsize: The number of individuals participating in each tournament.
    :returns: A list of selected individuals.

    This function uses the :func:`~random.choice` function from the python base
    :mod:`random` module.
    """
    chosen = []
    N = len(individuals)
    for i in xrange(k):
        chosen_i = random.randint(0,N-1)
        chosen.append(individuals[chosen_i])
        for j in xrange(tournsize - 1):
            aspirant = random.randint(0,N-1)
#            print len(fitness), aspirant, i
            if fitness[aspirant] > fitness[chosen_i]:
                chosen[i] = individuals[aspirant]

    return chosen

def selNSGA2(individuals, k):
    """Apply NSGA-II selection operator on the *individuals*. Usually, the
    size of *individuals* will be larger than *k* because any individual
    present in *individuals* will appear in the returned list at most once.
    Having the size of *individuals* equals to *k* will have no effect other
    than sorting the population according to a non-domination scheme. The list
    returned contains references to the input *individuals*. For more details
    on the NSGA-II operator see [Deb2002]_.

    :param individuals: A list of individuals to select from.
    :param k: The number of individuals to select.
    :returns: A list of selected individuals.

    .. [Deb2002] Deb, Pratab, Agarwal, and Meyarivan, "A fast elitist
       non-dominated sorting genetic algorithm for multi-objective
       optimization: NSGA-II", 2002.
    """
    pareto_fronts = sortFastND(individuals, k)
    for front in pareto_fronts:
        assignCrowdingDist(front)

    chosen = list(chain(*pareto_fronts[:-1]))
    k = k - len(chosen)
    if k > 0:
        sorted_front = sorted(pareto_fronts[-1], key=attrgetter("fitness.crowding_dist"), reverse=True)
        chosen.extend(sorted_front[:k])

    return chosen, pareto_fronts[0]