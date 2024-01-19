from Constants import *
import numpy as np
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
import networkx as nx
import matplotlib.pyplot as plt


# This class will read the maze map transform the map into a graph and then search for the best route to solve it
class MazeSolver:

    def __init__(self, mazeFile):
        self.maze_file = mazeFile
        self.transforMazeToGraph()

    # This method will transform the maze into a graph
    def transforMazeToGraph(self):
        # read the maze file and transform it into a matrix
        file = open(self.maze_file, "r")
        maze = []
        for line in file:
            line = line.replace("\n", "")
            line = line.split(",")
            maze.append(line)
        self.graph_maze = self.createMazeGraph(maze)

    def createMazeGraph(self, maze):
        rows, cols = (len(maze), len(maze[0]))
        graph_maze = nx.Graph()

        for i in range(rows):
            for j in range(cols):
                cell_types = maze[i][j]

                # Check if the cell is a wall or a floor
                if cell_types in IMPENETRABLE_OBSTACLE:
                    continue

                # Connect adjacent cells with weights
                neighbors = [(i - 1, j), (i + 1, j), (i, j - 1), (i, j + 1)]
                for neighbor in neighbors:
                    ni, nj = neighbor
                    if 0 <= ni < rows and 0 <= nj < cols and maze[ni][nj] not in IMPENETRABLE_OBSTACLE:
                        weight = 5

                        if maze[ni][nj] in EXIT_OBJ:
                            weight = 5

                        # Decrease weight if coin or treasure is encountered
                        if maze[ni][nj] in ADDING_ATTRIBUTES:
                            weight = 2

                        # Increase weight if obstacle or monster is encountered
                        if maze[ni][nj] in SLOWING_OBSTACLE:
                            weight = 7

                        graph_maze.add_edge((i, j), (ni, nj), weight=weight)

        return graph_maze

    def getMazeGraph(self):
        return self.graph_maze

    def getShortestPath(self, start, end):
        return nx.shortest_path(self.graph_maze, start, end)