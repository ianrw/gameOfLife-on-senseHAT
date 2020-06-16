#!/usr/bin/python3
import time
from sense_hat import SenseHat
from time import sleep
from copy import deepcopy
from sys import exit, stdin

"""Game of life on Raspberry Pi senseHAT LEDs"""
# ianrw  2020 Jun 11
# John Conway's Game of Life on a nxn map of cells where n>=8.
# The initial 8x8 cells chosen from a set of possibilities.
# The other cells, bordering the 8x8 cells, are all initially dead.
# Each successive generation is calculated on the map
# and the innermost 8x8 cells are then displayed on the LEDs.

sense = SenseHat()

RN = 12         # map of cells is RN x RN (range)
ET = 8          # 8x8 inner map for display on LEDs
BD = (RN-ET)//2 # width of border round inner map
DELAY = 0.5     # sleep between each display
LONGDELAY = 2   # sleep after new start
MAXGEN = 150    # maximum number of generations before exiting

# define choice of colours of pixels (not all are used)
d = (0, 0, 0)         # dark -- all colours off = dead cell
r = (255, 0, 0)       # red
y = (255, 255, 0)     # yellow
g = (0, 255, 0)       # green
b = (0, 0, 255)       # blue
w = (255, 255, 255)   # white
c = g                 # colour of live cell

pixi = []   #  list of possible starting maps

# a selection of starting maps (more may be added):-
# toad and 2 blinkers
pix_init1 = [d, d, d, d, d, d, d, d,
             d, c, c, c, d, d, d, d,
             c, c, c, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, c, d, d, d, d, d, d,
             d, c, d, d, d, c, c, c,
             d, c, d, d, d, d, d, d]
pixi.append(pix_init1)

# glider
pix_init2 = [d, c, d, d, d, d, d, d,
             d, d, c, d, d, d, d, d,
             c, c, c, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d]
pixi.append(pix_init2)

# small spaceship
pix_init3 = [d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             c, d, d, c, d, d, d, d,
             d, d, d, d, c, d, d, d,
             c, d, d, d, c, d, d, d,
             d, c, c, c, c, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d]
pixi.append(pix_init3)

# beacon and 2 blinkers (clash)
pix_init4 = [c, c, d, d, d, d, d, d,
             c, d, d, d, d, c, c, c,
             d, d, d, c, d, d, d, d,
             d, d, c, c, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, c, c, c,
             d, d, d, d, d, d, d, d]
pixi.append(pix_init4)

# beacon and 1 blinker (no clash)
pix_init5 = [c, c, d, d, d, d, d, d,
             c, d, d, d, d, d, d, d,
             d, d, d, c, d, d, d, d,
             d, d, c, c, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, d, d, d,
             d, d, d, d, d, c, c, c,
             d, d, d, d, d, d, d, d]
pixi.append(pix_init5)

n_init = str(len(pixi))
sense.show_message("  Game of Life", text_colour=r)
text = "Enter number 1 to " + n_init
sense.show_message(text,text_colour=y)
print("Enter a number (1 upto "+ n_init +") on the keyboard")

i = int(stdin.read(1))
if i>=1 and i<=5:
    p = int(i)-1
else:
    p = 0
pix_init = pixi[p]
print("Starting with map ",p+1)

# define and display initial 8x8 map of cells
pix_disp = deepcopy(pix_init)   # for initial display
sense.set_pixels(pix_disp)
sleep(LONGDELAY)        # long wait after initial display

gen = 0     # generation counter

# initialize map_old: it will hold current generation of cells
map_old = [d]
z = RN*RN-1
for i in range(z):
    map_old.append(d)
    
# amend map_old to include inner 8x8 cells starting map pix_init
for Y in range(ET):
    for X in range(ET):
       x = X+BD
       y = Y+BD
       map_old[x + RN*y] = pix_init[X + ET*Y]
    
# initialize map_new as store to hold next generation of cells
map_new = [d]
z = RN*RN-1
for i in range(z):
    map_new.append(d)

# calculate new display according to these rules:
# Loneliness:   A living cell with 0 or 1 live neighbours dies
# Overcrowding: A living cell with more than 3 live neighbours dies
# Stasis:       A living cell with 2 or 3 live neighbours survives
# Stasis:       A dead cell with less than or more than 3 neighbours stays dead
# Reproduction: A dead cell with 3 live neighbours comes to life

# calculate life or death of each cell in the new generation
def cell(X, Y):
    if map_old[X + RN*Y] == d:
        cell_state = 0
    else:    
        cell_state = 1
    nbrs = 0                        # count of live nearest neighbours
    for x in range(X-1, X+2):
        for y in range(Y-1, Y+2):
            if (x<0) or (x>=RN):    #  outside RN x RN map
                continue
            if (y<0) or (y>=RN):    #  outside RN x RN map
                continue
            if (x==X) and (y==Y):
                continue            # exclude the cell itself
            if map_old[x + RN*y] != d:    # neighbour is alive
                nbrs += 1           # increment number of live neighbours
    if cell_state == 0:             # cell is originally dead
        if nbrs == 3:
            cell_state = 1          # Reproduction: cell comes to life
    else:        
        if nbrs > 3:
            cell_state = 0          # Overcrowding: cell dies
        if nbrs < 2:
            cell_state = 0          # Loneliness: cell dies
    return cell_state

while True:
    # update cell states in map_new (keeping old values in pix_disp)
    gen += 1
    print('Generation',gen)
    if gen > MAXGEN:
        print("Over "+ str(MAXGEN) +" generations. \nGoodbye")
        sense.clear()
        sense.show_message("Goodbye!",text_colour=r)
        exit()
    for y in range(RN):
        for x in range(RN):
            if cell(x,y) == 0:
                col = d
            else:
                col = c
            map_new[x + RN*y] = col
    # copy new states to update display matrix
    alive = False  # to check whether all displayed cells are dead
    for x in range(ET):
        for y in range(ET):
            z = x + ET*y
            pix_disp[z] = map_new[x+BD + RN*(y+BD)]
            if pix_disp[z] != d:
                alive = True
    if alive == False:
        print('All displayed cells are now dead.')
        sense.clear() # Clear display of cells brought to life by border cells
        for x in range(RN):
            for y in range(RN):
                if map_new[x + RN*y] != d:
                    print('live cell in border at x,y=',x,y)
        print('Goodbye!')
        sense.show_message("Goodbye!",text_colour=r)
        exit()
    sense.set_pixels(pix_disp)
    map_old = deepcopy(map_new)
    sleep(DELAY)               # wait after displaying

    
     



