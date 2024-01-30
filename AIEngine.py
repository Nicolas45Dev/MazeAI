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
        self.monster_killer = MonsterKiller()
        self.monster = None

        self.topWall = None
        self.rightWall = None
        self.bottomWall = None
        self.leftWall = None
        self.obstacle = None

        self.lastPosition = self.player.get_rect().center
        self.stuckCounter = 0

    def getInstruction(self):
        # Make sure the path is computed
        if not self.path:
            self.path = self.mazeSolver.computePath()

        if len(self.path) == 0:
            print('There is no path')
            return NO_PATH

        # get player rectangle
        player_rect = self.player.get_rect()

        if player_rect.center == self.lastPosition:
            self.stuckCounter += 1
            if self.stuckCounter >= 5:
                print('Player is stuck')
        else:
            self.stuckCounter = 0

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
        if  next_tile_top <= player_rect.top and \
            next_tile_right >= player_rect.right and \
            next_tile_bottom >= player_rect.bottom and \
            next_tile_left <= player_rect.left:
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

        # Check for obstacle
        next_instruction = self.checkForObstacles(obstacles, walls, player_rect, next_instruction)

        # Check for monster
        self.checkForMonsters(monsters)

        # Check for door
        self.checkForDoors(doors)

        # Send the instruction
        self.instruction = next_instruction
        self.lastPosition = player_rect.center
        return self.instruction

    def checkForWalls(self, walls, player_rect, next_instruction):
        self.topWall = None
        self.rightWall = None
        self.bottomWall = None
        self.leftWall = None

        if len(walls):
            for wall in walls:
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

    def checkForObstacles(self, obstacles, walls, player_rect, next_instruction):
        # Check if already avoiding obstacle and if it is still blocking
        if self.obstacle is not None:
            if not self.isObstacleBlockingPlayer(self.obstacle, player_rect, next_instruction):
                self.obstacle = None

        # Find the closest obstacle that is blocking
        if len(obstacles) and self.obstacle is None:
            closest_obstacle = None
            closest_distance = 0
            for obstacle in obstacles:
                if self.isObstacleBlockingPlayer(obstacle, player_rect, next_instruction):
                    distance = (player_rect.centerx - obstacle.centerx) ** 2 + (player_rect.centery - obstacle.centery) ** 2
                    if closest_obstacle is None or distance < closest_distance:
                        closest_obstacle = obstacle
                        closest_distance = distance
            #print(f"Distance {closest_distance}")
            self.obstacle = closest_obstacle

        # Avoid the obstacle if any
        if self.obstacle is not None:
            #self.checkForWalls(walls, player_rect, next_instruction)
            print(f"Avoiding {self.obstacle}")
            #new_instruction = self.obstacle_dodger.dodge(self.obstacle, player_rect, next_instruction, self.topWall,self.rightWall, self.bottomWall, self.leftWall)
            new_instruction = self.obstacle_dodger.dodge(self.obstacle, player_rect, next_instruction)

            if new_instruction == NO_PATH:
                print("Player can't pass. Recomputing the path")
                if self.nextPathIndex + 1 > len(self.path)-1:
                    print('Cant access tue exit')
                else:
                    oy = self.path[self.nextPathIndex + 1][0]
                    ox = self.path[self.nextPathIndex + 1][1]
                    print(f"Changing {self.path[self.nextPathIndex]} to a wall")

                    self.maze.maze[oy][ox] = WALL
                    py = int(player_rect.centery // self.maze.tile_size_y)
                    px = int(player_rect.centerx // self.maze.tile_size_x)
                    self.mazeSolver.setStart(py, px)

                    self.path = self.mazeSolver.computePath()
                    print(f" new Path {self.path}")
                    self.nextPathIndex = 1

            # Check if there is an obstacle blocking the new instruction
            for obstacle in obstacles:
                if self.isObstacleBlockingPlayer(obstacle, player_rect, new_instruction):
                    return next_instruction

            return new_instruction

        # Return the current instruction since there is nothing to avoid
        return next_instruction

    def checkForMonsters(self, monsters):
        if len(monsters) and self.monster == None:
            # print("Monster detected")
            self.monster_killer = MonsterKiller()
            self.monster = self.maze.make_perception_list(self.player, "")[3][0]
            solution = self.monster_killer.genetic_algorithm(self.monster)
            self.player.set_attributes(solution)
        elif self.monster not in monsters:
            self.monster = None

    def checkForDoors(self, doors):
        if len(doors):
            # print("Door detected")
            self.door_state = self.maze.look_at_door(self.player, "")
            solution = self.resolvePuzzle()
            self.maze.unlock_door(solution)

    def isObstacleBlockingPlayer(self, obstacle, player_rect, next_instruction):
        if next_instruction == UP and obstacle.centery < player_rect.centery:
            if player_rect.left < obstacle.right and player_rect.right > obstacle.left:
                return True
        elif next_instruction == DOWN and obstacle.centery > player_rect.centery:
            if player_rect.left < obstacle.right and player_rect.right > obstacle.left:
                return True
        elif next_instruction == RIGHT and obstacle.centerx > player_rect.centerx:
            if player_rect.bottom > obstacle.top and player_rect.top < obstacle.bottom:
                return True
        elif next_instruction == LEFT and obstacle.centerx < player_rect.centerx:
            if player_rect.bottom > obstacle.top and player_rect.top < obstacle.bottom:
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
