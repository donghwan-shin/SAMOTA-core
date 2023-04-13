from problem.individual import Individual
import random


def mutation(individual: Individual):
    # mutate the individual
    return individual


def crossover(individual1: Individual, individual2: Individual):
    # crossover the two individuals
    return individual1, individual2


def select(population: list):
    # randomly select individuals from the population
    return random.sample(population, len(population)//2)


def generate_offspring(population: list, mutation_prob: float, crossover_prob: float):
    offspring = []
    for i in range(len(population)):
        if random.uniform(0, 1) < mutation_prob:
            offspring.append(mutation(population[i]))
        if random.uniform(0, 1) < crossover_prob:
            offspring.append(crossover(population[i], population[(i + 1) % len(population)]))
    return offspring
