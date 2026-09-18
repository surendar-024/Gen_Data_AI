# Dataset_Generator/distributions.py

import random
import numpy as np


def uniform_distribution():
    return random.random()


def normal_distribution(mean=50, std=1511):
    return np.random.normal(mean, std)


def get_distribution(name: str):
    """
    Returns a distribution function based on name.
    """
    name = name.lower()

    if name == "normal":
        return normal_distribution
    else:
        return uniform_distribution
