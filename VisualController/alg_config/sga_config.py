comp_prop["L"] = 64
comp_prop["U"] = -4.0
comp_prop["V"] = 4.0
comp_prop["DIM"] = 20
comp_prop["POP"] = 300
creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
creator.create("Individual", array.array, typecode='b', fitness=creator.FitnessMax)
toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, comp_prop["DIM"]*comp_prop["L"])
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("mate", tools.cxTwoPoints)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.001)
toolbox.register("select", tools.selTournament, tournsize=5)