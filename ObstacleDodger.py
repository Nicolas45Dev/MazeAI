import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import math
import matplotlib.pyplot as plt

class Dodger:
    def __init__(self):
        pass

    def dodge(self, perception_list, player):
        # Obstacle list are the second element of the vision list
        # compute the angle of the obstacle from the player and the distance
        for obstacle in perception_list[1]:
            # angle in degree
            x_size = abs(player.get_position()[0] - obstacle[0])
            y_size = abs(player.get_position()[1] - obstacle[1])
            angle = math.degrees(math.atan2(y_size, x_size))
            player_position = player.get_position()
            distance = math.sqrt((obstacle[0] - player_position[0]) ** 2 + (obstacle[1] - player_position[1]) ** 2)

        # Fuzzy logic to dodge obstacles
        p_angle_left = np.arange(0, 90, 1)
        p_angle_right = np.arange(90, 180, 1)
        p_wall_distance_left = np.arange(0, 100, 1)
        p_wall_distance_right = np.arange(0, 100, 1)

        # 0 - 90 is right and 90 - 180 is left
        # Fuzzification right angle 0-25, 25-80, 80-90 left angle 90-155, 155-180
        angle_left_full = fuzz.trimf(p_angle_left, [45, 90, 90])
        angle_left_med = fuzz.trimf(p_angle_left, [20, 45, 70])
        angle_left_low = fuzz.trimf(p_angle_left, [0, 0, 45])

        angle_right_full = fuzz.trimf(p_angle_right, [90, 90, 135])
        angle_right_med = fuzz.trimf(p_angle_right, [110, 135, 160])
        angle_right_low = fuzz.trimf(p_angle_right, [135, 180, 180])

        wall_left_distance_med = fuzz.trimf(p_wall_distance_left, [0, 50, 100])
        wall_left_distance_near = fuzz.trimf(p_wall_distance_left, [0, 0, 50])
        wall_left_distance_far = fuzz.trimf(p_wall_distance_left, [50, 100, 100])

        wall_distance_right_med = fuzz.trimf(p_wall_distance_right, [0, 50, 100])
        wall_distance_right_near = fuzz.trimf(p_wall_distance_right, [0, 0, 50])
        wall_distance_right_far = fuzz.trimf(p_wall_distance_right, [50, 100, 100])

        action_direction_left_lo = fuzz.interp_membership(p_angle_left, angle_left_low, angle)
        action_direction_left_med = fuzz.interp_membership(p_angle_left, angle_left_med, angle)
        action_direction_left_hi = fuzz.interp_membership(p_angle_left, angle_left_full, angle)

        action_direction_right_lo = fuzz.interp_membership(p_angle_right, angle_right_low, angle)
        action_direction_right_med = fuzz.interp_membership(p_angle_right, angle_right_med, angle)
        action_direction_right_hi = fuzz.interp_membership(p_angle_right, angle_right_full, angle)

        # Here we apply the rules

        # # Visualize these universes and membership functions
        # fig, (ax0, ax1, ax2) = plt.subplots(nrows=3, figsize=(8, 9))
        #
        # ax0.plot(p_angle_left, angle_left_full, 'b', linewidth=1.5, label='Full')
        # ax0.plot(p_angle_left, angle_left_med, 'g', linewidth=1.5, label='Med')
        # ax0.plot(p_angle_left, angle_left_low, 'r', linewidth=1.5, label='Low')
        # ax0.set_title('Angle Left')
        # ax0.legend()
        #
        # ax1.plot(p_angle_right, angle_right_full, 'b', linewidth=1.5, label='Full')
        # ax1.plot(p_angle_right, angle_right_med, 'g', linewidth=1.5, label='Med')
        # ax1.plot(p_angle_right, angle_right_low, 'r', linewidth=1.5, label='Low')
        # ax1.set_title('Angle Right')
        # ax1.legend()
        #
        # # Turn off top/right axes
        # for ax in (ax0, ax1, ax2):
        #     ax.spines['top'].set_visible(False)
        #     ax.spines['right'].set_visible(False)
        #     ax.get_xaxis().tick_bottom()
        #     ax.get_yaxis().tick_left()
        #
        # plt.tight_layout()
        # plt.show()
