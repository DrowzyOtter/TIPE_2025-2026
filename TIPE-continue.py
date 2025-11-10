from random import random,gauss
from math import sin,cos,sqrt,log,exp,pi

###foctions de distribution et tirage aléatoire 

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

###definition de la forme à parcourir (FAP)

fap = [(0,0)]

###generateur à points équidistants par liste d'angles (modèle 1)

Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant la FAP
dx = 1

def angles_a_forme (Langles,dx) :
    x , y = 0 , 0
    fap = [(x,y)]
    orientation = 0
    for angle in Langles :
        orientation += angle
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap
#print(angles_a_forme(Lex1,2))

###test de présence par definition parametrique de la foret

###cas simplifié : rectangle suivant la grille
foret_rec_ex1= (-2,2,-6,6) # tuple des coordonnées x1, x2, y1 et y2

def est_dans_la_foret_rec (foret_rec,x,y) :
    x1,x2,y1,y2 = foret_rec
    return (x1 <= x <= x2) and (y1 <= y <= y2)

def placement_initial_possible (foret_rec) : #méthode matrice rota (rota du chemin)
    x1,x2,y1,y2 = foret_rec
    orientation = random.uniform(-180, 180)
    x , y = random.uniform(x1 , x2) , random.uniform(y1 , y2)
    return x , y , orientation




###execution
