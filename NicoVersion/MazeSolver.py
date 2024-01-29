from Constants import *

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
        self.getStartAndExit()

    def getStartAndExit(self):
        rows = len(self.maze)
        cols = len(self.maze[0])

        for r in range(rows):
            for c in range(cols):
                if self.maze[r][c] == START:
                    self.start = (r, c)

                if self.maze[r][c] == EXIT:
                    self.exit = (r, c)

    def computePath(self):
        """Returns a list of tuples as a path from the given start to the given end in the given maze"""

        # Create start and end node
        start_node = Node(None, self.start)
        start_node.g = start_node.h = start_node.f = 0
        exit_node = Node(None, self.exit)
        exit_node.g = exit_node.h = exit_node.f = 0

        # Initialize both open and closed list
        open_list = []
        closed_list = []

        # Add the start node
        open_list.append(start_node)

        # Loop until you find the end
        while len(open_list) > 0:

            # Get the current node
            current_node = open_list[0]
            current_index = 0
            for index, item in enumerate(open_list):
                #print(item.position)
                if item.f < current_node.f:
                    current_node = item
                    current_index = index

            # Pop current off open list, add to closed list
            open_list.pop(current_index)
            closed_list.append(current_node)

            # Found the goal
            if current_node == exit_node:
                path = []
                current = current_node
                while current is not None:
                    path.append(current.position)
                    current = current.parent
                return path[::-1] # Return path in reverse

            # Generate children
            children = []
            #for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1, -1), (-1, 1), (1, -1), (1, 1)]:  # Adjacent squares
            for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]:  # Adjacent squares

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
                if self.maze[node_position[0]][node_position[1]] in WALL:
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

                # Child is on the closed list
                for closed_child in closed_list:
                    if child == closed_child:
                        continue

                # Create the f, g, and h values
                child.g = current_node.g + 1
                child.h = ((child.position[0] - exit_node.position[0]) ** 2) + (
                            (child.position[1] - exit_node.position[1]) ** 2)
                child.f = child.g + child.h

                # Child is already in the open list
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        continue

                # Add the child to the open list
                open_list.append(child)