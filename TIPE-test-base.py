from math import *
import tkinter as tki

n = 500
m = 500

esp = [[False]*m for _ in range (n)]

def peint_foret_rectangle (x1,x2,y1,y2,is_foret) :
    for x in range (x1,x2 + 1) :
        for y in range (y1,y2 + 1) :
            esp [x][y] = True
    print ("foret modifiée")



# def peint_foret_polygone (,is_foret) :

#fenetre
fenetre = tki.Tk()
fenetre.title("visualisation")
fenetre.geometry("1080x720")
fenetre.minsize(480,360)
fenetre.config(background="#f1ede4") #e8e2d6 #ece8d2


#affichage
fenetre.mainloop()


"""def Affiche_Nul(n):
    B=np.zeros((n,n))
    fenetre = tki.Tk()
    Text=str(B)
    l = tki.LabelFrame(fenetre, text="Matrice nulle", padx=20, pady=20, width=600)
    l.pack(fill="both", expand="yes")
    tki.Label(l, text=Text).pack()
    fenetre.mainloop()

def Affiche_Matrice(A):
    fenetre = tki.Tk()
    Text=str(A)
    l = tki.LabelFrame(fenetre, text="Notre matrice", padx=20, pady=20, width=600)
    l.pack(fill="both", expand="yes")
    tki.Label(l, text=Text).pack()
    fenetre.mainloop()"""

