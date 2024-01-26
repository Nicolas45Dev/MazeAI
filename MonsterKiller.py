from Maze import Maze
from Player import Player
from Constants import *
import pygame
import random
import statistics

POPULATION_SIZE = 40
NUMBER_OF_GENERATIONS = 60
CROSSOVER_RATE = 0.8
MUTATION_RATE = 0.01

TOURNAMENT_SIZE = 10
DIVERSITY_THRESHOLD = 10

NUMBER_OF_BITS = 12

class MonsterKiller:

    def __init__(self, maze, player):
        self.monster = None
        self.maze = maze
        self.player = player

    def int_to_bit_array(self, n):
        # Get binary representation without the sign prefix
        binary_str = bin(n & 0xFFF)[2:]
        print(f"Binary of {n} : {binary_str}")
        # Convert the binary string to a list of integers
        bit_array = [int(bit) for bit in binary_str]

        #print(f"Binary 1 of {n}: {bit_array}")

        #binary_str = bin(n)
        #bit_array = [int(bit) for bit in binary_str[3:]]  # Skip the first three characters '-0b'
        #print(f"Binary 2 of {n}: {bit_array}")

        #print(n, bit_array)

        return bit_array

        ## Get binary representation with the sign prefix
        #binary_str = bin(n)
#
        ## Convert the binary string to a list of integers
        #bit_array = [int(bit) for bit in binary_str[3:]]  # Skip the first three characters '-0b'
#
        #return bit_array

    def bit_array_to_int(self, bit_array):
        # Convert the list of integers to a binary string
        binary_str = ''.join(map(str, bit_array))

        # Convert the binary string to an integer
        integer_value = int(binary_str, 2)

        print(f"Integer of {bit_array}: {integer_value}")

        return integer_value

    def twos_complement_binary(self, number, num_bits):
        # Assurer que le nombre est dans la plage de -2^(num_bits-1) à 2^(num_bits-1)-1
        max_val = 2**(num_bits - 1) - 1
        min_val = -2**(num_bits - 1)

        if number < min_val or number > max_val:
            raise ValueError("Number is out of range for {} bits".format(num_bits))

        # Si le nombre est négatif, trouver la représentation binaire de son complément à deux
        if number < 0:
            positive_value = -number
            positive_binary = bin(positive_value)[2:]  # Omettre le préfixe '0b'
            positive_binary_padded = positive_binary.zfill(
                num_bits)  # Remplir de zéros à gauche pour atteindre num_bits

            # Inverser les bits
            inverted_binary = ''.join('1' if bit == '0' else '0' for bit in positive_binary_padded)

            # Ajouter 1 au résultat inversé
            carry = 1
            result = ''
            for bit in inverted_binary[::-1]:  # Itérer à l'envers
                if bit == '0' and carry == 1:
                    result = '1' + result
                    carry = 0
                elif bit == '1' and carry == 1:
                    result = '0' + result
                else:
                    result = bit + result

            return [int(bit) for bit in result]
        else:
            # Si le nombre est positif, simplement retourner sa représentation binaire avec remplissage de zéros à gauche
            return [int(bit) for bit in bin(number)[2:].zfill(num_bits)]

    def from_twos_complement_binary(self, bit_array):
        # Vérifier si le nombre est négatif

        binary_string = ''.join(map(str, bit_array))
        is_negative = binary_string[0] == '1'

        if is_negative:
            # Si le nombre est négatif, calculer le complément à deux
            inverted_binary = ''.join('1' if bit == '0' else '0' for bit in binary_string)
            number = int(inverted_binary, 2) + 1
            return -number
        else:
            # Si le nombre est positif, simplement le convertir en base 10
            return int(binary_string, 2)


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
            crossover_point = random.randint(1, NUMBER_OF_BITS - 1)
            child1 = []
            child2 = []

            for index in range(NUM_ATTRIBUTES):
                child1.append(parent1[index][:crossover_point] + parent2[index][crossover_point:])
                child2.append(parent2[index][:crossover_point] + parent1[index][crossover_point:])
            return child1, child2
        else:
            return parent1, parent2

    def mutate(self, individual):
        for i in range(NUM_ATTRIBUTES):
            if random.random() < MUTATION_RATE:
                bit_index = random.randint(0, NUMBER_OF_BITS -1)
                if(individual[i][bit_index] == 1):
                    individual[i][bit_index] = 0
                else:
                    individual[i][bit_index] = 1
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

                parent1 = [self.twos_complement_binary(attribute, NUMBER_OF_BITS) for attribute in parent1]
                parent2 = [self.twos_complement_binary(attribute, NUMBER_OF_BITS) for attribute in parent2]

                child1, child2 = self.crossover(parent1, parent2)

                child1 = self.mutate(child1)
                child2 = self.mutate(child2)

                child1 = [self.from_twos_complement_binary(attribute) for attribute in child1]
                child2 = [self.from_twos_complement_binary(attribute) for attribute in child2]

                next_generation.extend([child1, child2])

            population = next_generation

            # Optional: Print best fitness in each generation
            print(f"Generation {generation}, Best Fitness: {self.calculate_fitness(population[0])}")

        # If no individual reaches the threshold, return the best found
        return population[0]