from Monster import *
import random
from Player import Player

GNOME_MAX_LEN = 12


class Individu:

    def __init__(self, chromosome, monster, player):
        self.chromosome = chromosome
        self.monster = monster
        self.player = player
        self.scores = 0
        self.fitness = self.cal_fitness()

    @classmethod
    def mutated_genes(self):
        gene = random.randint(-1000, 1000)
        gene = self.encode_population(gene)
        return gene

    @classmethod
    def create_gnome(self):
        gnome_len = GNOME_MAX_LEN
        return [self.mutated_genes() for _ in range(gnome_len)]

    def mate(self, parent2):
        child_chromosome = []

        for gene1, gene2 in zip(self.chromosome, parent2.chromosome):
            prob = random.random()
            if prob < 0.40:
                child_chromosome.append(gene1)
            elif prob < 0.90:
                child_chromosome.append(gene2)
            else:
                child_chromosome.append(self.mutated_genes())

        return Individu(child_chromosome, self.monster, self.player)

    def cal_fitness(self):
        fitness = 0
        decoded_chromosome = [self.decode_population(self.chromosome[gene]) for gene in range(len(self.chromosome))]
        self.player.set_attributes(decoded_chromosome)
        self.scores, fitness = self.monster.mock_fight(self.player)
        return fitness

    @classmethod
    def encode_population(self, value, bits=11):
        value = max(-1000, min(1000, value))
        if value < 0:
            signe = '1'
            value = abs(value)
        else:
            signe = '0'
        bin_value = bin(value)[2:]
        bin_value = bin_value.zfill(bits - 1)
        bin_value = signe + bin_value
        return bin_value

    @classmethod
    def decode_population(self, bin):
        signe = bin[0]
        value = bin[1:]
        value = int(value, base=2)
        if signe == '1':
            value = -value
        return value

    @classmethod
    def get_decoded_chromosome(self, chromosome):
        return [self.decode_population(chromosome[g]) for g in range(GNOME_MAX_LEN)]
