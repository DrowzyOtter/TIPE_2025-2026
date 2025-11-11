from random import random,gauss
from math import sin,cos,tan,sqrt,log,exp,pi

#region : foctions de distribution et tirage aléatoire 

def distrib_uniforme (inf,sup) :
    return (sup-inf)*random() + inf
def liste_équirépartie (a,b,nb) :
    return [a + (b-a)*k/(nb-1) for k in range (nb)]
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

# endregion
###generateur à points équidistants par liste d'angles (modèle 1)
"""varables"""
nb_individu = 20
dx = 1
nb_segment = 5
nb_génération = 100
génération_actuelle = 0
répartition = [5,0,5,10]

"""variables de test"""
Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant un individu

###création de la population de départ
def création_pop (nb_individu,nb_segment) :
    population = []
    for _ in range (nb_individu) :
        population.append([distrib_uniforme(-180,180) for _ in range (nb_segment)])
    return population

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


###-------------------------------###
###       fitness fonction        ###
###-------------------------------###

###test de présence et vecteur de départ avec une definition parametrique de la foret
#region : cas simplifié : rectangle suivant la grille
foret_rec_ex1= (-2,2,-6,6) # tuple des coordonnées x1, x2, y1 et y2

def est_dans_la_foret_rec (foret_rec,x,y) :
    x1,x2,y1,y2 = foret_rec
    return (x1 <= x <= x2) and (y1 <= y <= y2)

def placement_initial_possible (foret_rec) : #méthode matrice rota (rota du chemin)
    x1,x2,y1,y2 = foret_rec
    orientation = distrib_uniforme(-180, 180)
    x , y = distrib_uniforme(x1 , x2) , distrib_uniforme(y1 , y2)
    return x , y , orientation

#endregion
#region : cas de Zalgaller : bande infini (de largeur L)
Lforet = 10

def vecteur_de_départ_Zalgaller (Lforet) :
    orientation = distrib_uniforme(-180, 180)
    x0 = distrib_uniforme(-Lforet/2,Lforet/2 )
    return (x0, orientation)

def appartenance_Zalgaller (Lforet, x0, orientation, x, y) :
    if orientation % 180 == 0 :
        return -Lforet/2 <= x <= Lforet/2
    else :
        orientation_radian = orientation * pi /180
        pente = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y <= pente * x - (x0 - Lforet / 2) / sin(orientation_radian)
        bool2 = y >= pente * x - (x0 + Lforet / 2) / sin(orientation_radian)
        return (bool1 and bool2) or (not bool1 and not bool2) #on ne pense pas tout de suite au second cas

#endregion
###évaluation d'un individu (Z)
def création_positions_évaluées_aléatoires (nb_positions_évaluées,Lforet) :
    positions_évaluées = []
    for _ in range (nb_positions_évaluées) : 
        positions_évaluées.append(vecteur_de_départ_Zalgaller(Lforet))
    return positions_évaluées

def création_positions_évaluées_équiréparti (nb_x0,nb_orientations,Lforet) :
    x0_évalués = liste_équirépartie(-Lforet/2+0.05,Lforet/2-0.05,nb_x0)
    orientations_évaluées = liste_équirépartie(-179,179,nb_orientations)
    return x0_évalués, orientations_évaluées

def fitness (individu,dx) :
    nb_x0 = 10
    nb_orientations = 6
    #x_ind , y_ind = angles_a_forme(individu,dx)
    score = nb_x0 * nb_orientations
    x0_évalués, orientations_évaluées = création_positions_évaluées_équiréparti (nb_x0,nb_orientations,Lforet)
    for x0 in x0_évalués :
        for orientation in orientations_évaluées :
            inside = []
            for x,y in angles_a_forme(individu,dx) :
                inside.append(appartenance_Zalgaller(Lforet,x0,orientation,x,y))
            if False in inside :
                score -= 1
    return score

###méthode 1 bis : tri du couple (f.score,indiv)
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


def évaluation_et_tri (population,dx):
    coût_associé = []
    for individu in range(len(population)) :
        coût_associé.append((fitness(individu,dx),individu))
    return tri_fusion(coût_associé)

def couples_à_listes (couples) :
    pop_triée =[]
    coût_trié = []
    for coût,individu in couples :
        pop_triée.append(individu)
        coût_trié.append(coût)
    return pop_triée, coût_trié


def séléction (pop_triée,coût_trié,sigma_mutation) :
    nv_population = pop_triée[:répartition[0]] #élitisme
    for X in pioche_parmi_un_intervalle(répartition[0],len(pop_triée),répartition[1]): #réplication
        nv_population.append(pop_triée(X))
    #jusqu'ici nv_pop est triée et les fitness scores sont déjà connus
    for (X,Y) in pioche_couple_parmi_un_intervalle(0,len(pop_triée),répartition[2]) : #croisement (on peut aussi changer pour (0,len(nv_population)))
        nv_population.append(pop_triée[X][:3] + pop_triée[X][3:])
    for X in pioche_parmi_un_intervalle(0,len(pop_triée),répartition[3]): #mutation
        indivdu = pop_triée[X]
        for angle in indivdu :
            angle = distrib_gaussienne_tronquée(-180,180,angle,sigma_mutation) #sigma relatif est à changer au cours du temps
        nv_population.append(indivdu)
    return nv_population

###execution
"""for _ in range (30):
    x0 , orientation = vecteur_de_départ_Zalgaller (Lforet)
    x , y = distrib_uniforme(-5 , 5) , distrib_uniforme(-5 , 5)
    print(x,y,x**2+y**2<=25,orientation,appartenance_Zalgaller(Lforet,0,orientation,x,y))
    print()"""
"""print(appartenance_Zalgaller(Lforet,0,-97,-2.05,-2.42))
print(sin(pi/2))"""


population = création_pop(nb_individu,nb_segment)
print(population)
pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx))
print(pop_triée, coût_trié)
