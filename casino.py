import customtkinter as ctk
import tkinter as tk
from PIL import Image
import random

class Casino(ctk.CTkFrame) :
    def __init__(self, master):
        super().__init__(master, fg_color="black")
        self.pack(fill="both", expand=True)
        self.casino_frames = {}
        self.create_selecter()

    def create_selecter(self):
        self.container_casino = ctk.CTkFrame(self, fg_color="black")
        self.container_casino.pack(fill="both", expand=True)
        
        self.menu_casino = ctk.CTkFrame(self.container_casino, fg_color="black")
        self.menu_casino.pack(fill="both", expand=True)

        try: 
            wheel_pic = ctk.CTkImage(dark_image=Image.open("Image/Roulette.png"), size=(320,320))
            slot_pic = ctk.CTkImage(dark_image=Image.open("Image/Casino/SlotMachine.png"), size=(320,320))
            trading_pic = ctk.CTkImage(dark_image=Image.open("Image/Trading.png"), size=(320,320))
            multi_pic = ctk.CTkImage(dark_image=Image.open("Image/Multi.png"), size=(320,320))
            bank_pic = ctk.CTkImage(dark_image=Image.open("Image/Bank.png"), size=(320,320))
        except:
            wheel_pic = None
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None

        self.btn_wheel = ctk.CTkButton(self.menu_casino, text="Roulette", fg_color="transparent", image=wheel_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_wheel.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
                
        self.btn_market = ctk.CTkButton(self.menu_casino, text="Slot machine", fg_color="transparent", image=slot_pic, compound="top", command=self.open_slot_machine)
        self.btn_market.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
                
        self.btn_stats = ctk.CTkButton(self.menu_casino, text="Trading", fg_color="transparent", image=trading_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_stats.grid(row=0, column=3, padx=5, pady=10, sticky="nsew")
                
        self.btn_multi = ctk.CTkButton(self.menu_casino, text="Multi", fg_color="transparent", image=multi_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_multi.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
                
        self.btn_bank = ctk.CTkButton(self.menu_casino, text="Bank", fg_color="transparent", image=bank_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_bank.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")

        # Initialisation de la vue SlotMachine en arrière-plan dans le conteneur
        self.slot_view = SlotMachine(self.container_casino, back_callback=self.return_menu)
        self.slot_view.place(relx=0, rely=0, relwidth=1, relheight=1)
        # On la cache au démarrage pour n'afficher que le menu du casino
        self.slot_view.lower()

    def open_slot_machine(self):
        """Fait passer la machine à sous au premier plan"""
        self.slot_view.tkraise()

    def return_menu(self):
        """Remet le menu du casino au premier plan (si tu ajoutes un bouton retour)"""
        self.menu_casino.tkraise()

class Roulette(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="black")
        self.pack(fill="both", expand=True)

class SlotMachine(ctk.CTkFrame):
    def __init__(self, master, back_callback=None):
        super().__init__(master, fg_color="black")
        self.pack(fill="both", expand=True)
        
        # Liste de tes images pour l'animation
        self.image_paths = ["Image/Casino/SlotMachine/7.png", "Image/Casino/SlotMachine/Bell.png",
                             "Image/Casino/SlotMachine/Cherry.png", "Image/Casino/SlotMachine/Bar.png",
                             "Image/Casino/SlotMachine/Melon.png"]
        
        # Chargement des images en mémoire
        self.loaded_images = []
        for path in self.image_paths:
            try:
                self.loaded_images.append(ctk.CTkImage(dark_image=Image.open(path), size=(400, 400)))
            except:
                pass

        # --- CONTENEUR POUR LES 3 ROULEAUX (Côte à côte) ---
        self.rouleaux_frame = ctk.CTkFrame(self, fg_color="black")
        self.rouleaux_frame.pack(pady=40)

        # Création des 3 labels (les 3 rouleaux)
        self.slot_label1 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label1.grid(row=0, column=0, padx=10)

        self.slot_label2 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label2.grid(row=0, column=1, padx=10)

        self.slot_label3 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label3.grid(row=0, column=2, padx=10)

        # Afficher une image par défaut au démarrage sur les 3 rouleaux
        if self.loaded_images:
            for lbl in (self.slot_label1, self.slot_label2, self.slot_label3):
                lbl.configure(image=self.loaded_images[0])

        # Bouton pour lancer l'animation
        self.btn_play = ctk.CTkButton(self, text="Jouer à la Machine à Sous", command=self.lancer_machine)
        self.btn_play.pack(pady=10)

        # Variables de suivi pour les 3 rouleaux
        self.temps_1 = 0
        self.temps_2 = 0
        self.temps_3 = 0

        self.result_label = ctk.CTkLabel(self, text="", font=("Arial", 16, "bold"))
        self.result_label.pack(pady=20)

    def lancer_machine(self):
        """Déclenche l'animation des 3 rouleaux avec des temps d'arrêt échelonnés"""
        self.btn_play.configure(state="disabled")
        self.result_label.configure(text="")
        
        # Chaque rouleau tourne un peu plus longtemps que le précédent
        # Rouleau 1 s'arrête à 6 secondes, Rouleau 2 à 8 secondes, Rouleau 3 à 10 secondes
        self.temps_1 = 500
        self.temps_2 = 1500
        self.temps_3 = 2500

        self.index_final_1 = None
        self.index_final_2 = None
        self.index_final_3 = None

        self.animer_rouleau_1()
        self.animer_rouleau_2()
        self.animer_rouleau_3()

    def animer_rouleau_1(self):
        if self.temps_1 > 0:
            if self.loaded_images:
                self.slot_label1.configure(image=random.choice(self.loaded_images))
            self.temps_1 -= 80
            self.after(80, self.animer_rouleau_1)
        else:
            if self.loaded_images:
                self.index_final_1 = random.randint(0, len(self.loaded_images) - 1)
                self.slot_label1.configure(image=self.loaded_images[self.index_final_1])


    def animer_rouleau_2(self):
        if self.temps_2 > 0:
            if self.loaded_images:
                self.slot_label2.configure(image=random.choice(self.loaded_images))
            self.temps_2 -= 80
            self.after(80, self.animer_rouleau_2)
        else:
            # Résultat final pour le rouleau 2
            if self.loaded_images:
                self.index_final_2 = random.randint(0, len(self.loaded_images) - 1)
                self.slot_label2.configure(image=self.loaded_images[self.index_final_2])

    def animer_rouleau_3(self):
        if self.temps_3 > 0:
            if self.loaded_images:
                self.slot_label3.configure(image=random.choice(self.loaded_images))
            self.temps_3 -= 80
            self.after(80, self.animer_rouleau_3)
        else:
            if self.loaded_images:
                self.index_final_3 = random.randint(0, len(self.loaded_images) - 1)
                self.slot_label3.configure(image=self.loaded_images[self.index_final_3])

            self.verify_victory()
            self.btn_play.configure(state="normal")

    def verify_victory(self):
        if self.index_final_1 == self.index_final_2 == self.index_final_3:
            self.result_label.configure(text="Win!!!", text_color="green")
            # Code pour gain argent
        else:
            self.result_label.configure(text="Lose...", text_color="red")
            # code pour perte argent