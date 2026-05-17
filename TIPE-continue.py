from random import random,gauss
from math import sin,cos,tan,sqrt,log,exp,pi

#region : foctions de distribution et tirage aléatoire 

def distrib_uniforme (inf,sup) :
    return (sup-inf)*random() + inf
def liste_équirépartie (a,b,nb) :
    if nb == 1 :
        return [(a+b)/2]
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
    compteur = 0
    while len(piochés) < nb_a_pioché and compteur < nb_a_pioché * 100 :
        X = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        if X not in piochés :
            piochés.append(X)
        compteur += 1
    if len(piochés) < nb_a_pioché :
        raise Exception("Trop peu d'éléments uniques piochés, augmenter l'intervalle ou diminuer le nombre à piocher")
    return sorted(piochés) #ou utilisé sa propre fct de tri

def pioche_couple_parmi_un_intervalle (minimum,maximum,nb_a_pioché) : #l'intervalle est [ minimum ; maximum [
    intervalle = maximum - minimum
    piochés = []
    compteur = 0
    while len(piochés) < nb_a_pioché and compteur < nb_a_pioché * 100 :
        X = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        Y = minimum + int(abs(distrib_gaussienne_centrée_tronquée (-intervalle,intervalle,2)))
        if (X,Y) not in piochés and (X != Y):
            piochés.append((X,Y))
        compteur += 1
    if len(piochés) < nb_a_pioché :
        raise Exception("Trop peu d'éléments uniques piochés, augmenter l'intervalle ou diminuer le nombre à piocher")
    return sorted(piochés) #ou utilisé sa propre fct de tri

# endregion
###generateur à points équidistants par liste d'angles (modèle 1)
"""varables"""
nb_individu = 60
Lforet = 10 #largeur de la foret pour Zalgaller, Isbell et rectangle
Hforet = 10 #hauteur de la foret pour rectangle
#nom_foret = "Isbell"
#nom_foret = "Zalgaller"
nom_foret = "rectangle"

#cas zalgaller : l0 = 2.278
#cas isbell : l0 = 6.3972/2 * distance à la frontière
#cas rectangle l0 2.0471 ?? sqrt(Lforet^2+Hforet^2)
nb_segment = 10
#dx = #longueur de chaque segment
dx = (sqrt(Lforet^2+Hforet^2) + 0.1)/nb_segment*Lforet


sigma_mutation = 0.005 * 3 #écart type relatif pour la mutation
nb_génération = 6
génération_actuelle = 0
répartition = [5,0,15,40] #élitisme, réplication, croisement, mutation
assert sum(répartition) == nb_individu

"""variables de test"""
Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant un individu

###création de la population de départ
def création_pop (nb_individu,nb_segment) :
    population = []
    for _ in range (nb_individu) :
        population.append([distrib_uniforme(-180,180) for _ in range (nb_segment)])
    return population

def angles_a_forme (Langles,dx) : #petite optimisation mais confusion : le 1er angle est inutile
    x , y = 0 , 0
    fap = [(x,y)]
    orientation = 0
    #print("Langles",Langles)
    for angle in Langles :
        orientation += angle
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap
#print(angles_a_forme(Lex1,2))
def angles_a_forme2 (Langles,dx) : #petite optimisation mais confusion : le 1er angle est inutile
    x , y = 0 , 0
    fap = [(x,y)]
    #print("Langles",Langles)
    for orientation in Langles :
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap


###-------------------------------###
###       fitness fonction        ###
###-------------------------------###

###test de présence et vecteur de départ avec une definition parametrique de la foret
#region : cas simplifié : rectangle (suivant la grille)
"""foret_rec= (-5,5,-5*3,5*3) # tuple des coordonnées x1, x2, y1 et y2

def vecteur_de_départ_rectangle () : #méthode matrice rota (rota du chemin)
    global foret_rec
    x1,x2,y1,y2 = foret_rec
    orientation = distrib_uniforme(-180, 180)
    x , y = distrib_uniforme(x1 , x2) , distrib_uniforme(y1 , y2)
    return x , y , orientation
"""

