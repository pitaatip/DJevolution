__author__ = 'pita'

from deap import benchmarks

for foo_k in benchmarks.__dict__:
    w = globals()
    w[foo_k] = benchmarks.__dict__[foo_k]

def three_obj(individual):
    return individual[0], individual[0] ** 2, (individual[0] - 2) ** 2