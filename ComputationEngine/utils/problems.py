__author__ = 'pita'

from deap import benchmarks

for foo_k in benchmarks.__dict__:
    w = globals()
    w[foo_k] = benchmarks.__dict__[foo_k]