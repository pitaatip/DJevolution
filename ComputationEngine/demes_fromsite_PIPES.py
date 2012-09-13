#    This file is part of DEAP.
#
#    DEAP is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as
#    published by the Free Software Foundation, either version 3 of
#    the License, or (at your option) any later version.
#
#    DEAP is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with DEAP. If not, see <http://www.gnu.org/licenses/>.

import array
from collections import deque
from multiprocessing import Event, Pipe, Process
import random
import sys

if sys.version_info < (2, 7):
    print "ga_onemax_island example requires Python >= 2.7."
    exit(1)

from deap import algorithms, benchmarks
from deap import base
from deap import creator
from deap import tools
from datetime import datetime

L = 32
U = -4.0
V = 4.0
DIM = 20

def rastrigin_arg0(sol):
    return benchmarks.rastrigin(convertArrToFloat(sol))

def binListToInt(l):
    w=''
    for a in l:
        w=''.join([w,str(a)])
    return int(w,2)

def sliceIntGen(arr,slice_n):
    for i in xrange(0,len(arr)-slice_n,slice_n):
        yield binListToInt(arr[i:i+slice_n].tolist())

def convertArrToFloat(arr):
    x=[]
    for a in sliceIntGen(arr,L):
        x.append(U + (float(a) / (2**float(L) -1.0) )*(V - U))
    return x


creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax) #@UndefinedVariable

toolbox = base.Toolbox()

# Attribute generator
toolbox.register("attr_bool", random.randint, 0, 1)

# Structure initializers
toolbox.register("individual", tools.initRepeat, creator.Individual, #@UndefinedVariable
    toolbox.attr_bool, DIM*L)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalOneMax(individual):
    return sum(individual),

def migPipe(deme, k, pipein, pipeout, selection, replacement=None):
    """Migration using pipes between initialized processes. It first selects
    *k* individuals from the *deme* and writes them in *pipeout*. Then it
    reads the individuals from *pipein* and replace some individuals in the
    deme. The replacement strategy shall not select twice the same individual.
    
    :param deme: A list of individuals on which to operate migration.
    :param k: The number of individuals to migrate.
    :param pipein: A :class:`~multiprocessing.Pipe` from which to read
                   immigrants.
    :param pipeout: A :class:`~multiprocessing.Pipe` in which to write
                    emigrants. 
    :param selection: The function to use for selecting the emigrants.
    :param replacement: The function to use to select which individuals will
                        be replaced. If :obj:`None` (default) the individuals
                        that leave the population are directly replaced.
    """
    emigrants = selection(deme, k)
    if replacement is None:
        # If no replacement strategy is selected, replace those who migrate
        immigrants = emigrants
    else:
        # Else select those who will be replaced
        immigrants = replacement(deme, k)
    
    pipeout.send(emigrants)
    buf = pipein.recv()
    
    for place, immigrant in zip(immigrants, buf):
        indx = deme.index(place)
        deme[indx] = immigrant

toolbox.register("evaluate", rastrigin_arg0)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.001)
toolbox.register("select", tools.selTournament, tournsize=5)

def main(procid, pipein, pipeout, sync, computation, connection, seed=None):

    a = datetime.now()

    random.seed(seed)
    toolbox.register("migrate", migPipe, k=5, pipein=pipein, pipeout=pipeout,
        selection=tools.selBest, replacement=random.sample)

    MU = 100
    NGEN = 100
    CXPB = 0.8
    MUTPB = 1
    MIG_RATE = 5
    
    deme = toolbox.population(n=MU)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", tools.mean)
    stats.register("std", tools.std)
    stats.register("min", min)
    stats.register("max", max)
    
    logger = tools.EvolutionLogger(["gen", "deme", "evals"] + stats.functions.keys())
    if procid == 0:
        # Synchronization needed to log header on top and only once
        logger.logHeader()
        sync.set()
    else:
        sync.wait()
    
    for ind in deme:
        ind.fitness.values = toolbox.evaluate(ind)
    stats.update(deme)
    hof.update(deme)
    logger.logGeneration(gen="0", deme=procid, evals=len(deme), stats=stats)
    
    for gen in range(1, NGEN):
        deme = toolbox.select(deme, len(deme))
        deme = algorithms.varAnd(deme, toolbox, cxpb=CXPB, mutpb=MUTPB)
        
        invalid_ind = [ind for ind in deme if not ind.fitness.valid]
        for ind in invalid_ind:
            ind.fitness.values = toolbox.evaluate(ind)
        
        stats.update(deme)
        hof.update(deme)
        logger.logGeneration(gen="%d" % gen, deme=procid, evals=len(invalid_ind), stats=stats)
            
        if gen % MIG_RATE == 0 and gen > 0:
            toolbox.migrate(deme)

    b = datetime.now()

    c = b - a

    if procid == 0:
        computation['restrigin_val'] = rastrigin_arg0(hof[-1])[0]
        computation['results'] = convertArrToFloat(hof[-1])
        computation['computed'] = True
        computation['computation_time'] = str(c.total_seconds()) + "s."
        connection.save(computation)

#    print "Best individual:  " + str(convertArrToFloat(hof[-1]))
#    print "Rastrigin value: " + str(rastrigin_arg0(hof[-1])[0]) + "\n\n\n"

if __name__ == "__main__":
    random.seed(64)
    
    NBR_DEMES = 3
    
    pipes = [Pipe(False) for _ in range(NBR_DEMES)]
    pipes_in = deque(p[0] for p in pipes)
    pipes_out = deque(p[1] for p in pipes)
    pipes_in.rotate(1)
    pipes_out.rotate(-1)
    
    e = Event()
    
    processes = [Process(target=main, args=(i, ipipe, opipe, e, random.random())) for i, (ipipe, opipe) in enumerate(zip(pipes_in, pipes_out))]
    
    for proc in processes:
        proc.start()
    
    for proc in processes:
        proc.join()

