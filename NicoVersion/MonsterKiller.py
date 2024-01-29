import pygame
import random
import Maze
from Player import Player
from Constants import *

POPULATION_SIZE = 300
CROSSOVER_RATE = 0.90
MUTATION_RATE = 0.1
ELITE_RATIO = 0.1
GENERATION_RESTART = 1000

class Individu:
    def __init__(self, attributes):
        self.attributes = attributes
        self.fitness = -100
        self.kill = 0

class MonsterKiller:

    def __init__(self, maze):
        self.monster = None
        self.maze = maze
        self.player = Player()
        self.population_size = POPULATION_SIZE
        self.crossover_rate = CROSSOVER_RATE
        self.mutation_rate = MUTATION_RATE
        self.population = None
        self.generation = 1
        self.restart = 0

    def generate_individual(self):
        attributes = [random.randint(-1000, 1000) for _ in range(NUM_ATTRIBUTES)]
        return Individu(attributes)

    def evaluate_population(self):
        for i in range(POPULATION_SIZE - 1):
            individual = self.population[i]
            self.player.set_attributes(individual.attributes)
            individual.kill, individual.fitness = self.monster.mock_fight(self.player)

    def crossover(self, p1, p2):
        if random.random() < CROSSOVER_RATE:
            crossover_point = random.randint(0, NUM_ATTRIBUTES - 1)
            c1 = p1.attributes[:crossover_point] + p2.attributes[crossover_point:]
            c2 = p2.attributes[:crossover_point] + p1.attributes[crossover_point:]

            return Individu(c1), Individu(c2)
        return p1, p2

    def mutate(self, individual):
        if random.random() < MUTATION_RATE:
            index = random.randint(0, NUM_ATTRIBUTES - 1)
            individual.attributes[index] = random.randint(-1000, 1000)

    def genetic_algorithm(self, monster):
        self.monster = monster
        self.population = [self.generate_individual() for _ in range(POPULATION_SIZE)]

        while True:
            self.evaluate_population()

            # Sort population from best to worst
            self.population.sort(key=lambda x: x.fitness, reverse=True)

            # Check if one is good enough
            bestIndividu = self.population[0]

            if bestIndividu.kill >= 4:
                print(f"********** The best has been found **********")
                print(f"Crossover rate : {self.crossover_rate}")
                print(f"Mutation rate : {self.mutation_rate}")
                print('Best attributes : ', bestIndividu.attributes)
                print('Best fitness : ', bestIndividu.fitness)
                print('Best kill : ', bestIndividu.kill)
                return bestIndividu.attributes
            elif self.generation % 50 == 0 :
                print(f"********** Generation {self.generation} **********")
                print(f"Crossover rate : {self.crossover_rate}")
                print(f"Mutation rate : {self.mutation_rate}")
                print(f"Best attributes : {bestIndividu.attributes}")
                print(f"Best fitness : {bestIndividu.fitness}")
                print(f"Best kill : {bestIndividu.kill}")

            if self.generation >= GENERATION_RESTART:
                self.population = [self.generate_individual() for _ in range(POPULATION_SIZE)]
                self.generation = 1
                self.restart += 1

                if self.restart % 2 == 0:
                    self.mutation_rate += 0.01
                else:
                    self.crossover_rate += 0.01

            else:

                # Get the best from the population
                new_generation = []
                new_generation.extend(self.population[:int(ELITE_RATIO * POPULATION_SIZE) - 1])

                while len(new_generation) < POPULATION_SIZE:
                    [parent1, parent2] = random.choices(self.population, k=2)

                    child1, child2 = self.crossover(parent1, parent2)

                    self.mutate(child1)
                    self.mutate(child2)

                    new_generation.extend([child1, child2])

                self.population = new_generation
                self.generation += 1

        # If no individual reaches the threshold, return the best found
        return self.population[0]
