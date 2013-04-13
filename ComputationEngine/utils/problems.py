import os

__author__ = 'pita'

from deap import benchmarks

for foo_k in benchmarks.__dict__:
    if not "__" in foo_k:
        w = globals()
        w[foo_k] = benchmarks.__dict__[foo_k]

def three_obj(individual):
    return individual[0], individual[0] ** 2, (individual[0] - 2) ** 2

def logging_zdt1(individual):
    print os.getpid()
    return zdt1(individual)

def uber_three(individual):
    g  = 1 + 10*(len(individual)-1) + sum(xi**2 - 10*cos(4*pi*xi) for xi in individual[1:])
    g2  = 1.0 + 9.0*sum(individual[1:])/(len(individual)-1)
    f1 = individual[0]
    f2 = g * (1 - sqrt(f1/g))
    f3 = g2 * (1 - sqrt(f1/g2))
    return f1,f2,f3
