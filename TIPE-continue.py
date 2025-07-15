from math import *

import random

###definition de la forme à parcourir (FAP)

fap = [(0,0)]

###generateur de forme

''' generateur "isodistant" par liste d'angles'''
Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant la FAP
dist = 1

def angles_a_forme (Langles,dist) :
    x , y = 0 , 0
    fap = [(x,y)]
    orientation = 0
    for angle in Langles :
        orientation += angle
        x , y = x + sin(orientation*pi/180) , y + cos(orientation*pi/180)
        fap.append((x,y))
    return fap

###test de présence et placement par definition parametrique de la foret foret

'''cas simplifié : rectangle suivant la grille'''
foret_rec_ex1= (-2,2,-6,6) # tuple des coordonnées x1, x2, y1 et y2

def est_dans_la_foret_rec (foret_rec,x,y) :
    x1,x2,y1,y2 = foret_rec
    return (x1 <= x <= x2) and (y1 <= y <= y2)

def placement_initial_possible (foret_rec) :
    x1,x2,y1,y2 = foret_rec
    orientation = random.uniform(-180, 180)
    x , y = random.uniform(x1 , x2) , random.uniform(y1 , y2)
    return x , y , orientation




###execution

print(angles_a_forme (Lex1,dist))
