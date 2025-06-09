from math import *
import tkinter as tki

n = 100
m = 100

esp = [[False]*m for _ in range (n)]

def peint_foret_rectangle (x1,x2,y1,y2,is_foret) :
    for x in range (x1,x2 + 1) :
        for y in range (y1,y2 + 1) :
            esp [x][y] = True
    print ("foret modifiée")



# def peint_foret_polygone (,is_foret) :

# Paramètres de la grille
ligne = n
colonne = m
taille_cellule = 5  # taille des cases en pixels





#fenetre
fenetre = tki.Tk()
fenetre.title("visualisation")
fenetre.geometry("1080x720")
fenetre.minsize(480,360)
fenetre.config(background="#f1ede4") #e8e2d6 #ece8d2

canvas = tki.Canvas(fenetre, width=colonne*taille_cellule, height=ligne*taille_cellule)
canvas.pack()

# Dessin de la grille
color_map = {
    True: "green",
    False: "#f1ede4"
}
for i in range(ligne):
    for j in range(colonne):
        x1 = j * taille_cellule
        y1 = i * taille_cellule
        x2 = x1 + taille_cellule
        y2 = y1 + taille_cellule
        canvas.create_rectangle(x1, y1, x2, y2, fill=color_map[(esp[i][j])])

#affichage
fenetre.mainloop()

