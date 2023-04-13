"""
This class represents an individual in the population.
The actual encoding of an individual is defined in this class.

As an example, the candidate solution is a list of 5 floats.
"""

import random


class Individual:
    candidate = []
    for i in range(5):
        candidate.append(random.uniform(0, 1))
    fitness = [-1, -1]  # considering two objectives
    predicted_fitness = [-1, -1]  # considering two objectives
    uncertainty = [-1, -1]  # considering two objectives
