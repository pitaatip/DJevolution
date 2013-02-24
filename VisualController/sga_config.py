self.L = 32
self.U = -4.0
self.V = 4.0
self.DIM = 20
self.POP = 300
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, self.DIM*self.L)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.001)
toolbox.register("select", tools.selTournament, tournsize=5)