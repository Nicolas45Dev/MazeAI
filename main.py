# Simple interactive dungeon crawler
# This code was written for the AI courses in computer engineering at Université de Sherbrooke
# Author : Audrey Corbeil Therrien

from Games2D import *
from AIEngine import AIEngine

if __name__ == '__main__':
    # Niveau 0 - sans obstacle - 'assets/Mazes/mazeMedium_0'
    # Niveau 1 - avec obstacles - 'assets/Mazes/mazeMedium_1'
    # Niveau 2 - avec obstacles, portes et un ennemi - 'assets/Mazes/mazeMedium_2'
    # Niveau 2 - avec obstacles, portes et plusieurs ennemis - 'assets/Mazes/mazeMedium_2'

    maze_file = 'assets/Mazes/mazeMedium_1'

    theAPP = App(maze_file)
    player_zero = AIEngine(theAPP.player, "Jacques", maze_file, theAPP.maze)
    theAPP.on_execute(player_zero)


