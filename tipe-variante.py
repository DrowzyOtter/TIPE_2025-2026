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

def distrib_gaussienne_tronquée (inf,sup,mu,sigma_relatif) : 
    sigma = sigma_relatif * (sup - inf)
    X = gauss(mu,sigma)
    #while X < inf or X > sup :
    #    X = gauss(mu,sigma)
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
        raise Exception("Trop peu d'éléments uniques piochés")
    return sorted(piochés)

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
        raise Exception("Trop peu d'éléments uniques piochés")
    return sorted(piochés) #ou utilisé sa propre fct de tri

# endregion

"""varables"""
nb_individu = 75
Lforet = 10 #largeur de la foret pour Zalgaller, Isbell et rectangle
Hforet = 10 #hauteur de la foret pour rectangle
nom_foret = "Isbell"
#nom_foret = "Zalgaller"
#nom_foret = "rectangle"

nb_segment = 16 #dx = longueur de chaque segment

if nom_foret == "Isbell" :
    l0 = 6.3972/2
elif nom_foret == "Zalgaller" :
    l0 = 2.278
elif nom_foret == "rectangle" :
    l0 = sqrt(1+(Hforet/Lforet)**2)
else :
    raise Exception("nom_foret doit être Zalgaller ou Isbell ou rectangle")


dx = ( l0 + 0.03)/nb_segment*Lforet*2
#assert abs(dx*nb_segment - (sqrt(2)+0.03)*10)<10**(-4)

sigma_mutation = 0.005 * 30 #écart type relatif pour la mutation
nb_génération = 15
génération_actuelle = 0
répartition = [3,5,27,40] #élitisme, réplication, croisement, mutation
assert sum(répartition) == nb_individu

données_csv = []

"""variables de test"""
Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant un individu

###création de la population de départ
def création_pop (nb_individu,nb_segment) :
    population = []
    for _ in range (nb_individu) :
        population.append([distrib_uniforme(-180,180) for _ in range (nb_segment)])
    return population

def angles_a_forme (Langles,dx) : # le 1er angle est inutile
    x , y = 0 , 0
    fap = [(x,y)]
    orientation = 0
    for angle in Langles :
        orientation += angle
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap

def angles_a_forme2 (Langles,dx) : #angles absolus par rapport à l'axe des abscisses
    x , y = 0 , 0
    fap = [(x,y)]
    for orientation in Langles :
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap


###-------------------------------###
###       fitness fonction        ###
###-------------------------------###

###test de présence et vecteur de départ avec une definition parametrique de la foret
#region : cas simplifié : rectangle (suivant la grille)

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

def positions_évaluées_équiréparti (para) : #-> liste de x0 , liste de y0, liste d'orientations
    nb_x0,nb_y0,nb_orientations = para
    global Lforet
    global Hforet
    ε = 1e-2
    x0_évalués = liste_équirépartie(ε,Lforet/2-ε,nb_x0)
    y0_évalués = liste_équirépartie(ε,Hforet/2-ε,nb_y0)
    orientations_évaluées = [(2*pi*k/nb_orientations - pi)/pi*180 for k in range (nb_orientations)]
    return x0_évalués, y0_évalués, orientations_évaluées

def appartenance_Zalgaller (x0, orientation, x, y) : #-> bool
    global Lforet
    ε = 1e-10
    orientation_radian = orientation * pi /180
    if (abs(sin(orientation_radian)) < ε) : # Pour éviter les approximations dues aux flottants
        return -Lforet/2 <= x <= Lforet/2
    else :
        pente = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y <= pente * x - (x0 - Lforet / 2) / sin(orientation_radian)
        bool2 = y >= pente * x - (x0 + Lforet / 2) / sin(orientation_radian)
        return (bool1 and bool2) or (not bool1 and not bool2) #on ne pense pas tout de suite au second cas

#endregion
#region : cas de Isbell : demi-plan (dont la frontière est à une distance L)

def appartenance_Isbell (x0,orientation,x, y) : #-> bool
    global Lforet
    ε = 1e-5
    orientation_radian = orientation * pi /180
    if abs(sin(orientation_radian)) < ε : # Pour éviter les approximations dues aux flottants 
        #print("celui-la")
        return -Lforet/2 <= x <= Lforet/2
    else :
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
        raise Exception("nom_foret doit être Zalgaller ou Isbell ou rectangle")

"""def création_positions_évaluées_aléatoires (nb_positions_évaluées,Lforet) : #-> liste de (x0,orientation)
    positions_évaluées = []
    for _ in range (nb_positions_évaluées) : 
        positions_évaluées.append(vecteur_de_départ_Zalgaller(Lforet))
    return positions_évaluées"""