def appartenance_rectangle (x0,y0,orientation,x,y) :
    global Lforet
    global Hforet
    ε = 1e-10
    orientation_radian = orientation * pi /180
    if (sin(orientation_radian) < ε) : # Pour éviter les approximations dues aux flottants
        return ( - Lforet/2 <= x-x0 <= Lforet/2) and ( - Hforet/2 <= y-y0 <= Hforet/2)
    elif (cos(orientation_radian) < ε) :
        return ( - Hforet/2 <= x-x0 <= Hforet/2) and ( - Lforet/2 <= y-y0 <= Lforet/2)
    else :
        pente1 = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y - y0 <= pente1 * (x-x0) - (0 - Lforet / 2) / sin(orientation_radian)
        bool2 = y - y0 >= pente1 * (x-x0) - (0 + Lforet / 2) / sin(orientation_radian)
        pente2 = - tan(pi/2 - (orientation_radian + pi/2))
        bool3 = y - y0 >= pente2 * (x-x0) - (0 - Hforet / 2) / sin(orientation_radian + pi/2)
        bool4 = y - y0 >= pente2 * (x-x0) - (0 + Hforet / 2) / sin(orientation_radian + pi/2)
        return ((bool1 and bool2) or (not bool1 and not bool2)) and ((bool3 and bool4) or (not bool3 and not bool4))

#endregion
#region : cas de Zalgaller : bande infini (de largeur L)

"""def vecteur_de_départ_Zalgaller () : #-> (x0, orientation)
    global Lforet
    orientation = distrib_uniforme(-180, 180)
    x0 = distrib_uniforme(-Lforet/2,Lforet/2 )
    return (x0, orientation)"""

def positions_évaluées_équiréparti (para) : #-> liste de x0 , liste de y0, liste d'orientations
    nb_x0,nb_y0,nb_orientations = para
    global Lforet
    global Hforet
    ε = 1e-2
    x0_évalués = liste_équirépartie(-Lforet/2+ε,Lforet/2-ε,nb_x0)
    y0_évalués = liste_équirépartie(-Hforet/2+ε,Hforet/2-ε,nb_y0)
    #orientations_évaluées = liste_équirépartie(-360 * (1 - 1/nb_orientations/2),360 * (1 - 1/nb_orientations/2),nb_orientations) #/!\ à fixer
    orientations_évaluées = [(2*pi*k/nb_orientations - pi)/pi*180 for k in range (nb_orientations)]
    return x0_évalués, y0_évalués, orientations_évaluées

def appartenance_Zalgaller (x0, orientation, x, y) : #-> bool
    global Lforet
    ε = 1e-10
    if (abs(sin(orientation)) < ε) : # Pour éviter les approximations dues aux flottants
        return -Lforet/2 <= x <= Lforet/2
    else :
        orientation_radian = orientation * pi /180
        pente = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y <= pente * x - (x0 - Lforet / 2) / sin(orientation_radian)
        bool2 = y >= pente * x - (x0 + Lforet / 2) / sin(orientation_radian)
        return (bool1 and bool2) or (not bool1 and not bool2) #on ne pense pas tout de suite au second cas

#endregion
#region : cas de Isbell : demi-plan (dont la frontière est à une distance L)
"""
def vecteur_de_départ_Isbell () : #-> (x0, orientation)
    global Lforet
    orientation = distrib_uniforme(-180, 180)
    x0 = 0 #inutile
    return orientation
"""

def appartenance_Isbell (x0,orientation,x, y) : #-> bool
    global Lforet
    ε = 1e-5
    if abs(sin(orientation)) < ε : # Pour éviter les approximations dues aux flottants (or -180.1 < orientation < -179.9)
        #print("celui-la")
        return -Lforet/2 <= x <= Lforet/2
    else :
        orientation_radian = orientation * pi /180
        pente = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y <= pente * x + (Lforet / 2) / sin(orientation_radian)
        bool2 = sin(orientation_radian) > 0
        return (bool1 and bool2) or (not bool1 and not bool2)

#endregion
###évaluation d'un individu

def appartenance_foret (nom_foret,x0,y0,orientation,x,y) :
    if nom_foret == "Zalgaller" :
        return appartenance_Zalgaller(x0,orientation,x,y)
    elif nom_foret == "Isbell" :
        #print("isbell", x0, orientation, x, y, nom_foret)
        return appartenance_Isbell(x0,orientation,x,y)
    elif nom_foret == "rectangle" :
        return appartenance_rectangle(x0,y0,orientation,x,y)
    else :
        breakpoint("nom_foret doit être Zalgaller ou Isbell ou rectangle")

"""def création_positions_évaluées_aléatoires (nb_positions_évaluées,Lforet) : #-> liste de (x0,orientation)
    positions_évaluées = []
    for _ in range (nb_positions_évaluées) : 
        positions_évaluées.append(vecteur_de_départ_Zalgaller(Lforet))
    return positions_évaluées"""

