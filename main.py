import tkinter as tk
from tkinter.messagebox import *
import re
import serial
import time
import threading

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.isStarted = False
        self.create_widgets()

    def create_widgets(self):
        self.main_title = tk.Label(self, text="Commande du slider de 4m !!!", padx=20, pady=20)
        self.main_title.config(font=("TkDefaultFont", 24))

        self.input_frame = tk.LabelFrame(self, text="Configuration pour l'essai", padx=20, pady=20)

        self.distance_label = tk.Label(self.input_frame, text="Longueur du banc d'essai (en m)")
        self.distance_input = tk.Spinbox(self.input_frame, from_=0, to=4, increment=0.1)

        self.velocity_label = tk.Label(self.input_frame, text="Vitesse nominale max (en m/s)")
        self.velocity_input = tk.Spinbox(self.input_frame, from_=0, to=1, increment=0.1)
        
        self.initialization_button = tk.Button(self, text="Initialiser", command=self.initialize)
        self.start_button = tk.Button(self, text="Démarrer l'essai", command=self.start, state="disabled")
        self.stop_button = tk.Button(self, text="Arrêt d'urgence", command=self.stop, bg='red')

        self.velocity_label = tk.Label(self, text="Vitesse : 0.00 m/s", padx=20, pady=20)


        self.main_title.pack()

        self.input_frame.pack()
        self.distance_label.pack()
        self.distance_input.pack()
        self.velocity_label.pack()
        self.velocity_input.pack()

        self.initialization_button.pack()

        self.velocity_label.pack()

        self.main_title.pack()


        self.update_real_velocity()
    
    def initialize(self):
        # Send serial for initialization
        if askyesno("Initialisation du banc", "Avant de lancer l'initialisation, vérifier que rien que rien ne gène le slider ou qu'aucun risque n'est présent."):
            self.initialization_button.pack_forget()
            command = "i" + str(self.distance_input.get())
            ser.write(command.encode())
            self.start_button.pack()
            self.start_button['state'] = 'normal'

    def start(self):
        # Send serial for start
        print(self.velocity_input.get())
        command = "v" + str(self.velocity_input.get())
        ser.write(command.encode()) 
        self.isStarted = True
        self.start_button.pack_forget()
        self.stop_button.pack()

    def stop(self):
        # Send serial for start
        ser.write("s".encode())
        print("STOOOOOP")
        self.isStarted = False
        self.stop_button.pack_forget()
        self.initialization_button.pack()

    def update_real_velocity(self):
        if(self.isStarted):
            ser_bytes = ser.readline()
            decoded_bytes = ser_bytes[0:len(ser_bytes)-2].decode("utf-8")
            try:
                float(decoded_bytes)
                print(float(decoded_bytes))
                self.velocity_label['text'] = "Vitesse : " + str(round(float(decoded_bytes), 2)) + "m/s"
            except ValueError:
                return False
        self.after(10, self.update_real_velocity)

if __name__ == "__main__":
    app = Application()
    app.title("Slider Controller")
    app.geometry("600x320")
    app.mainloop()
    


