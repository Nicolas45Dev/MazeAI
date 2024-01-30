# Simple interactive dungeon crawler
# This code was written for the AI courses in computer engineering at Université de Sherbrooke
# Author : Audrey Corbeil Therrien

from Games2D import *
from AIEngine import AIEngine

if __name__ == '__main__':
    # Niveau 0 - sans obstacle - 'assets/Mazes/mazeMedium_0'
    # Niveau 1 - avec obstacles - 'assets/Mazes/mazeMedium_1'
    # Niveau 2 - avec obstacles, portes et un ennemi - 'assets/Mazes/mazeMedium_2'
    # Niveau 2 - avec obstacles, portes et plusieurs ennemis - 'assets/Mazes/mazeMedium_3'

    #theAPP = App('assets/Mazes/mazeMedium_3')
    #theAPP = App('assets/Mazes/mazeLarge_0')
    #theAPP = App('assets/Mazes/mazeLarge_1')
    #theAPP = App('assets/Mazes/MazeLarge_2')
    theAPP = App('assets/Mazes/MazeLarge_3')
    #theAPP = App('assets/Mazes/mazeTest_0')
    theAPP.on_execute()