def fitness (individu,dx,para_evaluation : list,nom_foret) : #-> score (nb entre 0 et nb_x0 * nb_orientations)
    #nb_segment = len(individu)
    global génération_actuelle
    xy_ind = angles_a_forme(individu,dx)
    score = para_evaluation[0] * para_evaluation[1] * para_evaluation[2] #part du pire score possible
    print("score max à la génération", génération_actuelle, ":", score)
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti (para_evaluation) #idiot de recalculer à chaque fois
    """
    for x0 in x0_évalués :
        for y0 in y0_évalués :
            for orientation in orientations_évaluées :
                dedans = []
                #for x,y in angles_a_forme(individu,dx) :
                for (x,y) in xy_ind :
                    if nom_foret == "Zalgaller" :
                        dedans.append(appartenance_Zalgaller(x0,orientation,x,y))
                    elif nom_foret == "Isbell" :
                        dedans.append(appartenance_Isbell(x0,orientation,x,y))
                    elif nom_foret == "rectangle" :
                        dedans.append(appartenance_rectangle(x0,y0,orientation,x,y))
                if False in dedans : #si au moins un segment est hors de la foret
                    score -= 1
    return score
    """    
    if nom_foret == "Zalgaller" :
        for x0 in x0_évalués :
            for orientation in orientations_évaluées :
                dedans = []
                for (x,y) in xy_ind :
                    dedans.append(appartenance_Zalgaller(x0,orientation,x,y))
                if False in dedans :
                    score -= 1
    elif nom_foret == "Isbell" :
        for x0 in x0_évalués :
            for orientation in orientations_évaluées :
                dedans = []
                for (x,y) in xy_ind :
                    dedans.append(appartenance_Isbell(x0,orientation,x,y))
                if False in dedans :
                    score -= 1
    elif nom_foret == "rectangle" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = []
                    for (x,y) in xy_ind :
                        dedans.append(appartenance_rectangle(x0,y0,orientation,x,y))
                    if False in dedans :
                        score -= 1
        print("score à la génération", génération_actuelle, ":", score)
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

#-------------------------------------------#

def évaluation_et_tri (population,dx,para_evaluation,nom_foret) : #-> liste de couples (fitness score,individu)
    coût_associé = []
    for individu in population :
        coût_associé.append((fitness(individu,dx,para_evaluation,nom_foret),individu))
    return sorted(coût_associé) #ou tri_fusion(coût_associé)

def couples_à_listes (couples) :
    pop_triée =[]
    coût_trié = []
    for coût,individu in couples :
        pop_triée.append(individu)
        coût_trié.append(coût)
    return pop_triée, coût_trié

def séléction (pop_triée,coût_trié,sigma_mutation) : #-> nouvelle population
    nv_population = pop_triée[:répartition[0]][:] #élitisme
    for X in pioche_parmi_un_intervalle(répartition[0],len(pop_triée),répartition[1]): #réplication
        nv_population.append(pop_triée[X])
    #jusqu'ici nv_pop est triée et les fitness scores sont déjà connus
    for (X,Y) in pioche_couple_parmi_un_intervalle(0,len(pop_triée),répartition[2]) : #croisement (on peut aussi changer pour (0,len(nv_population)))
        demi = len(pop_triée[X]) // 2
        nv_population.append(pop_triée[X][:demi] + pop_triée[Y][demi:])
    for X in pioche_parmi_un_intervalle(0,len(pop_triée),répartition[3]): #mutation
        indivdu = pop_triée[X][:]
        for i in range(len(indivdu)) :
            indivdu[i] = distrib_gaussienne_tronquée(-180,180,indivdu[i],sigma_mutation) #sigma relatif est à changer au cours du temps
        nv_population.append(indivdu)
    return nv_population

#region : test éxecution
###éxecution
"""for _ in range (30):
    x0 , orientation = vecteur_de_départ_Zalgaller ()
    x , y = distrib_uniforme(-5 , 5) , distrib_uniforme(-5 , 5)
    print(x,y,x**2+y**2<=25,orientation,appartenance_Zalgaller(0,orientation,x,y))
    print()"""
"""print(appartenance_Zalgaller(0,-97,-2.05,-2.42))
print(sin(pi/2))"""

#population = création_pop(nb_individu,nb_segment)
#print(population)
#print([x for x,y in angles_a_forme(population[0],dx)])
#pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx))
#print(coût_trié)
#endregion

