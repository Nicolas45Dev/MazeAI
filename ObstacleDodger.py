import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import math
import matplotlib.pyplot as plt
from Constants import *

class Dodger:
    def __init__(self):
        self.actions = []
        self.last_player_position = None
        self.last_action = DOWN
        self.state = 0
        self.quadrant = 1
        self.maze = None

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

    def dodge(self, perception_list, player):

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
        if self.last_action == DOWN or self.last_action == UP:
            if player_size_box_x[0] > obstacle_size_box_x[1] or player_size_box_x[1] < obstacle_size_box_x[0]:
                return self.last_action
        else:
            if player_size_box_y[0] > obstacle_size_box_y[1] or player_size_box_y[1] < obstacle_size_box_y[0]:
                return self.last_action

        self.createFuzzyController()

        if self.last_action == DOWN or self.last_action == UP:
            self.dodger.input['position'] = obstacle_pos_mapped[0]
        else:
            self.dodger.input['position'] = obstacle_pos_mapped[1]

        self.dodger.compute()
        direction = self.dodger.output['direction']

        # Translate the direction to a direction in the game
        discrete_direction = int(direction / 5)
        direction_to_move = DOWN
        # possilbe directions are -2, -1, 0, 1, 2 print("discrete_direction: ", discrete_direction)
        direction_to_move = self.decode_action(discrete_direction, self.last_action)

        # Record the action taken
        self.actions.append(direction_to_move)

        # Update the last player position
        self.last_player_position = player_pos
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
