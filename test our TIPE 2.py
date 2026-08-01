"""import matplotlib.pyplot as plt
plt.xkcd(1,100,2)
plt.plot([i ** (1/2) for i in range (100)])
plt.show()"""

import tkinter as tk

root = tk.Tk()
root.geometry('600x400')  # fenêtre visible assez grande

canvas = tk.Canvas(root, width=300, height=200, bg='lightblue')
canvas.place(relx=0.5, rely=0.5, anchor='center')
print (canvas.winfo_width())

root.mainloop()
