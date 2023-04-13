"""
This function defines the fitness function to be used for evaluating the individuals.
"""

from structure.individual import Individual


def fitness_function1(individual: Individual):
    candidate = individual.candidate
    return candidate[0] + candidate[1]


def fitness_function2(individual: Individual):
    candidate = individual.candidate
    return candidate[2] + candidate[3] + candidate[4]


fitness_functions = [fitness_function1, fitness_function2]