def fitness (individu,dx,para_evaluation : list,nom_foret) : #-> nombre d'échecs (à minimiser)
    global génération_actuelle
    xy_ind = angles_a_forme(individu,dx)
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti (para_evaluation)
    lmax = float('inf')
    if nom_foret == "Zalgaller" :
        for x0 in x0_évalués :
            for orientation in orientations_évaluées :
                dedans = [appartenance_Zalgaller(x0,orientation,x,y) for (x,y) in xy_ind]
                if not False in dedans :
                    échecs += 1
    elif nom_foret == "Isbell" :
        for x0 in x0_évalués :
            for orientation in orientations_évaluées :
                dedans = [appartenance_Isbell(x0,orientation,x,y) for (x,y) in xy_ind]
                if False in dedans :
                    indice = 0
                    lmax = dx
                    while indice < len(dedans) and dedans[indice] :
                        lmax += dx
                        indice += 1
    elif nom_foret == "rectangle" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = [appartenance_rectangle(x0,y0,orientation,x,y) for (x,y) in xy_ind]
                    if not False in dedans :
                        échecs += 1
    else :
        raise Exception("nom_foret doit être Zalgaller ou Isbell ou rectangle")
    #if échecs == 0 :
        fitness_affichage_z_or_i(individu,dx,"rectangle")
        moncanva1.pack(expand=True)
        fenêtre1.mainloop()
    return lmax

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
    for (X,Y) in pioche_couple_parmi_un_intervalle(0,len(pop_triée),répartition[2]) : #croisement 
        demi = len(pop_triée[X]) // 2
        nv_population.append(pop_triée[X][:demi] + pop_triée[Y][demi:])
    for X in pioche_parmi_un_intervalle(0,len(pop_triée),répartition[3]): #mutation
        indivdu = pop_triée[X][:]
        for i in range(len(indivdu)) :
            indivdu[i] = distrib_gaussienne_tronquée(-180,180,indivdu[i],sigma_mutation) #sigma dynamique
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
    A = (1, 69, 31) #20, 110, 145 //  0, 122, 51
    B = (71, 122, 54) #87, 199, 133 // 114, 237, 165
    C = (214, 197, 43) #237, 221, 83 // 237, 221, 83

    if t <= 0.4:
        u = t / 0.4 #0.67
        r = A[0] + u * (B[0] - A[0])
        g = A[1] + u * (B[1] - A[1])
        b = A[2] + u * (B[2] - A[2])
    else:
        u = (t - 0.4) / (1 - 0.4)
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
fenêtre1.configure(bg="#EEEEE2") # #020618

#moncanva = Canvas(fenêtre)
moncanva1 = Canvas(fenêtre1,width=largeur,height=hauteur, bg="#EEEEE2",borderwidth=0,highlightthickness=0) #020618
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

def nv_ligne (x0,y0,x1,y1,tx,canva,style="defaut") :
    épaisseur = 2
    X0 = convertisseur_affine_x(x0,canva)
    Y0 = convertisseur_affine_y(y0,canva)
    X1 = convertisseur_affine_x(x1,canva)
    Y1 = convertisseur_affine_y(y1,canva)
    if style == "frontiere" :
        couleur = "#290E00" #"white"
        largeur = 5
    elif style == "fine" :
        largeur = 2
        couleur = "#93BA8F"
    elif style == "defaut" :
        largeur = 3
        couleur = gradient_color(tx)
    return canva.create_line(X0,Y0,X1,Y1,fill=couleur,width=largeur)
#moncanva.create_oval(100,100,200,200,fill="red")

def afficher_individu (individu,dx,x0,y0,incl,tx,style="defaut") : #-> None
    xy_ind = angles_a_forme(individu,dx)
    for i in range (len(xy_ind)) :
        x , y = xy_ind[i]
        xy_ind[i] = x*cos(incl*pi/180) - y*sin(incl*pi/180) + x0 , x*sin(incl*pi/180) + y*cos(incl*pi/180) + y0
    for i in range (1,len(xy_ind)) :
        nv_ligne(xy_ind[i-1][0],xy_ind[i-1][1],xy_ind[i][0],xy_ind[i][1],tx,moncanva1,style)
    nv_point(x0,y0,tx,moncanva1)

