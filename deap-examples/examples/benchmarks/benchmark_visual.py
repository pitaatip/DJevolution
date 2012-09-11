'''
Created on Apr 10, 2012

@author: wysek

    Usage:
        python benchmark_visual.py [--sleep x --min y --max z --function f --images]
        functions:
            1 - Rosenbrock
            2 - Rastrigin
            3 - Himmelblau
        default values:
        sleep 0.5
        min -2
        max 2
        function 2
'''

import random
import time

from ROOT import gROOT, TCanvas, TF2,  TPolyMarker3D #@UnresolvedImport
from deap import base, creator, tools
from math import cos,pi
from optparse import OptionParser

#LOW_LIMIT = -2
#HIGH_LIMIT = 2

## CLASSES ##

class Function(object):
    def __init__(self, func):
        self.func = func
    def __str__(self):
        if self.func == 1:
            return '(1-x)^2 + 100*(y-x^2)^2'
        elif self.func == 2:
            return '10 + (x^2 - 10 * cos(2*pi*x)) + (y^2 - 10 * cos(2*pi*y))'
        elif self.func == 3:
            return '(x**2+y-11)**2 + (x+y**2-7)**2'

    def eval(self, individual):
#        #print eval(self.func, individual[0], individual[1])
        return eval(self.func, individual[0], individual[1]),

##############
## FUNCTIONS ##   

def eval(func, x, y):
    if func == 1:
        return (1-x)**2 + 100*(y-x**2)**2
    elif func == 2:
        return 10 + (x**2 - 10 * cos(2*pi*x)) + (y**2 - 10 * cos(2*pi*y))
    elif func == 3:
        return (x**2+y-11)**2 + (x+y**2-7)**2

def draw(func, population, low, high, sleep_time, screens, gen=-1):
    if gen < 0:
        gROOT.Reset()
        func.c1 = TCanvas('c1', 'EvoBenchmark', 200, 10, 1000, 600)
        func.c1.SetGridx()
        func.c1.SetGridy() #mark =  TPolyMarker3D(1, [0,0,0], 2)
    func.fun1 = TF2('fun1', str(func), low, high, low, high)
    func.fun1.Draw("SURF1 p")
    func.mark = TPolyMarker3D(len(population), 2)
    func.mark.SetMarkerSize(1.3)
    func.mark.SetMarkerColor(46)
    for coordinates in population:
        func.mark.SetPoint(population.index(coordinates), coordinates[0], coordinates[1], func.eval(coordinates)[0])
    func.mark.Draw() #fun1.Draw('CONT1 SAME p')
    func.c1.Update()
    #raw_input()
    if screens:
        func.c1.SaveAs("graph" + str(gen) + ".png")
    time.sleep(sleep_time)
    
def main():

    parser = OptionParser()
    parser.add_option("", "--sleep", action="store", type="int", dest="sleep")
    parser.add_option("", "--max", action="store", type="int", dest="max")
    parser.add_option("", "--min", action="store", type="int", dest="min")
    parser.add_option("-f", "--function", action="store", type="int", dest="function")
    parser.add_option("-s", "--images", action="store_true", dest="screens")

    options, args = parser.parse_args()

    if options.function:
        func = Function(options.function)
    else:
        func = Function(2)
        
    if options.min:
        low_limit = options.min
    else:
        if options.min == 0:
            low_limit = 0
        else:
            low_limit = -2
    
    if options.max:
        high_limit = options.max
    else:
        high_limit = 2
        
    if options.sleep:
        sleep_time = options.sleep
    else:
        sleep_time = 0.5

    if options.screens:
        screens = options.screens
    else:
        screens = False

      
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin) #@UndefinedVariable
    
    dimensons=2
    ind_number=500
    
    toolbox = base.Toolbox()
    toolbox.register("attr_float", random.uniform, a=low_limit, b=high_limit)
    toolbox.register("individual", tools.initRepeat, creator.Individual, #@UndefinedVariable
                     toolbox.attr_float, n=dimensons)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    
    toolbox.register("evaluate", func.eval)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.3)
    toolbox.register("mate", tools.cxTwoPoints)
    toolbox.register("select", tools.selTournament, tournsize=5)
    
    random.seed(time.time())
    
    population = toolbox.population(n=ind_number)
    
    CXPB, MUTPB, NGEN = 0.7, 0.2, 20

    draw(func, population, low_limit, high_limit, sleep_time, screens)


    print "Start of Evolution"
    
    # Evaluate the entire population
    fitnesses = map(toolbox.evaluate, population)
    for ind, fit in zip(population, fitnesses):
        ind.fitness.values = fit
        
    print "  Evaluated %i individuals" % len(population)

    for generation in range(NGEN):
        #print "-- Generation %i --" % generation
        
        # Select the next generation individuals
        offsprings = toolbox.select(population, len(population))
        # Clone the selected individuals
        offsprings = map(toolbox.clone, offsprings)
        
        random.seed(time.time())
    
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
        population[:] = toolbox.select(population + offsprings, ind_number)
        
        # Gather all the fitnesses in one list and #print the stats
        fits = [ind.fitness.values[0] for ind in population]
        
        length = len(population)
        mean = sum(fits) / length
        sum2 = sum(x * x for x in fits)
        std = abs(sum2 / length - mean ** 2) ** 0.5
        
        #print "  Min %s" % min(fits)
        #print "  Max %s" % max(fits)
        #print "  Avg %s" % mean
        #print "  Std %s" % std
        
        draw(func, population, low_limit, high_limit, sleep_time, screens, generation)
    
    print "-- End of (successful) evolution --"
    
    best_ind = tools.selBest(population, 1)[0]
    print "Best individual is %s, %s" % (best_ind, best_ind.fitness.values)
    raw_input()
#    return best_ind    
##############    
    
if __name__ == '__main__':
    main()
