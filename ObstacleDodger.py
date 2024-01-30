import numpy as np
import pygame
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import math
import matplotlib.pyplot as plt
from Constants import *
from Maze import Maze

class ObstacleDodger:
    def __init__(self, maze: Maze):
        self.maze = maze
        self.actions = []
        self.last_player_position = None
        self.last_action = DOWN
        self.state = 0
        self.quadrant = 1

        self.max_distance_x = self.maze.tile_size_x * PERCEPTION_RADIUS
        self.max_distance_y = self.maze.tile_size_y * PERCEPTION_RADIUS

        self.dodger = None

    def createFuzzyController(self):

        position_obstacle = ctrl.Antecedent(np.arange(-10, 11, 1), 'position_obstacle')
        position_player = ctrl.Antecedent(np.arange(-10, 11, 1), 'position_player')
        distance = ctrl.Antecedent(np.arange(0, 11, 1), 'distance')

        direction = ctrl.Consequent(np.arange(-1, 2, 1), 'direction')

        # define rules
        position_obstacle['left'] = fuzz.trimf(position_obstacle.universe, [-10, -10, 2])
        position_obstacle['center'] = fuzz.trimf(position_obstacle.universe, [0, 0, 0])
        position_obstacle['right'] = fuzz.trimf(position_obstacle.universe, [-2, 10, 10])

        position_player['left'] = fuzz.trimf(position_player.universe, [-10, -10, 2])
        position_player['center'] = fuzz.trimf(position_player.universe, [0, 0, 0])
        position_player['right'] = fuzz.trimf(position_player.universe, [-2, 10, 10])

        distance['near'] = fuzz.trimf(distance.universe, [0, 0, 5])
        distance['medium'] = fuzz.trimf(distance.universe, [0, 5, 10])
        distance['far'] = fuzz.trimf(distance.universe, [5, 10, 10])

        direction['left'] = fuzz.trimf(direction.universe, [-1, -1, 0.5])
        direction['straight'] = fuzz.trimf(direction.universe, [-0.5, 0, 0.5])
        direction['right'] = fuzz.trimf(direction.universe, [-0.5, 1, 1])

        #position_obstacle.view()
        #position_player.view()
        #distance.view()
        #direction.view()

        rules = []
        rules.append(ctrl.Rule(distance['far'], direction['straight']))
        rules.append(ctrl.Rule(distance['medium'], direction['straight']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['left'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['center'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['right'], direction['right']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['center'] & position_player['left'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['center'] & position_player['center'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['center'] & position_player['right'], direction['right']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['left'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['center'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['right'], direction['left']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        self.dodger_ctrl = ctrl.ControlSystem(rules)
        self.dodger = ctrl.ControlSystemSimulation(self.dodger_ctrl)

    def new_createFuzzyController(self):

        position_obstacle = ctrl.Antecedent(np.arange(-10, 11, 1), 'position_obstacle')
        position_player = ctrl.Antecedent(np.arange(-10, 11, 1), 'position_player')
        distance = ctrl.Antecedent(np.arange(0, 11, 1), 'distance')

        direction = ctrl.Consequent(np.arange(-1, 2, 1), 'direction')

        # define rules
        position_obstacle['left'] = fuzz.trimf(position_obstacle.universe, [-10, -10, -4])
        position_obstacle['left-center'] = fuzz.trimf(position_obstacle.universe, [-8, -3, 2])
        position_obstacle['right-center'] = fuzz.trimf(position_obstacle.universe, [-2, 3, 8])
        position_obstacle['right'] = fuzz.trimf(position_obstacle.universe,[ 4, 10, 10])

        position_player['left'] = fuzz.trimf(position_player.universe, [-10, -10, -4])
        position_player['left-center'] = fuzz.trimf(position_player.universe, [-8, -3, 2])
        position_player['right-center'] = fuzz.trimf(position_player.universe, [-2, 3, 8])
        position_player['right'] = fuzz.trimf(position_player.universe, [4, 10, 10])

        distance['near'] = fuzz.trimf(distance.universe, [0, 0, 4])
        distance['medium'] = fuzz.trimf(distance.universe, [0, 5, 10])
        distance['far'] = fuzz.trimf(distance.universe, [5, 10, 10])

        direction['left'] = fuzz.trimf(direction.universe, [-1, -1, 0.5])
        direction['straight'] = fuzz.trimf(direction.universe, [-0.5, 0, 0.5])
        direction['right'] = fuzz.trimf(direction.universe, [-0.5, 1, 1])

        #position_obstacle.view()
        #position_player.view()
        #distance.view()
        #direction.view()

        rules = []
        rules.append(ctrl.Rule(distance['far'], direction['straight']))
        #rules.append(ctrl.Rule(distance['medium'], direction['straight']))

        #rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left'], direction['straight']))
        #rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left-center'], direction['right']))
        #rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right-center'], direction['left']))
        #rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right'], direction['straight']))

        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left'] & position_player['left'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left'] & position_player['left-center'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left'] & position_player['right-center'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left'] & position_player['right'], direction['right']))

        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left-center'] & position_player['left'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left-center'] & position_player['left-center'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left-center'] & position_player['right-center'], direction['right']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['left-center'] & position_player['right'], direction['right']))

        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right-center'] & position_player['left'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right-center'] & position_player['left-center'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right-center'] & position_player['right-center'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right-center'] & position_player['right'], direction['left']))

        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right'] & position_player['left'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right'] & position_player['left-center'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right'] & position_player['right-center'], direction['left']))
        rules.append(ctrl.Rule(distance['medium'] & position_obstacle['right'] & position_player['right'], direction['left']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['left'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['left-center'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['right-center'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left'] & position_player['right'],direction['right']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left-center'] & position_player['left'], direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left-center'] & position_player['left-center'],direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left-center'] & position_player['right-center'],direction['right']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['left-center'] & position_player['right'],direction['right']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right-center'] & position_player['left'],direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right-center'] & position_player['left-center'],direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right-center'] & position_player['right-center'],direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right-center'] & position_player['right'],direction['left']))

        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['left'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['left-center'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['right-center'], direction['left']))
        rules.append(ctrl.Rule(distance['near'] & position_obstacle['right'] & position_player['right'], direction['left']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        self.dodger_ctrl = ctrl.ControlSystem(rules)
        self.dodger = ctrl.ControlSystemSimulation(self.dodger_ctrl)

    def dodge(self, obstacle: pygame.Rect, player: pygame.Rect, direction_to_move):
        if self.dodger is None:
            self.new_createFuzzyController()

        #print(obstacle.right)

        # For the positions
        if direction_to_move == DOWN or direction_to_move == UP:
            canPassLeft = obstacle.left % self.maze.tile_size_x > player.width
            canPassRight = self.maze.tile_size_x - (obstacle.right % self.maze.tile_size_x) > player.width

            #print(f"Can pass right({canPassRight}) Can pass left({canPassLeft}) Obstacle({obstacle}) Player({player})")
            if canPassLeft or canPassRight:
                half = self.maze.tile_size_x // 2
                self.dodger.input['position_obstacle'] = (((obstacle.centerx % self.maze.tile_size_x) - half) * 10) / half
                self.dodger.input['position_player'] = (((player.centerx % self.maze.tile_size_x) - half) * 10) / half
            else:
                print("Player can't pass on the left or the right inside the tile")
                return NO_PATH

        else:
            canPassOver = obstacle.top % self.maze.tile_size_y > player.height
            canPassUnder = self.maze.tile_size_y - (obstacle.bottom % self.maze.tile_size_y) > player.height

            if canPassOver or canPassUnder:
                half = self.maze.tile_size_y // 2
                self.dodger.input['position_obstacle'] = (((obstacle.centery % self.maze.tile_size_y) - half) * 10) / half
                self.dodger.input['position_player'] = (((player.centery % self.maze.tile_size_y) - half) * 10) / half
            else:
                print("Player can't pass over or under the obstacle inside the tile")
                return NO_PATH


        # For the distance
        if direction_to_move == UP:
            self.dodger.input['distance'] = ((player.top - obstacle.bottom) * 10) / self.max_distance_y
        elif direction_to_move == RIGHT:
            self.dodger.input['distance'] = ((obstacle.left - player.right) * 10) / self.max_distance_x
        elif direction_to_move == DOWN:
            self.dodger.input['distance'] = ((obstacle.top - player.bottom) * 10) / self.max_distance_y
        elif direction_to_move == LEFT:
            self.dodger.input['distance'] = ((player.left - obstacle.right) * 10) / self.max_distance_x

        self.dodger.compute()
        direction = self.dodger.output['direction']
        #print(f"Direction({direction})")

        # Check for direction (-1, 0, 1)
        if direction <= -0.1:
            if direction_to_move == UP or direction_to_move == DOWN:
                return LEFT
            elif direction_to_move == RIGHT or direction_to_move == LEFT:
                return UP
        elif direction >= 0.1:
            if direction_to_move == UP or direction_to_move == DOWN:
                return RIGHT
            elif direction_to_move == RIGHT or direction_to_move == LEFT:
                return DOWN

        return direction_to_move
