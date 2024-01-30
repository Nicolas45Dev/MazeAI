# Université de Sherbrooke
# Code for Artificial Intelligence module
# Adapted by Audrey Corbeil Therrien, Simon Brodeur

# Source code
# Classic cart-pole system implemented by Rich Sutton et al.
# Copied from http://incompleteideas.net/sutton/book/code/pole.c
# permalink: https://perma.cc/C9ZM-652R

# NOTE : The print_state function of the FuzzyController needs
# to be updated with the latest version, available on github
# https://github.com/scikit-fuzzy/scikit-fuzzy/blob/master/skfuzzy/control/controlsystem.py
# Lines 514-572 from github replace lines 493-551 in the 0.4.2 2019 release

import gym
import time

import numpy as np

from cartpole import *
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

FORCE_MAG = 50.0
def createFuzzyController():
    # TODO: Create the fuzzy variables for inputs and outputs.
    # Defuzzification (defuzzify_method) methods for fuzzy variables:
    #    'centroid': Centroid of area
    #    'bisector': bisector of area
    #    'mom'     : mean of maximum
    #    'som'     : min of maximum
    #    'lom'     : max of maximum
    angleDeLaPole = ctrl.Antecedent(np.arange(-90, 91, 1), 'angle')
    omegaPole = ctrl.Antecedent(np.arange(-45, 46, 1), 'omega')
    #ant2 = ctrl.Antecedent(np.linspace(-1, 1, 1000), 'input2')
    force = ctrl.Consequent(np.arange(-10, 11, 1), 'force')

    # Accumulation (accumulation_method) methods for fuzzy variables:
    #    np.fmax
    #    np.multiply
    #cons1.accumulation_method = np.fmax

    # TODO: Create membership functions
    force['gauche'] = fuzz.trimf(force.universe, [-10, -10, -3])
    force['littlebit_gauche'] = fuzz.trimf(force.universe, [-10, -6, 0])
    force['neutre'] = fuzz.trimf(force.universe, [-5, 0, 5])
    force['littlebit_droite'] = fuzz.trimf(force.universe, [0, 6, 10])
    force['droite'] = fuzz.trimf(force.universe, [3, 10, 10])

    angleDeLaPole['gauche'] = fuzz.trimf(angleDeLaPole.universe, [-90, -90, -22])
    angleDeLaPole['littlebit_gauche'] = fuzz.trimf(angleDeLaPole.universe, [-45, -22, 0])
    angleDeLaPole['neutre'] = fuzz.trimf(angleDeLaPole.universe, [-22, 0, 22])
    angleDeLaPole['littlebit_droite'] = fuzz.trimf(angleDeLaPole.universe, [0, 22, 45])
    angleDeLaPole['droite'] = fuzz.trimf(angleDeLaPole.universe, [22, 90, 90])

    omegaPole['gauche'] = fuzz.trimf(omegaPole.universe, [-45, -45, -22])
    omegaPole['littlebit_gauche'] = fuzz.trimf(omegaPole.universe, [-45, -22, 0])
    omegaPole['neutre'] = fuzz.trimf(omegaPole.universe, [-22, 0, 22])
    omegaPole['littlebit_droite'] = fuzz.trimf(omegaPole.universe, [0, 22, 45])
    omegaPole['droite'] = fuzz.trimf(omegaPole.universe, [22, 45, 45])

    #force.view()
    #angleDeLaPole.view()
    #omegaPole.view()

    # TODO: Define the rules.
    rules = []
    rules.append(ctrl.Rule(angleDeLaPole['gauche'] | omegaPole['gauche'], force['gauche']))
    rules.append(ctrl.Rule(angleDeLaPole['littlebit_gauche'] | omegaPole['littlebit_gauche'], force['littlebit_gauche']))
    rules.append(ctrl.Rule(angleDeLaPole['neutre'] | omegaPole['neutre'], force['neutre']))
    rules.append(ctrl.Rule(angleDeLaPole['littlebit_droite'] | omegaPole['littlebit_droite'], force['littlebit_droite']))
    rules.append(ctrl.Rule(angleDeLaPole['droite'] | omegaPole['droite'], force['droite']))

    # Conjunction (and_func) and disjunction (or_func) methods for rules:
    #     np.fmin
    #     np.fmax
    for rule in rules:
        #rule.view()
        rule.and_func = np.fmin
        rule.or_func = np.fmax

    system = ctrl.ControlSystem(rules)
    sim = ctrl.ControlSystemSimulation(system)
    return sim


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    # Create the environment and fuzzy controller
    env = CartPoleEnv("human")
    fuzz_ctrl = createFuzzyController()

    # Display rules
    print('------------------------ RULES ------------------------')
    for rule in fuzz_ctrl.ctrl.rules:
        print(rule)
    print('-------------------------------------------------------')

    # Display fuzzy variables
    for var in fuzz_ctrl.ctrl.fuzzy_variables:
        var.view()
    plt.show()

    VERBOSE = False

    for episode in range(10):
        print('Episode no.%d' % (episode))
        env.reset()

        isSuccess = True
        action = np.array([0.0], dtype=np.float32)
        for _ in range(10000):
            env.render()
            time.sleep(0.01)

            # Execute the action
            observation, _, done, _ = env.step(action)
            if done:
                # End the episode
                isSuccess = False
                break

            # Select the next action based on the observation
            cartPosition, cartVelocity, poleAngle, poleVelocityAtTip = observation

            # TODO: set the input to the fuzzy system
            # input the angle of the pole in degrees
            fuzz_ctrl.input['angle'] = (poleAngle * 180 / np.pi)
            # input the angular velocity of the pole in degrees per second
            fuzz_ctrl.input['omega'] = (poleVelocityAtTip * 180 / np.pi)

            fuzz_ctrl.compute()
            if VERBOSE:
                fuzz_ctrl.print_state()

            # TODO: get the output from the fuzzy system
            force = fuzz_ctrl.output['force']
            #print(poleVelocityAtTip)

            action = np.array(force, dtype=np.float32).flatten()

    env.close()
