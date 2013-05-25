from math import exp, sin, pi, cos
from operator import mul
import os, itertools
import random

__author__ = 'pita'

from deap import benchmarks

def non_optimazeable_fun(individual,a,b):
    g  = 1 + 9 * (sum(individual[1:]) / (len(individual)-1))**a
    f1 = 1 - exp(-4*individual[0]) * sin(6*pi*individual[0])**b
    f2 = g * (1 - (f1/g)**2)
    xc = individual[:1]
    xm = individual[1:]
    g = sum((xi-0.5)**2 for xi in xm)
    f = [(1.0+g) *  reduce(mul, (cos(0.5*xi**a*pi) for xi in xc), 1.0)]
    f.extend((1.0+g) * reduce(mul, (cos(0.5*xi**a*pi) for xi in xc[:m-1]), 1) * sin(0.5*xc[m]**a*pi) for m in reversed(xrange(1)))
    return f1, f2

for foo_k in benchmarks.__dict__:
    if not "__" in foo_k:
        w = globals()
        w[foo_k] = benchmarks.__dict__[foo_k]

def three_obj(individual):
    return individual[0], individual[0] ** 2, (individual[0] - 2) ** 2

def logging_zdt1(individual):
    print os.getpid()
    return zdt1(individual)

def hacked_zdt6(individual):
    for _ in xrange(10):
        non_optimazeable_fun(individual,random.random(),random.randint(1,10))
    res = zdt6(individual)
    return res

def uber_three(individual):
    g  = 1 + 10*(len(individual)-1) + sum(xi**2 - 10*cos(4*pi*xi) for xi in individual[1:])
    g2  = 1.0 + 9.0*sum(individual[1:])/(len(individual)-1)
    f1 = individual[0]
    f2 = g * (1 - sqrt(f1/g))
    f3 = g2 * (1 - sqrt(f1/g2))
    return f1,f2,f3
