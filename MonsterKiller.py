from Maze import Maze
from Player import Player
from Constants import *
import pygame
import random
import statistics

POPULATION_SIZE = 10
NUMBER_OF_GENERATIONS = 10000
TOURNAMENT_SIZE = 10
CROSSOVER_RATE = 10
DIVERSITY_THRESHOLD = 10
MUTATION_RATE = 10

class MonsterKiller:

    def __init__(self, maze, player):
        self.monster = None
        self.maze = maze
        self.player = player

    def generate_individual(self):
        return [random.randint(-1000, 1000) for _ in range(NUM_ATTRIBUTES)]

    def calculate_fitness(self, attributes):
        self.player.set_attributes(attributes)
        #monster = (self.maze.make_perception_list(self.player, self._display_surf))[3][0]
        rounds_won, success_value = self.monster.mock_fight(self.player)

        fitness = 0

        # Primary component: Emphasize winning rounds
        if rounds_won == 4:
            fitness += 10  # Large reward for winning all rounds

        # Secondary component: Use success value for further differentiation
        fitness += success_value

        # Penalty for not winning all rounds
        if rounds_won == 3:
            fitness -= 1  # Penalize for each round lost
        elif rounds_won == 2:
            fitness -= 8
        elif rounds_won == 1:
            fitness -= 32

        elif rounds_won == 0:
            fitness -= 128

        return fitness

    def tournament_selection(self, population):
        tournament = random.sample(population, TOURNAMENT_SIZE)
        return max(tournament, key=lambda attributes: self.calculate_fitness(attributes))

    def crossover(self, parent1, parent2):
        if random.random() < CROSSOVER_RATE:
            crossover_point = random.randint(1, NUM_ATTRIBUTES - 1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            return child1, child2
        else:
            return parent1, parent2

    def mutate(self, individual):
        for i in range(NUM_ATTRIBUTES):
            if random.random() < MUTATION_RATE:
                individual[i] = random.randint(-1000, 1000)
        return individual

    def measure_diversity(self, population):
        diversity = []
        for attr_index in range(NUM_ATTRIBUTES):
            attr_values = [individual[attr_index] for individual in population]
            diversity.append(statistics.stdev(attr_values))
        return diversity

    def genetic_algorithm(self, monster):
        self.monster = monster
        population = [self.generate_individual() for _ in range(POPULATION_SIZE)]

        for generation in range(NUMBER_OF_GENERATIONS):
            fitness_scores = [self.calculate_fitness(individual) for individual in population]

            # Check diversity
            diversity = self.measure_diversity(population)
            if all(d < DIVERSITY_THRESHOLD for d in diversity):
                new_individuals = [self.generate_individual() for _ in range(POPULATION_SIZE // 10)]
                population.extend(new_individuals)

            # Check if any individual exceeds the fitness threshold
            for i, score in enumerate(fitness_scores):
                if score >= 10:
                    print(f"Optimal individual found in generation {generation} with fitness score: {score}")
                    return population[i]

            population = [x for _, x in sorted(zip(fitness_scores, population), reverse=True)]

            next_generation = population[:int(0.1 * POPULATION_SIZE)]  # 10% Elitism

            while len(next_generation) < POPULATION_SIZE:
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)

                child1, child2 = self.crossover(parent1, parent2)

                child1 = self.mutate(child1)
                child2 = self.mutate(child2)

                next_generation.extend([child1, child2])

            population = next_generation

            # Optional: Print best fitness in each generation
            print(f"Generation {generation}, Best Fitness: {self.calculate_fitness(population[0])}")

        # If no individual reaches the threshold, return the best found
        return population[0]