"""import matplotlib.pyplot as plt
plt.xkcd(1,100,2)
plt.plot([i ** (1/2) for i in range (100)])
plt.show()"""

"""import tkinter as tk

root = tk.Tk()
root.geometry('600x400')  # fenêtre visible assez grande

canvas = tk.Canvas(root, width=300, height=200, bg='lightblue')
canvas.place(relx=0.5, rely=0.5, anchor='center')
print (canvas.winfo_width())

root.mainloop()"""

"""import random 
import matplotlib.pyplot as plt 
	
# store the random numbers in a list 
nums = [] 
mu = 100
sigma = 50

def distrib_gaussienne_centrée_tronquée (inf,sup,k) : #sur l'intervalle [mu - k*sigma ; mu + k*sigma]
    mu = (inf + sup)/2
    sigma = (sup - inf)/(2*k)
    X = random.gauss(mu,sigma)
    while abs(X-mu) > k*sigma : #pas optimal surtout si k petit
        X = random.gauss(mu,sigma)
    return X

def distrib_gaussienne_tronquée (inf,sup,mu,sigma_relatif) : # un calcul d'intégrale permetterait d'avoir un équivalent du k
    sigma = sigma_relatif * (sup - inf) #chercher la justification de cette dépendance linéaire
    X = random.gauss(mu,sigma)
    while X < inf or X > sup :
        X = random.gauss(mu,sigma)
    return X

for i in range(50000): 
    #temp = distrib_gaussienne_centrée_tronquée (-1,1,10)
    #temp = distrib_gaussienne_tronquée (-10,20,0,0.3)
    #temp = abs(distrib_gaussienne_centrée_tronquée (-1,1,4))
    #temp = int(abs(distrib_gaussienne_centrée_tronquée (-15,15,2)))
    #temp = (random.random())**2
    #temp = (1-sqrt(random.random()))
    #temp = sinh(2*random.random())
    #temp = 1 - sin(1.5*random.random())
    #temp = exp(2*random.random())
    temp = distrib_gaussienne_tronquée(-180,180,-20,0.01)
    nums.append(temp) 

# plotting a graph 
plt.hist(nums, bins = 200) 
plt.show()"""
"""
nb_orientations = 8
from math import pi
print([(2*pi*k/nb_orientations - pi)/pi*180 for k in range (nb_orientations)])
"""
"""
# test fct en argument
def f1(x):
    return x + 2
def f2(x):
    return x * x
def appliquer_fonction_sur_liste(f, liste):
    return [f(x) for x in liste]
print(appliquer_fonction_sur_liste(f1, [1, 2, 3]))
print(appliquer_fonction_sur_liste(f2, [1, 2, 3]))
print(appliquer_fonction_sur_liste(lambda x: x - 5, [1, 2, 3]))
"""



from math import pi,sqrt,sin,cos,exp,tan

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

individu_ex_1 = [0,0,0,0,0]
individu_ex_2 = [0,90,0,0,0]
individu_ex_2_bis = [0,-90,0,0,0]
individu_ex_3 = [180,0,0,0,0]
individu_ex_4 = [0,30,-30,0,0]


def coeff_similarité_dist_vect (ind1,ind2) :
    assert len(ind1) == len(ind2)
    dist = sqrt(sum([(ind1[i]-ind2[i])**2 for i in range (1,len(ind1))])) #le premier angle est arbitraire
    return dist

def coeff_similarité_dist_pt_par_pt (ind1,ind2) :
    assert len(ind1) == len(ind2)
    n = len(ind1)
    l0 = 1
    ind2[0] = ind1[0] #le premier angle est arbitraire
    ind1_pts = angles_a_forme (ind1,l0)
    ind2_pts = angles_a_forme (ind2,l0)
    dist = sum([sqrt((ind2_pts[i][0] - ind1_pts[i][0])**2 + (ind2_pts[i][1] - ind1_pts[i][1])**2) for i in range (2,n)])
    dist_max = l0*(n-2)*(n-1)
    a = 2
    return dist, dist_max, ind1_pts, ind2_pts, [sqrt((ind2_pts[i][0] - ind1_pts[i][0])**2 + (ind2_pts[i][1] - ind1_pts[i][1])**2) for i in range (2,n)] #(exp(a*dist/dist_max)-1)/(exp(a)-1)
"""
print (coeff_similarité_dist_vect (individu_ex_1,individu_ex_2),
      coeff_similarité_dist_vect (individu_ex_1,individu_ex_3),
      coeff_similarité_dist_vect (individu_ex_1,individu_ex_4)
      )
print (coeff_similarité_dist_pt_par_pt (individu_ex_2_bis,individu_ex_2),
      #coeff_similarité_dist_pt_par_pt (individu_ex_1,individu_ex_3),
      #coeff_similarité_dist_pt_par_pt (individu_ex_1,individu_ex_4),
      )
"""
#--------------------------------------------------#
Lforet = 10 #largeur de la foret pour Zalgaller, Isbell et rectangle
Hforet = 10 #hauteur de la foret pour rectangle

def appartenance_rectangle (x0,y0,orientation,x,y) :
    global Lforet
    global Hforet
    ε = 1e-10
    if (sin(orientation) < ε) : # Pour éviter les approximations dues aux flottants
        return ( - Lforet/2 <= x <= Lforet/2) and ( - Hforet/2 <= y <= Hforet/2)
    elif (cos(orientation) < ε) :
        return ( - Hforet/2 <= x <= Hforet/2) and ( - Lforet/2 <= y <= Lforet/2)
    else :
        orientation_radian = orientation * pi /180
        pente1 = - tan(pi/2 - orientation_radian) #eq de la droite : y = pente * x + y0 
        bool1 = y - y0 <= pente1 * (x-x0) - (0 - Lforet / 2) / sin(orientation_radian)
        bool2 = y - y0 >= pente1 * (x-x0) - (0 + Lforet / 2) / sin(orientation_radian)
        pente2 = - tan(pi/2 - (orientation_radian + pi/2))
        bool3 = y - y0 >= pente2 * (x-x0) - (0 - Hforet / 2) / sin(orientation_radian + pi/2)
        bool4 = y - y0 >= pente2 * (x-x0) - (0 + Hforet / 2) / sin(orientation_radian + pi/2)
        return ((bool1 and bool2) or (not bool1 and not bool2)) and ((bool3 and bool4) or (not bool3 and not bool4))

#print(appartenance_rectangle (0,0,pi/4,0,6))

def angles_a_forme2 (Langles,dx) : #petite optimisation mais confusion : le 1er angle est inutile
    x , y = 0 , 0
    fap = [(x,y)]
    #print("Langles",Langles)
    for orientation in Langles :
        x , y = x + dx * sin(orientation*pi/180) , y + dx * cos(orientation*pi/180)
        fap.append((x,y))
    return fap

Lex1 = [0,0,90,0,-90] #liste des angles successifs décrivant un individu
print(angles_a_forme(Lex1,2))