###-------------------------------###
###         visualisation         ###
###-------------------------------###

from tkinter import *

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

# Création de la fenêtre principale
hauteur = 400*2
largeur = 600*2
fenêtre1 = Tk()
fenêtre1.title("évaluation du fitness score simplifiée")
fenêtre1.geometry("1126x900")
fenêtre1.configure(bg="#020618")
#moncanva = Canvas(fenêtre)
moncanva1 = Canvas(fenêtre1,width=largeur,height=hauteur, bg="#020618",borderwidth=0,highlightthickness=0)
moncanva1.place(relx=0.5, rely=0.5, anchor='center')
fenêtre1.update_idletasks()


def convertisseur_affine_x (x,canva) :
    #return (544-15)/(20+10)*(x+10) + 15
    #return x*largeur/(4*Lforet)
    largeur_canva = canva.winfo_width()
    return largeur_canva// 2 + x / (Lforet * 3.5) * largeur_canva
def convertisseur_affine_y (y,canva) :
    #return (65-595)/(15+15)*(y+15) + 595
    #return y*hauteur/(4*Lforet)
    hauteur_canva = canva.winfo_height()
    largeur_canva = canva.winfo_width()
    return hauteur_canva // 2 - y / (Lforet * 3.5) * largeur_canva

def nv_point (x,y,tx,canva):
    R = 4
    X = convertisseur_affine_x(x,canva)
    Y = convertisseur_affine_y(y,canva)
    return canva.create_oval(X-R,Y-R,X+R,Y+R,fill=gradient_color(tx))

def nv_ligne (x0,y0,x1,y1,tx,canva) :
    épaisseur = 2
    if tx == 2 :
        couleur = "white"
    else :
        couleur = gradient_color(tx)
    X0 = convertisseur_affine_x(x0,canva)
    Y0 = convertisseur_affine_y(y0,canva)
    X1 = convertisseur_affine_x(x1,canva)
    Y1 = convertisseur_affine_y(y1,canva)
    return canva.create_line(X0,Y0,X1,Y1,fill=couleur)
#moncanva.create_oval(100,100,200,200,fill="red")

def afficher_individu (individu,dx,x0,y0,inclinaison,tx) : #-> None
    xy_ind = angles_a_forme(individu,dx)
    for i in range (len(xy_ind)) :
        x , y = xy_ind[i]
        xy_ind[i] = x*cos(inclinaison*pi/180) - y*sin(inclinaison*pi/180) + x0 , x*sin(inclinaison*pi/180) + y*cos(inclinaison*pi/180) + y0 #matrice de rotation cachée
    for i in range (1,len(xy_ind)) :
        nv_ligne(xy_ind[i-1][0],xy_ind[i-1][1],xy_ind[i][0],xy_ind[i][1],tx,moncanva1)
    nv_point(x0,y0,tx,moncanva1)

def affichage_forme_unique (individu,dx) : #-> None
    hauteur = 400*2
    largeur = 600*2
    fenêtre2 = Tk()
    fenêtre2.title("évaluation du fitness score simplifiée")
    fenêtre2.geometry("1126x900")
    fenêtre2.configure(bg="#020618")
    moncanva2 = Canvas(fenêtre2,width=largeur,height=hauteur, bg="#020618",borderwidth=0,highlightthickness=0)
    moncanva2.place(relx=0.5, rely=0.5, anchor='center')
    fenêtre2.update_idletasks()
    individu[0] = 0 #pour orienter la forme
    xy_ind = angles_a_forme(individu,dx)
    #centrage :
    val_extrm = [0,0,0,0] #x_min,x_max,y_min,y_max
    for (x,y) in xy_ind :
        if x < val_extrm[0] :
            val_extrm[0] = x
        if x > val_extrm[1] :
            val_extrm[1] = x
        if y < val_extrm[2] :
            val_extrm[2] = y
        if y > val_extrm[3] :
            val_extrm[3] = y
    coef = 10*min(2.33 / (val_extrm[3]-val_extrm[2]), 3.5 / (val_extrm[1]-val_extrm[0]))*0.9 #0.9 pour la marge
    milieu_x = (val_extrm[0] + val_extrm[1]) / 2
    milieu_y = (val_extrm[2] + val_extrm[3]) / 2
    tx = 1
    for i in range (1,len(xy_ind)) :
        nv_ligne((xy_ind[i-1][0]-milieu_x)*coef,(xy_ind[i-1][1]-milieu_y)*coef,(xy_ind[i][0]-milieu_x)*coef,(xy_ind[i][1]-milieu_y)*coef,tx,moncanva2)
        nv_point((xy_ind[i-1][0]-milieu_x)*coef,(xy_ind[i-1][1]-milieu_y)*coef,tx,moncanva2)
        tx -= 1/(len(xy_ind)-1)
    #moncanva2.pack(expand=True)
    #fenêtre2.mainloop()

