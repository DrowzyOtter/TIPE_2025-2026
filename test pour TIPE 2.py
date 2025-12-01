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

import random 
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
plt.show()
