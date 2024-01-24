import math

import matplotlib.pyplot as plt

from Player import Player
from MazeSolver import MazeSolver
import pygame
from Maze import Maze
import ObstacleDodger
from Constants import *
from swiplserver import PrologMQI

MOVE_PLAYER_RIGHT = pygame.USEREVENT + 1
MOVE_PLAYER_LEFT = pygame.USEREVENT + 2
MOVE_PLAYER_UP = pygame.USEREVENT + 3
MOVE_PLAYER_DOWN = pygame.USEREVENT + 4


# This the AI player
class AIEngine:

    def __init__(self, player: Player, name: str, maze_file, maze: Maze):
        self.name = name
        self.player = player
        self.maze = maze
        self.graphic_maze = MazeSolver(maze_file)
        self.dodger = ObstacleDodger.Dodger()
        self.tuile_size = (self.maze.tile_size_x, self.maze.tile_size_y)

    def index_2d(self, list, item):
        for i, x in enumerate(list):
            if item in x:
                return i, x.index(item)

    def findMazeEnd(self):
        # Get the coordinates of the maze end from the maze file
        maze_file = open(self.graphic_maze.maze_file, "r")
        maze = []
        for line in maze_file:
            line = line.replace("\n", "")
            line = line.split(",")
            maze.append(line)
        return self.index_2d(maze, 'E')

    # The coordinates in the graph are 1 to 14 for y and 1 to 23 for x
    def formatCoordinates(self, coordinates):
        return coordinates[0] - 1, coordinates[1] - 1

    def computeShortestPath(self):
        self.player_position_start = (0, 1)
        self.player_position_end = (15, 22)
        self.shortest_graph_list = self.graphic_maze.getShortestPath(self.player_position_start,
                                                                     self.player_position_end)

    # This method loop through the shortest path and move the player accordingly
    def movePlayer(self):
        coordinate = self.shortest_graph_list[0]

        player_x = self.player.get_position()[1] // 60
        player_y = self.player.get_position()[0] // 54

        self.direction_to_move = 0

        # Move the player to the coordinate
        if coordinate[0] < player_x:
            self.direction_to_move = UP
        elif coordinate[0] > player_x:
            self.direction_to_move = DOWN
        elif coordinate[1] < player_y:
            self.direction_to_move = LEFT
        elif coordinate[1] > player_y:
            self.direction_to_move = RIGHT

        self.direction_to_move = self.dodgeObstacles()
        # move the player in the direction computed by the fuzzy logic
        if self.direction_to_move == LEFT:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_LEFT))
        elif self.direction_to_move == RIGHT:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_RIGHT))
        elif self.direction_to_move == UP:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_UP))
        elif self.direction_to_move == DOWN:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_DOWN))
        elif self.direction_to_move == HALF_LEFT:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_LEFT))
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_DOWN))
        elif self.direction_to_move == HALF_RIGHT:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_RIGHT))
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_DOWN))

        if len(self.maze.make_perception_list(self.player, "")[4]):
            self.door_state = self.maze.look_at_door(self.player, "")
            solution = self.resolvePuzzle()
            self.maze.unlock_door(solution)


        # if the coordinate is reached, remove it from the list
        if coordinate == (player_x, player_y) and len(self.shortest_graph_list) > 1:
            self.shortest_graph_list.pop(0)
        elif len(self.shortest_graph_list) == 1:
            pygame.event.post(pygame.event.Event(MOVE_PLAYER_DOWN))

    # This method uses fuzzy logic to dodge obstacles
    def dodgeObstacles(self):
        vision = self.maze.make_perception_list(self.player, "")
        self.dodger.maze = self.maze
        return self.dodger.dodge(vision, self.player, self.direction_to_move)

    # If a coin or a treasure is near the player, the method will change the player direction to get it
    def getCoinTreasure(self):
        vision = self.maze.make_perception_list(self.player, "")
        for item in vision[2]:
            if item[0] < 0:
                pygame.event.post(pygame.event.Event(MOVE_PLAYER_LEFT))
            elif item[0] > 0:
                pygame.event.post(pygame.event.Event(MOVE_PLAYER_RIGHT))
            elif item[1] < 0:
                pygame.event.post(pygame.event.Event(MOVE_PLAYER_UP))
            elif item[1] > 0:
                pygame.event.post(pygame.event.Event(MOVE_PLAYER_DOWN))

    def resolvePuzzle(self):
        try:
            with PrologMQI() as mqi:
                with mqi.create_thread() as prolog_thread:
                    prolog_thread.query(f"consult('./prolog/enigme.pl')")
                    crystals = self.door_state[0]
                    crystals.pop(0)
                    lock_color = self.door_state[0][0]
                    query_string = f"remove_crystal({crystals}, {lock_color}, CrystalToRemove)"
                    solutions = prolog_thread.query(query_string)
                    if solutions:
                        return solutions[0]['CrystalToRemove']
                    else:
                        return "No solution found"
        except Exception as e:
            return f"Error executing Prolog query: {e}"
