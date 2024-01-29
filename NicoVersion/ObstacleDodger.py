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

        position = ctrl.Antecedent(np.arange(0, 100, 1), 'position')

        direction = ctrl.Consequent(np.arange(-10, 11, 5), 'direction')

        # define rules
        rules = []
        direction['gauche'] = fuzz.trimf(direction.universe, [-10, -10, -5])
        direction['littlebit_gauche'] = fuzz.trimf(direction.universe, [-10, -2, 0])
        direction['neutre'] = fuzz.trimf(direction.universe, [-2, 0, 2])
        direction['littlebit_droite'] = fuzz.trimf(direction.universe, [0, 2, 10])
        direction['droite'] = fuzz.trimf(direction.universe, [5, 10, 10])

        position['gauche'] = fuzz.trimf(position.universe, [62, 100, 100])
        position['centre_gauche'] = fuzz.trimf(position.universe, [45, 65, 85])
        position['centre_droite'] = fuzz.trimf(position.universe, [15, 35, 55])
        position['droite'] = fuzz.trimf(position.universe, [0, 0, 37])

        rules.append(ctrl.Rule(position['droite'], direction['littlebit_gauche']))
        rules.append(ctrl.Rule(position['centre_droite'], direction['gauche']))
        rules.append(ctrl.Rule(position['centre_gauche'], direction['droite']))
        rules.append(ctrl.Rule(position['gauche'], direction['littlebit_droite']))

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
        position_obstacle['left'] = fuzz.trimf(position_obstacle.universe, [-10, -10, 2])
        position_obstacle['center'] = fuzz.trimf(position_obstacle.universe, [0, 0, 0])
        position_obstacle['right'] = fuzz.trimf(position_obstacle.universe, [-2, 10, 10])

        position_player['left'] = fuzz.trimf(position_player.universe, [-10, -10, 2])
        position_player['center'] = fuzz.trimf(position_player.universe, [0, 0, 0])
        position_player['right'] = fuzz.trimf(position_player.universe, [-2, 10, 10])

        distance['near'] = fuzz.trimf(distance.universe, [0, 0, 1])
        distance['medium'] = fuzz.trimf(distance.universe, [0, 5, 10])
        distance['far'] = fuzz.trimf(distance.universe, [5, 10, 10])

        direction['left'] = fuzz.trimf(direction.universe, [-1, -1, 0.5])
        direction['straight'] = fuzz.trimf(direction.universe, [-0.5, 0, 0.5])
        direction['right'] = fuzz.trimf(direction.universe, [-0.5, 1, 1])

        # position_obstacle.view()
        # position_player.view()
        # distance.view()
        # direction.view()

        rules = []
        rules.append(ctrl.Rule(distance['far'], direction['straight']))
        rules.append(ctrl.Rule(distance['medium'], direction['straight']))

        rules.append(ctrl.Rule(position_obstacle['left'], direction['right']))

        rules.append(ctrl.Rule(position_obstacle['center'] & position_player['center'], direction['right']))

        rules.append(ctrl.Rule(position_obstacle['right'], direction['left']))

        for rule in rules:
            rule.view()
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        self.dodger_ctrl = ctrl.ControlSystem(rules)
        self.dodger = ctrl.ControlSystemSimulation(self.dodger_ctrl)

    def dodge(self, perception_list, player, direction_to_move):

        # if the perception list is empty return the last action taken
        if len(perception_list[1]) == 0:
            return direction_to_move

        player_size = player.get_size()
        player_pos = player.get_position()

        obstacle_size = (perception_list[1][0].width, perception_list[1][0].height)
        obstacle_pos = (perception_list[1][0].x, perception_list[1][0].y)
        obstacle_pos_mapped = (obstacle_pos[0] % int(self.maze.tile_size_x), obstacle_pos[1] % int(self.maze.tile_size_y))

        # obstacle_pos x range: 0 to 52 and y range: 0 to 59
        # map the obstacle position 100 to 0
        obstacle_pos_mapped = (self.map(obstacle_pos_mapped[0], 0, 52, 100, 0), self.map(obstacle_pos_mapped[1], 0, 59, 100, 0))

        player_size_box_x = (player_pos[0], player_pos[0] + player_size[0])
        player_size_box_y = (player_pos[1], player_pos[1] + player_size[1])

        obstacle_size_box_x = (obstacle_pos[0], obstacle_pos[0] + obstacle_size[0])
        obstacle_size_box_y = (obstacle_pos[1], obstacle_pos[1] + obstacle_size[1])

        # if the player can pass beside the obstacle dont dodge
        if direction_to_move == DOWN or direction_to_move == UP:
            if player_size_box_x[0] > obstacle_size_box_x[1] or player_size_box_x[1] < obstacle_size_box_x[0]:
                return direction_to_move
        else:
            if player_size_box_y[0] > obstacle_size_box_y[1] or player_size_box_y[1] < obstacle_size_box_y[0]:
                return direction_to_move

        self.createFuzzyController()

        if direction_to_move == DOWN or direction_to_move == UP:
            self.dodger.input['position'] = obstacle_pos_mapped[0]
        else:
            self.dodger.input['position'] = obstacle_pos_mapped[1]

        self.dodger.compute()
        direction = self.dodger.output['direction']

        # Translate the direction to a direction in the game
        discrete_direction = int(direction / 5)
        # possilbe directions are -2, -1, 0, 1, 2 print("discrete_direction: ", discrete_direction)
        new_direction = self.decode_action(discrete_direction, self.last_action)

        return new_direction

    def new_dodge(self, obstacle: pygame.Rect, player: pygame.Rect, direction_to_move, topWall, rightWall, bottomWall, leftWall):
        if self.dodger is None:
            self.new_createFuzzyController()

        #print(obstacle.right)

        # For the positions
        if direction_to_move == DOWN or direction_to_move == UP:
            canPassLeft = obstacle.left % self.maze.tile_size_x >= player.width
            canPassRight = self.maze.tile_size_x - (obstacle.right % self.maze.tile_size_x) >= player.width

            print(f"Can pass right({canPassRight}) Can pass left({canPassLeft}) Obstacle({obstacle}) Player({player})")
            if canPassLeft or canPassRight:
                half = self.maze.tile_size_x // 2
                self.dodger.input['position_obstacle'] = (((obstacle.centerx % self.maze.tile_size_x) - half) * 10) / half
                self.dodger.input['position_player'] = (((player.centerx % self.maze.tile_size_x) - half) * 10) / half
            else:
                print("Player can't pass on the left or the right inside the tile")
                print(f"Left wall({leftWall}) Right wall({rightWall})")
                half = (rightWall - leftWall) // 2
                middle = half + leftWall
                self.dodger.input['position_obstacle'] = ((obstacle.centerx - middle) * 10) / half
                self.dodger.input['position_player'] = ((player.centerx - middle) * 10) / half
        else:
            canPassOver = obstacle.top % self.maze.tile_size_y >= player.height
            canPassUnder = self.maze.tile_size_y - (obstacle.bottom % self.maze.tile_size_y) >= player.height

            if canPassOver or canPassUnder:
                half = self.maze.tile_size_y // 2
                self.dodger.input['position_obstacle'] = (((obstacle.centery % self.maze.tile_size_y) - half) * 10) / half
                self.dodger.input['position_player'] = (((player.centery % self.maze.tile_size_y) - half) * 10) / half
            else:
                print("Player can't pass over or under the obstacle inside the tile")
                print(f"Top wall({topWall}) Bottom wall({bottomWall})")
                half = (bottomWall - topWall) // 2
                middle = half + topWall
                self.dodger.input['position_obstacle'] = ((obstacle.centery - middle) * 10) / half
                self.dodger.input['position_player'] = ((player.centery - middle) * 10) / half

        # For the distance
        if direction_to_move == UP:
            self.dodger.input['distance'] = ((player.centery - obstacle.centery) * 10) / self.max_distance_y
        elif direction_to_move == RIGHT:
            self.dodger.input['distance'] = ((obstacle.centerx - player.centerx) * 10) / self.max_distance_x
        elif direction_to_move == DOWN:
            self.dodger.input['distance'] = ((obstacle.centery - player.centery) * 10) / self.max_distance_y
        else:
            self.dodger.input['distance'] = ((player.centerx - obstacle.centerx) * 10) / self.max_distance_x

        self.dodger.compute()
        direction = self.dodger.output['direction']
        print(f"Direction({direction})")

        # Check for direction (-1, 0, 1)
        if direction == 0:
            return direction_to_move
        elif direction < 0:
            if direction_to_move == UP or direction_to_move == DOWN:
                return LEFT
            elif direction_to_move == RIGHT or direction_to_move == LEFT:
                return UP
        else:
            if direction_to_move == UP or direction_to_move == DOWN:
                return RIGHT
            elif direction_to_move == RIGHT or direction_to_move == LEFT:
                return DOWN



        #else:
        #    if direction_to_move == UP:
        #        if direction == -1:
        #            return
        #    elif direction_to_move == RIGHT:




        #new_direction = self.decode_action(discrete_direction, self.last_action)





        #if direction_to_move == DOWN or direction_to_move == UP:
        #    self.dodger.input['position'] = obstacle_pos_mapped[0]
        #else:
        #    self.dodger.input['position'] = obstacle_pos_mapped[1]



        # Translate the direction to a direction in the game
        #discrete_direction = int(direction / 5)
        # possilbe directions are -2, -1, 0, 1, 2 print("discrete_direction: ", discrete_direction)
        #new_direction = self.decode_action(discrete_direction, self.last_action)

        #return new_direction
        return direction_to_move

    # The method will return the action to take to dodge the obstacle
    # It will consider the last action taken and the last player position
    # @orientation is the last action taken
    # @action is the encoded action
    def decode_action(self, action, orientation):
        direction_to_move = DOWN
        # possilbe directions are -2, -1, 0, 1, 2 print("discrete_direction: ", discrete_direction)
        if action == -2:
            direction_to_move = LEFT
        if action == -1:
            direction_to_move = HALF_LEFT
        if action == 0:
            direction_to_move = DOWN
        if action == 1:
            direction_to_move = HALF_RIGHT
        if action == 2:
            direction_to_move = RIGHT
        return direction_to_move

    def map(self, value, min, max, new_min, new_max):
        return (value - min) * (new_max - new_min) / (max - min) + new_min

    # This method will map the angle according to the last action taken
    # The mapped angle will always be between -90 and 90
    # @angle is the angle to map
    # @orientation is the last action taken
    def map_angle(self, angle, orientation):
        mapped_angle = angle
        # If the last action taken was DOWN the angle of the obstacle may range from 180 to 360
        if orientation == DOWN:
            mapped_angle = self.map(angle, 180, 360, 0, 180)
        # If the last action taken was UP the angle of the obstacle may range from 0 to 180
        if orientation == UP:
            mapped_angle = self.map(angle, 0, 180, 0, 180)
        # If the last action taken was LEFT the angle of the obstacle may range from 90 to 270
        if orientation == LEFT:
            mapped_angle = self.map(angle, 90, 270, 0, 180)
        # If the last action taken was RIGHT the angle of the obstacle may range from 270 to 90
        if orientation == RIGHT:
            mapped_angle = self.map(angle, 90, 270, 0, 180)
        return 90 - mapped_angle