def fitness_affichage_z_or_i (individu,dx,nom_foret : str) : #-> None
    #nb_segment = len(individu)
    global Lforet
    global Hforet
    if nom_foret == "Zalgaller" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nv_ligne(-Lforet/2,-moncanva1.winfo_height()//2,-Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nb_x0 = 5
        nb_y0 = 1
        nb_orientations = 35
    elif nom_foret == "Isbell" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nb_x0 = 1
        nb_y0 = 1
        nb_orientations = 50
    elif nom_foret == "rectangle" :
        nv_ligne(Lforet/2,-Hforet/2,Lforet/2,Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,-Hforet/2,-Lforet/2,Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,-Hforet/2,Lforet/2,-Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,Hforet/2,Lforet/2,Hforet/2,2,moncanva1)
        nb_x0 = 3
        nb_y0 = 3
        nb_orientations = 5
    else :
        breakpoint("nom_foret doit être Zalgaller ou Isbell")
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti ([nb_x0,nb_y0,nb_orientations])
    tx = 0
    for x0 in x0_évalués :
        for y0 in y0_évalués :
            for orientation in orientations_évaluées :
                #if nom_foret == "Zalgaller" :
                #print(x0,orientation)
                afficher_individu (individu,dx,x0,y0,orientation,tx)
                tx += 1/(nb_x0*nb_y0*nb_orientations)
                print(tx,len(x0_évalués),len(y0_évalués),len(orientations_évaluées))

def fitness_affichage_z_or_i_2 (individu,dx,nom_foret : str) : #-> None
    global Lforet
    global Hforet
    if nom_foret == "Zalgaller" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nv_ligne(-Lforet/2,-moncanva1.winfo_height()//2,-Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nb_x0 = 5
        nb_y0 = 1
        nb_orientations = 35
    elif nom_foret == "Isbell" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1)
        nb_x0 = 1
        nb_y0 = 1
        nb_orientations = 50
    elif nom_foret == "rectangle" :
        nv_ligne(Lforet/2,-Hforet/2,Lforet/2,Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,-Hforet/2,-Lforet/2,Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,-Hforet/2,Lforet/2,-Hforet/2,2,moncanva1)
        nv_ligne(-Lforet/2,Hforet/2,Lforet/2,Hforet/2,2,moncanva1)
        nb_x0 = 3
        nb_y0 = 3
        nb_orientations = 5
    else :
        breakpoint("nom_foret doit être Zalgaller ou Isbell")
    xy_ind = angles_a_forme(individu,dx)
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti ([nb_x0,nb_y0,nb_orientations])
    if nom_foret == "Zalgaller" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = []
                    for (x,y) in xy_ind :
                        dedans.append(appartenance_Zalgaller(x0,orientation,x,y))
                    if False in dedans :
                        afficher_individu (individu,dx,x0,y0,-orientation,0) #/!\ on a - orientation car l'oriantation de la forme est inverse de celle de la foret
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,1)
                        #print ("x0 =", x0, "orientation =", orientation)
                        #print(dedans)
                        
    elif nom_foret == "Isbell" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = []
                    for (x,y) in xy_ind :
                        dedans.append(appartenance_Isbell(x0,orientation,x,y))
                    if False in dedans :
                        afficher_individu (individu,dx,x0,y0,-orientation,0)
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,1)
    elif nom_foret == "rectangle" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = []
                    for (x,y) in xy_ind :
                        dedans.append(appartenance_rectangle(x0,y0,orientation,x,y))
                    if False in dedans :
                        afficher_individu (individu,dx,x0,y0,-orientation,0)
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,1)


    

