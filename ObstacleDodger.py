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
        self.state = 0

    def createFuzzyController(self):
        angle_obstacle = ctrl.Antecedent(np.arange(-90, 91, 1), 'angle')
        wall_distance = ctrl.Antecedent(np.arange(0, 100, 1), 'wall_distance')

        direction = ctrl.Consequent(np.arange(-10, 11, 5), 'direction')

        # define rules
        rules = []
        direction['gauche'] = fuzz.trimf(direction.universe, [-10, -10, -5])
        direction['littlebit_gauche'] = fuzz.trimf(direction.universe, [-10, -5, 0])
        direction['neutre'] = fuzz.trimf(direction.universe, [-5, 0, 5])
        direction['littlebit_droite'] = fuzz.trimf(direction.universe, [0, 5, 10])
        direction['droite'] = fuzz.trimf(direction.universe, [5, 10, 10])

        angle_obstacle['gauche'] = fuzz.trimf(angle_obstacle.universe, [-15, -1, 1])
        angle_obstacle['littlebit_gauche'] = fuzz.trimf(angle_obstacle.universe, [-35, -15, -10])
        angle_obstacle['neutre'] = fuzz.trimf(angle_obstacle.universe, [25, 40, 90])
        angle_obstacle['neutre1'] = fuzz.trimf(angle_obstacle.universe, [-90, -40, -25])
        angle_obstacle['littlebit_droite'] = fuzz.trimf(angle_obstacle.universe, [10, 15, 35])
        angle_obstacle['droite'] = fuzz.trimf(angle_obstacle.universe, [-1, 1, 15])

        #direction.view()
        #angle_obstacle.view()

        rules.append(ctrl.Rule(angle_obstacle['gauche'], direction['gauche']))
        rules.append(ctrl.Rule(angle_obstacle['littlebit_gauche'], direction['littlebit_gauche']))
        rules.append(ctrl.Rule(angle_obstacle['neutre'], direction['neutre']))
        rules.append(ctrl.Rule(angle_obstacle['neutre1'], direction['neutre']))
        rules.append(ctrl.Rule(angle_obstacle['littlebit_droite'], direction['littlebit_droite']))
        rules.append(ctrl.Rule(angle_obstacle['droite'], direction['droite']))

        for rule in rules:
            rule.and_func = np.fmin
            rule.or_func = np.fmax

        self.dodger_ctrl = ctrl.ControlSystem(rules)
        self.dodger = ctrl.ControlSystemSimulation(self.dodger_ctrl)

    def reverseActionList(self):
        reverse_actions = []
        for action in self.actions:
            if action == LEFT:
                reverse_actions.append(RIGHT)
            if action == RIGHT:
                reverse_actions.append(LEFT)
            if action == HALF_LEFT:
                reverse_actions.append(HALF_RIGHT)
            if action == HALF_RIGHT:
                reverse_actions.append(HALF_LEFT)
            if action == UP:
                reverse_actions.append(DOWN)
            if action == DOWN:
                reverse_actions.append(UP)
        return reverse_actions

    def dodge(self, perception_list, player):
        # Compute the angle of the player and the angle of the closest obstacle
        player_pos = player.get_position()

        # If the player is not moving, reverse the last action
        if self.last_player_position == player_pos:
            self.actions = self.reverseActionList()
            self.state = 1

        if self.state == 1:
            if len(self.actions) == 0:
                self.state = 0
                return DOWN
            return self.actions.pop(0)

        obstacle_pos = perception_list[1][0]
        angle = math.atan2(obstacle_pos.y - player_pos[1], obstacle_pos.x - player_pos[0]) * 180 / math.pi
        # if the angle is greater than 180 or less than 0, it means that the obstacle is behind the player
        if angle > 155 or angle < 25:
            self.actions.clear()
            return DOWN
        # The angle computed range from 0 to 180 map it to -90 to 90
        angle = angle - 90

        #Compute the distance between the player and the obstacle
        distance = math.sqrt((obstacle_pos[1] - player_pos[1])**2 + (obstacle_pos[0] - player_pos[0])**2)

        self.createFuzzyController()
        # Set the inputs
        self.dodger.input['angle'] = angle

        self.dodger.compute()
        direction = self.dodger.output['direction']

        # Translate the direction to a direction in the game
        discrete_direction = int(direction / 5)
        direction_to_move = DOWN
        # possilbe directions are -2, -1, 0, 1, 2 print("discrete_direction: ", discrete_direction)
        if discrete_direction == -2:
            direction_to_move = LEFT
        if discrete_direction == -1:
            direction_to_move = HALF_LEFT
        if discrete_direction == 0:
            direction_to_move = DOWN
        if discrete_direction == 1:
            direction_to_move = HALF_RIGHT
        if discrete_direction == 2:
            direction_to_move = RIGHT

        # Record the action taken
        self.actions.append(direction_to_move)
        print("direction_to_move: ", direction_to_move)


        # Update the last player position
        self.last_player_position = player_pos
        return direction_to_move
