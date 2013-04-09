__author__ = 'wysek'

from mpi4py import MPI
from itertools import chain


def divide_list(lst, n):
    return [lst[i::n] for i in xrange(n)]


def chain_list(lst):
    return list(chain.from_iterable(lst))


def evaluate_individuals_in_groups(func, rank, individuals):
    comm = MPI.COMM_WORLD
    size = MPI.COMM_WORLD.Get_size()

    packages = None
    if not rank:
        packages = divide_list(individuals, size)

    ind_for_eval = comm.scatter(packages)
    eval_population(func, ind_for_eval)

    pop_with_fit = comm.gather(ind_for_eval)

    if not rank:
        pop_with_fit = chain_list(pop_with_fit)
        for index, elem in enumerate(pop_with_fit):
            individuals[index] = elem


def eval_population(func, pop):
    for ind in pop:
        ind.fitness.values = func(ind)


class Node(object):
    SEND = "send"
    RECV = "recv"

    def __init__(self):
        self.comm = MPI.COMM_WORLD
        self.rank = self.comm.Get_rank()
        self.size = self.comm.Get_size()

    def last_node(self):
        return self.size - 1

    def next(self):
        if self.rank != self.last_node():
            return self.rank + 1
        else:
            return 0

    def prev(self):
        if self.rank:
            return self.rank - 1
        else:
            return self.last_node()

    def pair(self, my_task):
        if my_task == self.SEND:
            return self.rank * 10 + self.next()
        else:
            return self.prev() * 10 + self.rank

    def send(self, msg):
        self.comm.send(msg, dest=self.next(), tag=self.pair(self.SEND))

    def recv(self):
        msg = self.comm.recv(source=self.prev(), tag=self.pair(self.RECV))
        return msg


def migRingMPI(deme, k, node, selection, rank, replacement=None):
    """Migration using MPI between initialized processes. It first selects
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

    # This if statement is present because of synchronous P2P communication
    if not rank % 2:
        node.send(emigrants)
        buf = node.recv()
    else:
        buf = node.recv()
        node.send(emigrants)

    for place, immigrant in zip(immigrants, buf):
        indx = deme.index(place)
        deme[indx] = immigrant


def migRingPipe(deme, k, pipein, pipeout, selection, replacement=None):
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