def affichage_forme_unique (individu,dx,nom_page="None") : #-> None
    hauteur = 400*2
    largeur = 600*2
    fenêtre2 = Tk()
    if nom_page == "None" :
        fenêtre2.title("évaluation du fitness score simplifiée")
    else :
        fenêtre2.title(nom_page)
    fenêtre2.geometry("1126x900")
    fenêtre2.configure(bg="#EEEEE2") # 020618
    moncanva2 = Canvas(fenêtre2,width=largeur,height=hauteur, bg="#EEEEE2",borderwidth=0,highlightthickness=0)
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
        nv_ligne((xy_ind[i-1][0]-milieu_x)*coef,(xy_ind[i-1][1]-milieu_y)*coef,(xy_ind[i][0]-milieu_x)
                 *coef,(xy_ind[i][1]-milieu_y)*coef,tx,moncanva2)
        nv_point((xy_ind[i-1][0]-milieu_x)*coef,(xy_ind[i-1][1]-milieu_y)*coef,tx,moncanva2)
        tx -= 1/(len(xy_ind)-1)

def fitness_affichage_z_or_i (individu,dx,nom_foret : str) : #-> None
    #nb_segment = len(individu)
    global Lforet
    global Hforet
    if nom_foret == "Zalgaller" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-moncanva1.winfo_height()//2,-Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nb_x0 = 5
        nb_y0 = 1
        nb_orientations = 35
    elif nom_foret == "Isbell" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nb_x0 = 1
        nb_y0 = 1
        nb_orientations = 50
    elif nom_foret == "rectangle" :
        nv_ligne(Lforet/2,-Hforet/2,Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-Hforet/2,-Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-Hforet/2,Lforet/2,-Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,Hforet/2,Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nb_x0 = 3
        nb_y0 = 3
        nb_orientations = 5
    else :
        raise Exception("nom_foret doit être Zalgaller ou Isbell")
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti ([nb_x0,nb_y0,nb_orientations])
    tx = 0
    for x0 in x0_évalués :
        for y0 in y0_évalués :
            for orientation in orientations_évaluées :
                #if nom_foret == "Zalgaller" :
                #print(x0,orientation)
                afficher_individu (individu,dx,x0,y0,orientation,tx,style="fine")
                tx += 1/(nb_x0*nb_y0*nb_orientations)


def fitness_affichage_z_or_i_2 (individu,dx,nom_foret : str) : #-> None
    global Lforet
    global Hforet
    if nom_foret == "Zalgaller" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-moncanva1.winfo_height()//2,-Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nb_x0 = 6
        nb_y0 = 1
        nb_orientations = 40
    elif nom_foret == "Isbell" :
        nv_ligne(Lforet/2,-moncanva1.winfo_height()//2,Lforet/2,moncanva1.winfo_height()//2,2,moncanva1,style="frontiere")
        nb_x0 = 1
        nb_y0 = 1
        nb_orientations = 20
    elif nom_foret == "rectangle" :
        nv_ligne(Lforet/2,-Hforet/2,Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-Hforet/2,-Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,-Hforet/2,Lforet/2,-Hforet/2,2,moncanva1,style="frontiere")
        nv_ligne(-Lforet/2,Hforet/2,Lforet/2,Hforet/2,2,moncanva1,style="frontiere")
        nb_x0 = 3
        nb_y0 = 3
        nb_orientations = 5
    else :
        raise Exception("nom_foret doit être Zalgaller ou Isbell")
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
                        afficher_individu (individu,dx,x0,y0,-orientation,1,style="fine") #/!\ on a - orientation car l'oriantation de la forme est inverse de celle de la foret
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,0)
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
                        afficher_individu (individu,dx,x0,y0,-orientation,1,style="fine")
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,0)
    elif nom_foret == "rectangle" :
        for x0 in x0_évalués :
            for y0 in y0_évalués :
                for orientation in orientations_évaluées :
                    dedans = []
                    for (x,y) in xy_ind :
                        dedans.append(appartenance_rectangle(x0,y0,orientation,x,y))
                    if False in dedans :
                        afficher_individu (individu,dx,x0,y0,-orientation,1,style="fine")
                    else :
                        afficher_individu (individu,dx,x0,y0,-orientation,0)
    

