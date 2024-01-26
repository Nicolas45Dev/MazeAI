import pygame
import random
from Constants import *
from Monster import *
from Maze import *
from Player import Player
from Individu import Individu

KILL_LIMIT = 4


class KillMonster:
    def __init__(self, pop_size=2, mutation_rate=0.01, generations=10, crossover_rate=0.8, elite_ratio=0.1):
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.maxKill = KILL_LIMIT
        self.bestKill = 0
        self.bestFitness = 0
        self.current_gen = 0
        self.elite_ratio = elite_ratio
        self.bestIndividual = []
        self.population = []
        self.monster = None
        self.scores = []
        self.kill = []
        self.Player = Player()

    def __init__(self, pop_size=2, mutation_rate=0.01, generations=10, crossover_rate=0.8, elite_ratio=0.1, maze=None):
        self.population_size = pop_size
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        self.generations = generations
        self.maxKill = KILL_LIMIT
        self.bestKill = 0
        self.bestFitness = 0
        self.current_gen = 0
        self.elite_ratio = elite_ratio
        self.bestIndividual = []
        self.population = []
        self.monster = None
        self.maze = maze
        self.kill = []
        self.scores = []
        self.Player = Player()

    # Générer une population initiale
    def generate_population(self, size):
        for _ in range(size):
            gnome = Individu.create_gnome()
            self.population.append(Individu(gnome, self.monster, self.Player))

    # Sélectionner un monstre
    def setMonster(self, monster):
        self.monster = monster


    def genetic_algorithm(self):
        self.generate_population(self.population_size)
        scores = []
        while 1:
            # Sort the best individuals
            self.population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
            for i in range(self.population_size):
                scores.append(self.population[i].scores)

            self.bestKill = max(scores, key=float)

            if self.population[0].scores >= 4:
                return self.population[0].get_decoded_chromosome(self.population[0].chromosome)

            new_generation = []

            boomer_index = int((10 * self.population_size) / 100)
            new_generation.extend(self.population[:boomer_index])

            xoomer_index = int((90 * self.population_size) / 100)
            for _ in range(xoomer_index):
                parent1 = random.choice(self.population[:50])
                parent2 = random.choice(self.population[:50])
                child = parent1.mate(parent2)
                new_generation.append(child)

            self.population = new_generation
            self.generations += 1
            scores = []

