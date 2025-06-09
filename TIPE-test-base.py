from math import *
import tkinter as tki

n = 50
m = 70

esp = [[False]*m for _ in range (n)]

def peint_foret_rectangle (x1,x2,y1,y2,is_foret) :
    for x in range (x1,x2 + 1) :
        for y in range (y1,y2 + 1) :
            esp [x][y] = is_foret
    print ("foret modifiée")



# def peint_foret_polygone (,is_foret) :

def test_forme_foret_1 () :
    peint_foret_rectangle (5,35,9,40,True)
    peint_foret_rectangle (35,45,9,25,True)

def test_forme_foret_2 () :
    peint_foret_rectangle (10,30,0,60,True)


#--------------------------------------------#
# Paramètres d'affichage de la grille
ligne = n
colonne = m
taille_cellule = 10  # taille des cases en pixels

#fenetre
fenetre = tki.Tk()
fenetre.title("visualisation")
fenetre.geometry("480x480")
fenetre.minsize(480,360)
fenetre.config(background="#f1ede4") #e8e2d6 #ece8d2

canvas = tki.Canvas(fenetre, width=colonne*taille_cellule, height=ligne*taille_cellule,highlightthickness=0,insertbackground="#f1ede4")
canvas.pack(ipadx=1,ipady=1) 

# Dessin de la grille
color_map = {
    True: "green",
    False: "#f1ede4"
}
def maj_affichage () :
    for i in range(ligne):
        for j in range(colonne):
            x1 = j * taille_cellule
            y1 = i * taille_cellule
            x2 = x1 + taille_cellule
            y2 = y1 + taille_cellule
            canvas.create_rectangle(x1, y1, x2, y2, fill=color_map[(esp[i][j])],outline="") 

#affichage
maj_affichage ()
test_forme_foret_2 ()
maj_affichage ()
fenetre.mainloop()