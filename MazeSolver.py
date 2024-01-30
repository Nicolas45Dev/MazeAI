from Constants import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import heapq

class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

    def __lt__(self, other):
        return self.f < other.f

    def passedBy(self, position):
        if self.position == position:
            return True
        elif self.parent and self.parent.passedBy(position):
            return True
        return False



class MazeSolver():
    def __init__(self, maze):
        self.maze = maze
        self.start = None
        self.exit = None
        self.findStartAndExit()

    def findStartAndExit(self):
        rows = len(self.maze)
        cols = len(self.maze[0])

        for r in range(rows):
            for c in range(cols):
                if self.maze[r][c] == START:
                    self.start = (r, c)
                if self.maze[r][c] == EXIT:
                    self.exit = (r, c)

    def setStart(self, y, x):
        self.start = (y, x)

    def setExit(self, y, x):
        self.exit = (y, x)

    def computePath(self):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        # Create start and end node
        start_node = Node(None, self.start)
        start_node.g = start_node.h = start_node.f = 0
        exit_node = Node(None, self.exit)
        exit_node.g = exit_node.h = exit_node.f = 0

        open_list = []
        heapq.heappush(open_list, (0, start_node))  # Use a heap queue (priority queue)
        # Initialize both open and closed list

        closed_list = set()

        counter = 0

        # Add the start node
        #open_list.append(start_node)

        # Loop until you find the end
        while len(open_list) > 0:
            #print("-----------------------------------------------------")
            # Get the current node
            current_node = heapq.heappop(open_list)[1]

            if counter % 50 == 1:
                print(closed_list)
                #self.plot_explored_nodes(closed_list)

            # Found the goal
            if current_node == exit_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent

                self.plot_explored_nodes(closed_list, path[::-1])
                return path[::-1] # Return path in reverse

            closed_list.add(current_node.position)

            # Generate children
            children = []
            #for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Adjacent squares (8 directions)
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares (4 directions)

                # Get node position
                node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

                #print(current_node.position," -> ",node_position)

                # Make sure within row range
                if node_position[0] < 0 or node_position[0] > (len(self.maze) - 1):
                    continue

                # Make sure within column range
                if node_position[1] < 0 or node_position[1] > (len(self.maze[0]) - 1):
                    continue

                # Make sure walkable terrain
                if self.maze[node_position[0]][node_position[1]] == WALL:
                    continue

                # Make sure node isn`t a parent
                if current_node.passedBy(node_position):
                    continue

                # Create new node
                new_node = Node(current_node, node_position)

                # Append
                children.append(new_node)

            # Loop through children
            for child in children:

                if child.position in closed_list:
                    continue

                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - exit_node.position[0]) ** 2) + (
                            (child.position[1] - exit_node.position[1]) ** 2)
                child.f = child.g + child.h

                for node in open_list:
                    if node[1].position == child.position and node[1].g <= child.g:
                        continue


                # Add the child to the open list
                heapq.heappush(open_list, (child.f, child))

            counter += 1

    def plot_explored_nodes(self, nodes, path=None):
        fig, ax = plt.subplots()

        # Plot explored nodes
        #positions = []
        #for i, node in enumerate(nodes):
        #    positions.append(node[1].position)

        y, x = zip(*nodes)
        ax.scatter(x, y, marker='o', color='blue')

        # Plot the path if it exists
        if path:
            path_y, path_x = zip(*path)
            ax.plot(path_x, path_y, color='red', linewidth=2)

        # Plot walls
        if hasattr(self.maze, 'wallList'):
            for wall in self.maze.wallList:
                rect = patches.Rectangle((wall.x, wall.y), wall.width, wall.height, linewidth=1,
                                         edgecolor='red',
                                         facecolor='none')
                ax.add_patch(rect)
        if hasattr(self.maze, 'obstacleList'):
            for obstacle in self.maze.obstacleList:
                rect = patches.Rectangle((obstacle.x, obstacle.y), obstacle.width, obstacle.height,
                                         linewidth=1,
                                         edgecolor='green',
                                         facecolor='none')
                ax.add_patch(rect)

        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Explored Nodes and Path in A* Algorithm')
        plt.gca().invert_yaxis()
        ax.legend(['Explored nodes', 'Shortest path'])
        plt.show()