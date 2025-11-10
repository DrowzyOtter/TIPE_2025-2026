from random import random,gauss
from math import sin,sqrt,log,exp

nb_individu = 20 # il serait peut-être interessant de faire varier cette valeur au cours de l'algorithme : phase de recherche = + d'indiv
#génération = 0
population = [] # un tableau semble le mieux (mais à voir)
abscisse_minimale = -10
abscisse_maximale = 20
ordonnée_minimale = -15
ordonnée_maximale = 15

def distrib_uniforme (inf,sup) :
    return (sup-inf)*random() + inf
def distrib_gaussienne_centrée_tronquée (inf,sup,k) : #sur l'intervalle [mu - k*sigma ; mu + k*sigma]
    mu = (inf + sup)/2
    sigma = (sup - inf)/(2*k)
    X = gauss(mu,sigma)
    while abs(X-mu) > k*sigma : #pas optimal surtout si k petit
        X = gauss(mu,sigma)
    return X

def distrib_gaussienne_tronquée (inf,sup,mu,sigma_relatif) : # un calcul d'intégrale permetterait d'avoir un équivalent du k
    sigma = sigma_relatif * (sup - inf) #chercher la justification de cette dépendance linéaire
    X = gauss(mu,sigma)
    while X < inf or X > sup :
        X = gauss(mu,sigma)
    return X

###création de la population de départ
def création_pop () :
    population = []
    for _ in range (nb_individu) :
        population.append((distrib_uniforme(abscisse_minimale,abscisse_maximale),distrib_uniforme(ordonnée_minimale,ordonnée_maximale)))
    return population
population = création_pop()

###fitness fonction
def sinuscardinal (x,y,x0,y0):
    return sin(sqrt((x-x0)**2 + (y-y0)**2))/sqrt((x-x0)**2 + (y-y0)**2)

def fitness(indiv : tuple):
    x,y = indiv
    return -5*sinuscardinal(x,y,0,0) - 4.999*sinuscardinal(x,y,10,0)

###évaluation : méthode 1 : tri de couple
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

def pop_et_coût_triés (population,coût_associé) :
    pop_triée = []
    coût_trié = []
    for i in range (len(coût_associé)) :
        coût,indice = coût_associé[i]
        pop_triée.append(population[indice])
        coût_trié.append(coût)
    return pop_triée,coût_trié

"""print(population)
print(evaluation_et_tri(population))"""

###évaluation : méthode 1 bis : tri de couple avec sort

###évaluation : méthode 2 : permutation de deux listes


###-------------------------------###
###         visualisation         ###
###-------------------------------###

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

def afficher (pop_triée,coût_trié) :
    maximum = max(coût_trié)
    minimum = min(coût_trié)
    for i in range (len(pop_triée)) :
        x,y = pop_triée[i]
        tx = 1-((coût_trié[i]-minimum) / (maximum-minimum))
        nv_point(x,y,tx)
def execution() :
    pop_triée,coût_trié = pop_et_coût_triés(population,evaluation_et_tri(population))
    afficher(pop_triée,coût_trié)
    print(pop_triée)
    for i in range(len(pop_triée)):
        print (pop_triée[i],coût_trié[i])
    return pop_triée,coût_trié

#pop_triée,coût_trié = execution()

moncanva.pack()
#fenêtre.mainloop()

###séléction (nouvelle génération)

répartition = [5,0,5,10] #pour l'instant en nombre d'individu
#serait mieux en taux mais attention  à ce qu'il n'y est pas de perte
#ex : int(33.33) = 33 ==> plus que 99 individus à la deuxième génération (donc dernière val pas ajouté à la liste : ce qui reste)

def pioche_parmi_un_intervalle (minimum,maximum,nb_a_pioché) : #l'intervalle est [ minimum ; maximum [
    intervalle = maximum - minimum
    piochés = []
    while len(piochés) < nb_a_pioché :
        X = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        if X not in piochés :
            piochés.append(X)
    return sorted(piochés) #ou utilisé sa propre fct de tri

def pioche_couple_parmi_un_intervalle (minimum,maximum,nb_a_pioché) : #l'intervalle est [ minimum ; maximum [
    intervalle = maximum - minimum
    piochés = []
    while len(piochés) < nb_a_pioché :
        X = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        Y = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        if (X,Y) not in piochés and (X != Y):
            piochés.append((X,Y))
    return sorted(piochés) #ou utilisé sa propre fct de tri

def séléction (pop_triée,coût_trié,sigma_mutation) :
    nv_population = pop_triée[:répartition[0]] #élitisme
    for X in pioche_parmi_un_intervalle(répartition[0],len(pop_triée),répartition[1]): #réplication
        nv_population.append(pop_triée(X))
    #jusqu'ici nv_pop est triée et les fitness scores sont déjà connus
    for (X,Y) in pioche_couple_parmi_un_intervalle(0,len(pop_triée),répartition[2]) : #croisement (on peut aussi changer pour (0,len(nv_population)))
        nv_population.append((pop_triée[X][0],pop_triée[Y][1])) #prend l'abscisse du premier, l'ordonnée du second
    for X in pioche_parmi_un_intervalle(0,len(pop_triée),répartition[3]): #mutation
        x,y = pop_triée[X]
        nv_x = distrib_gaussienne_tronquée (abscisse_minimale,abscisse_maximale,x,sigma_mutation) #sigma relatif est à changer au cours du temps
        nv_y = distrib_gaussienne_tronquée (ordonnée_minimale,ordonnée_maximale,y,sigma_mutation)
        nv_population.append((nv_x,nv_y))
    return nv_population

meilleur_score = []
score_moyen = []

def fonction_sigma_mutation (génération,nb_génération) : #il serait encore mieux de faire en fct de la vitesse de convergence
    #sigma = 0.5
    #sigma = 0.1 #plutot bien
    taux = génération/nb_génération
    #sigma = exp(-3.5*taux) #de 1 à 0,03
    sigma = exp(-5*taux) #de 1 à 0,006
    return sigma


def évolution (nb_génération) :
    global population #sinon UnboundLocalError mais évolution et exection pourraient être mieux recodées
    for génération in range(nb_génération):
        pop_triée,coût_trié = pop_et_coût_triés(population,evaluation_et_tri(population))
        meilleur_score.append(4.8+coût_trié[0])
        score_moyen.append(4.8+sum(coût_trié)/len(pop_triée))
        sigma_mutation = fonction_sigma_mutation(génération,nb_génération)
        population = séléction (pop_triée,coût_trié,sigma_mutation)

nb_génération = 100000

évolution(nb_génération)
pop_triée,coût_trié = execution()

import matplotlib.pyplot as plt
plt.plot(meilleur_score) #[i+1 for i in range(nb_génération)]
plt.plot(score_moyen) #brouillon d'echelle log : [log(i+1) for i in range(500)]
plt.xscale("log")
plt.yscale("log")
plt.show()

moncanva.pack()
fenêtre.mainloop()

#une fonction interessante à implémenter serait l'execution multiple de l'algorithme (avec peu de génération) permetant de déterminer quelle 
#liste "répartition" permet au mieux la convergence globale ou celle qui accélère le plus la convergence.