def fitness_lourde (individu,dx) : #pas d'optimisation computationnelle, juste pour le test final
    #nb_segment = len(individu)
    global nom_foret
    nb_x0 = 100
    nb_orientations = 100
    xy_ind = angles_a_forme(individu,dx)
    tx_moyen = 0
    score = 1
    nb_erreurs = nb_x0 * nb_orientations
    nb_segments_inutiles_total = 0
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti ([nb_x0,1,nb_orientations])
    for x0 in x0_évalués :
        for y0 in y0_évalués :
            for orientation in orientations_évaluées :
                dedans = []
                tx = 0
                #for x,y in angles_a_forme(individu,dx) :
                for (x,y) in xy_ind :
                    dedans.append(appartenance_foret(nom_foret,x0,y0,orientation,x,y))
                for val in dedans : #useless
                    tx += int(val)/len(dedans)
                for i in range(len(dedans)) :
                    if dedans[i] == False :
                        nb_segments_inutiles_total += len(dedans) - i #on compte les segments après la première sortie de la foret
                        nb_erreurs -= 1
                        break
                #if tx < 1 :
                #    score -= 1/(nb_x0 * nb_orientations)

                tx_moyen += tx/(nb_x0 * len(y0_évalués) * nb_orientations)
    if (nb_x0 * nb_orientations - nb_erreurs) > 0 : #dénombre les segments inutiles moyens parmi les essais réussis
        nb_segments_inutiles_moyen = nb_segments_inutiles_total / (nb_x0 * nb_orientations - nb_erreurs)
    else :
        nb_segments_inutiles_moyen = 0
    score = nb_erreurs / (nb_x0 * nb_orientations)
    return score*100, tx_moyen*100, nb_erreurs, nb_x0 * nb_orientations, nb_segments_inutiles_moyen


#fitness_affichage_z_or_i(pop_triée[0],dx,"Zalgaller")
#print (moncanva.winfo_width())

def éxecution (nb_individu,nb_génération,nb_segment,nom_foret) : #-> meilleur_score , score_moyen
    global sigma_mutation
    global dx
    global génération_actuelle
    génération_actuelle = 0
    sigma_ref = sigma_mutation
    meilleur_score , score_moyen , val_sigma = [] , [] , []
    if nom_foret == "Zalgaller" :
        para_evaluation = [8,1,20]
    elif nom_foret == "Isbell" :
        para_evaluation = [1,1,100]
    elif nom_foret == "rectangle" :
        para_evaluation = [6,6,10] #nb_x0,nb_y0,nb_orientations /!\ à modif si on change de foret
    else :
        breakpoint("nom_foret doit être Zalgaller ou Isbell ou rectangle")
    #nb_x0 = para_evaluation[0]
    population = création_pop(nb_individu,nb_segment)
    for génération in range (nb_génération) :
        if génération % 100 == 0 :
            sigma_mutation *= 0.8
        génération_actuelle = génération
        pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx,para_evaluation,nom_foret))
        meilleur_score.append(coût_trié[0])
        score_moyen.append(sum(coût_trié)/len(pop_triée))
        val_sigma.append(sigma_mutation/sigma_ref*20)
        population = séléction (pop_triée,coût_trié,sigma_mutation)
        """if coût_trié[0] <= 0 :
            nb_x0 += 10
            sigma_mutation *= 0.7
            #dx -= 0.02/nb_segment*10 
            print("évolution à la génération", génération, ": nb_x0 =", nb_x0)
            score,_,_,_,_ = fitness_lourde(pop_triée[0],dx)
            if score <= 0.05 :
                break"""
    pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx,para_evaluation,nom_foret))
    fitness_affichage_z_or_i(pop_triée[0],dx,nom_foret)
    affichage_forme_unique (pop_triée[0],dx)
    print("meilleur coût_trié[0] =", coût_trié[0])
    score, tx_moyen, nb_erreurs, nb_total, nb_segments_inutiles_moyen = fitness_lourde (pop_triée[0],dx)
    print("score :", score, "%, tx_moyen :", tx_moyen, "%, nb_erreurs :", nb_erreurs, ", nb_total :", nb_total, ", nb_segments_inutiles_moyen :", nb_segments_inutiles_moyen)
    return meilleur_score , score_moyen , val_sigma

meilleur_score , score_moyen , val_sigma = éxecution (nb_individu,nb_génération,nb_segment,nom_foret)
#fitness_affichage_z_or_i ([0,0,0,0],dx,"Isbell")

import matplotlib.pyplot as plt
plt.plot(meilleur_score) #[i+1 for i in range(nb_génération)]
plt.plot(score_moyen) #brouillon d'echelle log : [log(i+1) for i in range(500)]
#plt.plot(score_moyen)
plt.xscale("log")
#plt.yscale("log")
plt.show()

moncanva1.pack(expand=True)
fenêtre1.mainloop()