def fitness_lourde (individu,dx) : #pas d'optimisation computationnelle, juste pour le test final
    #nb_segment = len(individu)
    global nom_foret
    nb_x0 = 10
    nb_orientations = 20
    if nom_foret == "rectangle" :
        nb_y0 = 50
    else :
        nb_y0 = 1
    xy_ind = angles_a_forme(individu,dx)
    tx_moyen = 0
    score = 1
    nb_erreurs = nb_x0 * nb_orientations * nb_y0
    nb_segments_inutiles_total = 0
    x0_évalués, y0_évalués, orientations_évaluées = positions_évaluées_équiréparti ([nb_x0,nb_y0,nb_orientations])
    for x0 in x0_évalués :
        for y0 in y0_évalués :
            for orientation in orientations_évaluées :
                dedans = []
                tx = 0
                for (x,y) in xy_ind :
                    dedans.append(appartenance_foret(nom_foret,x0,y0,orientation,x,y))
                for val in dedans : #useless
                    tx += int(val)/len(dedans)
                for i in range(len(dedans)) :
                    if dedans[i] == False :
                        nb_segments_inutiles_total += len(dedans) - i
                        nb_erreurs -= 1
                        break
                #if tx < 1 :
                #    score -= 1/(nb_x0 * nb_orientations)

                tx_moyen += tx/(nb_x0 * len(y0_évalués) * nb_orientations)
    if (nb_x0 * nb_orientations - nb_erreurs) > 0 : #segments inutiles moyens parmi les essais réussis
        nb_segments_inutiles_moyen = nb_segments_inutiles_total / (nb_x0 * nb_orientations - nb_erreurs)
    else :
        nb_segments_inutiles_moyen = 0
    score = nb_erreurs / (nb_x0 * nb_orientations*nb_y0)
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
        para_evaluation = [6,1,100]
    elif nom_foret == "Isbell" :
        para_evaluation = [1,1,300]
    elif nom_foret == "rectangle" :
        para_evaluation = [3,3,50] #nb_x0,nb_y0,nb_orientations /!\ à modif si on change de foret
    else :
        raise Exception("nom_foret doit être Zalgaller ou Isbell ou rectangle")
    #nb_x0 = para_evaluation[0]
    population = création_pop(nb_individu,nb_segment)
    for génération in range (nb_génération) :
        if génération % 50 == 0 :
            sigma_mutation *= 0.8
        génération_actuelle = génération
        pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx,para_evaluation,nom_foret))
        meilleur_score.append(coût_trié[0])
        score_moyen.append(sum(coût_trié)/len(pop_triée))
        val_sigma.append(sigma_mutation/sigma_ref*20)
        population = séléction (pop_triée,coût_trié,sigma_mutation)
        if génération in [0,50,250] :
            affichage_forme_unique (pop_triée[0],dx,nom_page="solution : génération "+ str(génération))
        """if coût_trié[0] <= 0 :
            nb_x0 += 10
            sigma_mutation *= 0.7
            #dx -= 0.02/nb_segment*10 
            print("évolution à la génération", génération, ": nb_x0 =", nb_x0)
            score,_,_,_,_ = fitness_lourde(pop_triée[0],dx)
            if score <= 0.05 :
                break"""
    pop_triée, coût_trié = couples_à_listes(évaluation_et_tri(population,dx,para_evaluation,nom_foret))
    fitness_affichage_z_or_i_2(pop_triée[0],dx,nom_foret)
    affichage_forme_unique (pop_triée[0],dx)
    print("meilleur coût_trié[0] =", coût_trié[0])
    score, tx_moyen, nb_erreurs, nb_total, nb_segments_inutiles_moyen = fitness_lourde (pop_triée[0],dx)
    print("score :", score, "%, tx_moyen :", tx_moyen, "%, nb_erreurs :", nb_erreurs, ", nb_total :",
           nb_total, ", nb_segments_inutiles_moyen :", nb_segments_inutiles_moyen)
    print("meilleur_individu", pop_triée[0])
    return meilleur_score , score_moyen , val_sigma

meilleur_score , score_moyen , val_sigma = éxecution (nb_individu,nb_génération,nb_segment,nom_foret)
#fitness_affichage_z_or_i ([0,0,0,0],dx,"Isbell")

#indiv = [0, 38.65915484868573, 144.3933496156547, -24.772945381715417, -253.8680812812645, -21.40937108991477, -37.314860376012035, -412.0528685556913, 37.40813284630995, -375.09821681035856, -20.616134651786336, 175.1870057392491, -140.6568666574284, -177.93303246328227, -9.631127855703012, 9.024971717728548]
#print(fitness(indiv,dx,[3,3,50],"rectangle"))
#fitness_affichage_z_or_i_2(indiv,dx,"rectangle")

import matplotlib.pyplot as plt
plt.plot(meilleur_score,c="#3a5a40") #[i+1 for i in range(nb_génération)]
plt.plot(score_moyen,c="#a3b18a") #brouillon d'echelle log : [log(i+1) for i in range(500)]
#plt.plot(score_moyen)
plt.xscale("log")
#plt.yscale("log")
plt.show()

moncanva1.pack(expand=True)
fenêtre1.mainloop()
