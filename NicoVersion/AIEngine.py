import math

import matplotlib.pyplot as plt

from Player import Player
from MazeSolver import MazeSolver
import pygame
from Maze import Maze
from ObstacleDodger import ObstacleDodger
from Constants import *
from swiplserver import PrologMQI
from MonsterKiller import MonsterKiller

# This the AI player
class AIEngine:

    def __init__(self, player: Player, maze: Maze):
        self.player = player
        self.maze = maze
        self.mazeSolver = MazeSolver(self.maze.maze)
        self.path = None
        self.nextPathIndex = 1
        self.instruction = ''

        self.obstacle_dodger = ObstacleDodger(self.maze)
        self.tuile_size = (self.maze.tile_size_x, self.maze.tile_size_y)
        self.monster_killer = MonsterKiller(maze)
        self.monster = None

        self.topWall = None
        self.rightWall = None
        self.bottomWall = None
        self.leftWall = None

    def getInstruction(self):
        # Make sure the path is computed
        if not self.path:
            self.path = self.mazeSolver.computePath()

        # get player rectangle
        player_rect = self.player.get_rect()

        # get current position
        current_pos = [player_rect.centery, player_rect.centerx]
        current_map_tile = [current_pos[0]//self.maze.tile_size_y, current_pos[1]//self.maze.tile_size_x]


        # get next tile
        next_map_tile = self.path[self.nextPathIndex]
        next_pos = [(next_map_tile[0] + 0.5)*self.maze.tile_size_y, (next_map_tile[1] + 0.5)*self.maze.tile_size_x]

        next_tile_top = next_map_tile[0] * self.maze.tile_size_y
        next_tile_right = (next_map_tile[1] + 1) * self.maze.tile_size_x
        next_tile_bottom = (next_map_tile[0] + 1) * self.maze.tile_size_y
        next_tile_left = next_map_tile[1] * self.maze.tile_size_x

        # Check if player is fully on the tile
        if next_tile_top <= player_rect.top and next_tile_right >= player_rect.right and next_tile_bottom >= player_rect.bottom and next_tile_left <= player_rect.left:
            #print('Next position -----------------------------------------------------------')
            self.nextPathIndex += 1
            next_map_pos = self.path[self.nextPathIndex]
            next_pos = [(next_map_tile[0] + 0.5) * self.maze.tile_size_y,
                        (next_map_tile[1] + 0.5) * self.maze.tile_size_x]

        diff_y = abs(next_pos[0] - current_pos[0])
        diff_x = abs(next_pos[1] - current_pos[1])

        next_instruction = ''

        if next_pos[0] > current_pos[0] and diff_y >= diff_x:
            next_instruction = DOWN
        elif next_pos[0] < current_pos[0] and diff_y >= diff_x:
            next_instruction = UP
        elif next_pos[1] > current_pos[1]:
            next_instruction = RIGHT
        elif next_pos[1] < current_pos[1]:
            next_instruction = LEFT

        [walls, obstacles, items, monsters, doors] = self.maze.make_perception_list(self.player, "")

        # Reset wall
        self.topWall = None
        self.rightWall = None
        self.bottomWall = None
        self.leftWall = None

        # Trouver les mur bloquant
        if self.checkForWalls(walls):
            for wall in walls:
                #print(f"Wall({wall.center})")
                # For the right wall
                if wall.left > player_rect.right:
                    if wall.top <= player_rect.top and wall.bottom >= player_rect.top and next_instruction != UP:
                        self.setRightWall(wall.left)
                    elif wall.top <= player_rect.bottom and wall.bottom >= player_rect.bottom and next_instruction != DOWN:
                        self.setRightWall(wall.left)

                # For the left wall
                elif wall.right < player_rect.left:
                    if wall.top < player_rect.top and wall.bottom > player_rect.top and next_instruction != UP:
                        self.setLeftWall(wall.right)
                    elif wall.top < player_rect.bottom and wall.bottom > player_rect.bottom and next_instruction != DOWN:
                        self.setLeftWall(wall.right)

                # For the top wall
                elif wall.bottom < player_rect.top:
                    if wall.left < player_rect.right and wall.right > player_rect.right and next_instruction != RIGHT:
                        self.setTopWall(wall.bottom)
                    elif wall.left < player_rect.left and wall.right > player_rect.left and next_instruction != LEFT:
                        self.setTopWall(wall.bottom)

                # For the bottom wall
                elif wall.top > player_rect.bottom:
                    if wall.left < player_rect.right and wall.right > player_rect.right and next_instruction != RIGHT:
                        self.setBottomWall(wall.top)
                    elif wall.left < player_rect.left and wall.right > player_rect.left and next_instruction != LEFT:
                        self.setBottomWall(wall.top)

            # Check for unset walls and find on map
            if self.topWall is None:
                x = int(player_rect.centerx // self.maze.tile_size_x)
                y = int(player_rect.centery // self.maze.tile_size_y)
                while self.maze.maze[y][x] not in DELIMITER:
                    y -= 1

                self.setTopWall(y * self.maze.tile_size_y + self.maze.tile_size_y)

            if self.rightWall is None:
                x = int(player_rect.centerx // self.maze.tile_size_x)
                y = int(player_rect.centery // self.maze.tile_size_y)
                while self.maze.maze[y][x] not in DELIMITER:
                    x += 1

                self.setRightWall(x * self.maze.tile_size_x)

            if self.bottomWall is None:
                x = int(player_rect.centerx // self.maze.tile_size_x)
                y = int(player_rect.centery // self.maze.tile_size_y)
                while self.maze.maze[y][x] not in DELIMITER:
                    y += 1

                self.setBottomWall(y * self.maze.tile_size_y)

            if self.leftWall is None:
                x = int(player_rect.centerx // self.maze.tile_size_x)
                y = int(player_rect.centery // self.maze.tile_size_y)
                while self.maze.maze[y][x] not in DELIMITER:
                    x -= 1
                self.setLeftWall(x * self.maze.tile_size_x + self.maze.tile_size_x)

        # Check for obstacle
        if self.checkForObstacles(obstacles):
            closest_obstacle = None
            distance = 0
            for obstacle in obstacles:
                if next_instruction == UP or next_instruction == DOWN:
                    if player_rect.left < obstacle.right and player_rect.right > obstacle.left:
                        temp = (player_rect.centerx - obstacle.centerx)**2 + (player_rect.centery - obstacle.centery)**2
                        if closest_obstacle is None or temp < distance:
                            closest_obstacle = obstacle
                            distance = temp
                elif next_instruction == RIGHT or next_instruction == LEFT:
                    if player_rect.bottom > obstacle.top and player_rect.top < obstacle.bottom:
                        temp = (player_rect.centerx - obstacle.centerx)**2 + (player_rect.centery - obstacle.centery)**2
                        if closest_obstacle is None or temp < distance:
                            closest_obstacle = obstacle
                            distance = temp
            if closest_obstacle is not None:
                next_instruction = self.obstacle_dodger.dodge(closest_obstacle, player_rect, next_instruction, self.topWall, self.rightWall, self.bottomWall, self.leftWall)

        # Check for monster
        if self.checkForMonsters(monsters) and self.monster == None:
            #print("Monster detected")
            self.monster = self.maze.make_perception_list(self.player, "")[3][0]
            solution = self.monster_killer.genetic_algorithm(self.monster)
            self.player.set_attributes(solution)
        elif self.monster not in self.maze.make_perception_list(self.player, "")[3]:
            self.monster = None

        # Check for door
        if self.checkForDoors(doors):
            #print("Door detected")
            self.door_state = self.maze.look_at_door(self.player, "")
            solution = self.resolvePuzzle()
            self.maze.unlock_door(solution)

        # Send the instruction
        self.instruction = next_instruction
        return self.instruction

    def checkForWalls(self, walls):
        if len(walls):
            return True
        return  False

    def checkForObstacles(self, obstacles):
        if len(obstacles):
            # Check if obstacle is in the direction
            return True
        return False

    def checkForMonsters(self, monsters):
        if len(monsters):
            return True
        return False

    def checkForDoors(self, doors):
        if len(doors):
            return True
        return False

    def setTopWall(self, topWall):
        if self.topWall is not None:
            if topWall > self.topWall:
                # Le mur est plus proche
                self.topWall = int(topWall)
        else:
            self.topWall = int(topWall)

    def setBottomWall(self, bottomWall):
        if self.bottomWall is not None:
            if bottomWall < self.bottomWall:
                # Le mur est plus proche
                self.bottomWall = int(bottomWall)
        else:
            self.bottomWall = int(bottomWall)

    def setRightWall(self, rightWall):
        if self.rightWall is not None:
            if rightWall < self.rightWall:
                # Le mur est plus proche
                self.rightWall = int(rightWall)
        else:
            self.rightWall = int(rightWall)

    def setLeftWall(self, leftWall):
        if self.leftWall is not None:
            if leftWall > self.leftWall:
                # Le mur est plus proche
                self.leftWall = int(leftWall)
        else:
            self.leftWall = int(leftWall)

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
            while True:
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
        except Exception as e:
            return f"Error executing Prolog query: {e}"
