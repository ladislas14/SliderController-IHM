import tkinter as tk
from tkinter.messagebox import *
import re
import subprocess

class Application(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
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
        self.start_button = tk.Button(self, text="Démarrer l'essai", command=self.start)
        self.stop_button = tk.Button(self, text="Arrêt d'urgence", command=self.stop, bg='red')

        self.main_title.pack()

        self.input_frame.pack()
        self.distance_label.pack()
        self.distance_input.pack()
        self.velocity_label.pack()
        self.velocity_input.pack()

        self.initialization_button.pack()
    
    def initialize(self):
        # Send serial for initialization
        if askyesno("Initialisation du banc", "Avant de lancer l'initialisation, vérifier que rien que rien ne gène le slider ou qu'aucun risque n'est présent."):
            self.initialization_button.pack_forget()
            self.start_button.pack()

    def start(self):
        # Send serial for start
        if askyesno("Démarrage de l'essai", "Avant de lancer l'essai, vérifier que rien que rien ne gène le slider ou qu'aucun risque n'est présent."):
            print(self.distance_input.get())
            self.start_button.pack_forget()
            self.stop_button.pack()

    def stop(self):
        # Send serial for start
        print("STOOOOOP")


if __name__ == "__main__":
    device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")
    devices = []
    for i in df.split('\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)
    print(devices)
    app = Application()
    app.title("Slider Controller")
    app.geometry("600x320")
    app.mainloop()

