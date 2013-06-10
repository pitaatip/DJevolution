import random
from time import time

def my_rand(V=1,U=0):
    return random.random()*(V-U) - (V+U)/2

class TimeMeasurer(object):

    def __init__(self, rank):
        self.times = dict()
        self.temp_times = dict()
        self.rank = rank

    def start(self, name):
        if not name in self.times:
            self.times[name] = 0
        self.temp_times[name] = time()

    def stop(self, name):
        self.times[name] += time() - self.temp_times[name]

    def print_times(self):
        for tag, measurement in self.times.iteritems():
            print 'Rank {} {}: {}'.format(self.rank, tag, measurement)