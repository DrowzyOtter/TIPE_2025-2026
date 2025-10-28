from random import random
from math import sin,sqrt

nb_individu = 10 # il serait peut-être interessant de faire varier cette valeur au cours de l'algorithme : phase de recherche = + d'indiv
génération = 0
population = [] # un tableau semble le mieux (mais à voir)

###création de la population de départ

def distrib_aléa (inf,sup) :
    return (sup-inf)*random() + inf

for _ in range (nb_individu) :
    population.append((distrib_aléa(-10,20),distrib_aléa(-15,15)))

###fitness fonction
def sinuscardinal (x,y,x0,y0):
    return sin(sqrt((x-x0)**2 + (y-y0)**2))/sqrt((x-x0)**2 + (y-y0)**2)

def fitness(indiv : tuple):
    x,y = indiv
    return -5*sinuscardinal(x,y,0,0) - 4*sinuscardinal(x,y,10,0)

###évaluation (tri)

"""indice_associé = {}
coûts = []
for i in range(population) :
    coût = fitness(indiv)
    if coût in indice_associé :
        indiv_associé[coût] = i"""
"""def fusion (c1,c2) :
    if c1 != [] and c2 != [] :
        if c1[0] > c2[0] :
            return 
    elif c1 == [] : [c1[0]] + []
        return c2
    else :
        return c1"""

def fusion (c1,c2) :
    n1 = len(c1)
    n2 = len(c2)
    i1 = 0
    i2 = 0
    triée = []
    while i1 < n1 and i2 < n2 :
        if c1[i1] < c2[i2] :
            triée.append(c1[i1])
            i1 += 1
        else :
            triée.append(c2[i2])
            i2 += 1
    if i1 == n1 :
        triée += c2[i2:n2]
    else :
        triée += c1[i1:n1]
    return triée

def séparation (c) :
    c1,c2 = [],[]
    for i in range (len(c)):
        if i%2 == 0 :
            c1.append(c[i])
        else :
            c2.append(c[i])
    return c1,c2

def tri_fusion (couples) :
    if len(couples) < 2 :
        return couples
    else :
        c1,c2 = séparation (couples)
        return fusion (tri_fusion(c1),tri_fusion(c2))

"""print(tri_fusion([(56,1),(38,2),(86,3),(95,4),(55,5),(23,6),(67,7)]))"""

def evaluation_et_tri (population):
    coût_associé = []
    for i in range(len(population)) :
        coût_associé.append((fitness(population[i]),i))
    return tri_fusion(coût_associé)

def ordre (coût_associé) :
    ordre = []
    for i in range (len(coût_associé)) :
        coût,indice = coût_associé[i]
        ordre.append(indice)
    return ordre

print(population)
print(evaluation_et_tri(population))

###visualisation

from tkinter import *
# Création de la fenêtre principale
hauteur = 600
largeur = 600
fenêtre = Tk()
fenêtre.title("Population sur la fonction de coût")
fenêtre.geometry("600x600")
# Chargement de l'image
photo = PhotoImage(file="plan_de_coupe_réajusté-bis.png")
"""lbl = Label(fenêtre,image=photo)
lbl.pack()"""

#moncanva = Canvas(fenêtre)
moncanva = Canvas(fenêtre,width=largeur,height=hauteur)

moncanva.photo = photo

moncanva.create_image(0,0,anchor="nw",image=photo)
#moncanva.create_image(largeur/2,hauteur/2,anchor="center",image=photo)

def gradient_color(t):
    """
    Renvoie la couleur hexadécimale correspondant à t ∈ [0, 1].
    """
    # Points du gradient
    A = (20, 110, 145)
    B = (87, 199, 133)
    C = (237, 221, 83)

    if t <= 0.67:
        u = t / 0.67
        r = A[0] + u * (B[0] - A[0])
        g = A[1] + u * (B[1] - A[1])
        b = A[2] + u * (B[2] - A[2])
    else:
        u = (t - 0.67) / (1 - 0.67)
        r = B[0] + u * (C[0] - B[0])
        g = B[1] + u * (C[1] - B[1])
        b = B[2] + u * (C[2] - B[2])

    return f"#{int(r):02x}{int(g):02x}{int(b):02x}"

def convertisseur_affine_x (x) :
    return (544-15)/(20+10)*(x+10) + 15
def convertisseur_affine_y (y) :
    return (65-595)/(15+15)*(y+15) + 595

def nv_point (x,y,tx):
    R = 5
    X = convertisseur_affine_x(x)
    Y = convertisseur_affine_y(y)
    return moncanva.create_oval(X-R,Y-R,X+R,Y+R,fill=gradient_color(tx))

#moncanva.create_oval(100,100,200,200,fill="red")

#for i in range (len(population)) :

nv_point(0,0,0.5)
nv_point(3,-2,1)

moncanva.pack()
fenêtre.mainloop()