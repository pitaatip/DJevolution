pop_n = 80
pop_bar_n = 40
n_gen = 100
creator.create("FitnessMax", base.Fitness, weights=(-1.0, -1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)
toolbox.register("attr_float", my_rand)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=20)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxSimulatedBinaryBounded, eta=0.5, low=U, up=V)
toolbox.register("mutate", tools.mutPolynomialBounded, eta=0.5, low=U, up=V, indpb=1)
toolbox.register("select", tools.selSPEA2)
toolbox.register("selectTournament", tools.selTournament, tournsize=2)
