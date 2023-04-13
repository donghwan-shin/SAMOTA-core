from problem.individual import Individual
from problem.fitness import fitness_functions
from problem.operators import generate_offspring, select


def initialize_population(pop_size: int):
    population = []
    for i in range(pop_size):
        population.append(Individual())
    return population


def evaluate_population(population: list):
    for individual in population:
        individual.fitness = [fitness_function(individual) for fitness_function in fitness_functions]


def update_archive(population: list, archives: list, thresholds: list, is_covered_obj: list):
    # check if the current population covers any of the objectives and update the archive
    for individual in population:
        for obj_index in range(len(is_covered_obj)):
            if individual.fitness[obj_index] >= thresholds[obj_index]:
                is_covered_obj[obj_index] = True
                archives.append(individual)

    # remove the dominated individuals from the archive
    archives = [individual for individual in archives
                if all(other_individual.fitness[i] >= individual.fitness[i]
                       for other_individual in archives
                       for i in range(len(is_covered_obj)))]

    return archives, is_covered_obj


def update_database(evaluated_individuals: list, database: list):
    # add the current population to the database
    database.extend(evaluated_individuals)
    return database


def train_global_surrogate_model(database: list, obj_index: int):
    # train the (ensemble) surrogate model using the database for the given objective;
    # TODO
    return None


def train_global_surrogate_models(database: list, is_covered_obj: list):
    # train the surrogate models for the uncovered objectives
    g_surrogate_models = []
    for obj_index in range(len(is_covered_obj)):
        if not is_covered_obj[obj_index]:
            # train the surrogate model using the database for the uncovered objective
            g_surrogate_models.append(train_global_surrogate_model(database, obj_index))
    return g_surrogate_models


def evaluate_population_using_g_surrogate_models(population: list, g_surrogate_models: list):
    for individual in population:
        for surrogate_model in g_surrogate_models:  # one (ensemble) surrogate model per objective
            predicted_fitness, uncertainty = surrogate_model.predict(individual.candidate)
            individual.predicted_fitness.append(predicted_fitness)
            individual.uncertainty.append(uncertainty)


def global_search(database: list, is_covered_obj: list, g_search_max: int, pop_size: int, thresholds: list):
    g_surrogate_models = train_global_surrogate_models(database, is_covered_obj)
    best_predicted = [Individual() for _ in range(len(is_covered_obj))]  # keep track of the best candidate for each uncovered objective
    most_uncertain = [Individual() for _ in range(len(is_covered_obj))]  # keep track of the most uncertain candidate for each uncovered objective
    curr_population = initialize_population(pop_size)
    counter = 0
    while counter < g_search_max:
        new_population = generate_offspring(curr_population, mutation_prob=0.1, crossover_prob=0.8)
        evaluate_population_using_g_surrogate_models(curr_population + new_population, g_surrogate_models)
        for obj_index in range(len(is_covered_obj)):
            if not is_covered_obj[obj_index]:
                # select the best-predicted candidate
                best_predicted[obj_index] = max(curr_population + new_population + [best_predicted[obj_index]],
                                                key=lambda individual: individual.predicted_fitness[obj_index])

                # select the most uncertain candidate
                most_uncertain[obj_index] = max(curr_population + new_population + [most_uncertain[obj_index]],
                                                key=lambda individual: individual.uncertainty[obj_index])

                # update the is_covered_obj list
                if best_predicted[obj_index].predicted_fitness[obj_index] >= thresholds[obj_index]:
                    is_covered_obj[obj_index] = True

        # select the next population
        curr_population = select(curr_population + new_population)

        # go to the next iteration
        counter += 1
    return best_predicted + most_uncertain


def generate_clusters(database: list, min_cluster_size: int, l_search_ratio: float, obj_index: int):
    # generate clusters using the top `l_search_ratio` of the database
    clusters = []
    # TODO
    return clusters


def train_local_surrogate_model(cluster: list, obj_index: int):
    # train the (ensemble) surrogate model using the cluster for the given objective;
    # TODO
    return None


def evaluate_population_using_l_surrogate_model(population: list, l_surrogate_model, obj_index: int):
    for individual in population:
        individual.predicted_fitness[obj_index] = l_surrogate_model.predict(individual.candidate)


def local_search(database: list, is_covered_obj: list, l_search_max: int, l_search_ratio: float, min_cluster_size: int):
    best_predicted = [Individual() for _ in range(len(is_covered_obj))]  # keep track of the best candidate for each uncovered objective

    for obj_index in range(len(is_covered_obj)):
        if not is_covered_obj[obj_index]:

            # generate clusters using the top `l_search_ratio` of the database
            clusters = generate_clusters(database, min_cluster_size, l_search_ratio, obj_index)

            for cluster in clusters:
                l_surrogate_model = train_local_surrogate_model(cluster, obj_index)
                curr_population = cluster
                counter = 0
                while counter < l_search_max:
                    new_population = generate_offspring(curr_population, mutation_prob=0.1, crossover_prob=0.8)
                    evaluate_population_using_l_surrogate_model(curr_population + new_population, l_surrogate_model, obj_index)
                    best_predicted[obj_index] = max(curr_population + new_population + [best_predicted[obj_index]],
                                                    key=lambda individual: individual.predicted_fitness[obj_index])
                    curr_population = select(curr_population + new_population)
                    counter += 1

    return best_predicted


def samota(
        objectives: list,
        pop_size: int,
        thresholds: list,
        g_search_max: int,
        l_search_max: int,
        l_search_ratio: float = 0.2,
        min_cluster_size: int = 5
):
    # initialization
    archives = []
    is_covered_obj = [False for _ in range(len(objectives))]
    curr_population = initialize_population(pop_size)
    evaluate_population(curr_population)
    archives, is_covered_obj = update_archive(curr_population, archives, thresholds, is_covered_obj)
    database = update_database(curr_population, [])

    # main loop
    while not all(is_covered_obj):
        # global search
        g_candidates = global_search(database, is_covered_obj, g_search_max, pop_size, thresholds)
        evaluate_population(g_candidates)
        archives, is_covered_obj = update_archive(g_candidates, archives, thresholds, is_covered_obj)
        database = update_database(g_candidates, database)

        # local search
        l_candidates = local_search(database, is_covered_obj, l_search_max, l_search_ratio, min_cluster_size)
        evaluate_population(l_candidates)
        archives, is_covered_obj = update_archive(l_candidates, archives, thresholds, is_covered_obj)
        database = update_database(l_candidates, database)

    return archives, database
