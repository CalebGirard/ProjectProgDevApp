import customtkinter as ctk
import tkinter as tk
from PIL import Image
import random

class CasinoView(ctk.CTkFrame) :
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.casino_frames = {}
        self.create_selecter()

    def create_selecter(self):
        self.container_casino = ctk.CTkFrame(self, fg_color="#0b0e11")
        self.container_casino.pack(fill="both", expand=True)
        
        self.menu_casino = ctk.CTkFrame(self.container_casino, fg_color="#0b0e11")
        self.menu_casino.pack(fill="both", expand=True)

        for column in range(2):
            self.menu_casino.grid_columnconfigure(column, weight=1)

        promo_banner = ctk.CTkFrame(
            self.menu_casino, fg_color="#181a20", corner_radius=8
        )
        promo_banner.grid(
            row=0, column=0, columnspan=2, padx=24, pady=(20, 8), sticky="ew"
        )
        ctk.CTkLabel(
            promo_banner,
            text="CASINO LABS  /  EXCLUSIVE ENTERTAINMENT TECHNOLOGY",
            text_color="#0ecb81",
            font=("Arial", 12, "bold"),
        ).pack(anchor="w", padx=20, pady=(14, 2))
        ctk.CTkLabel(
            promo_banner,
            text="A new standard in play.",
            text_color="#eaecef",
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", padx=20)
        ctk.CTkLabel(
            promo_banner,
            text="Discover our next-gen suite of high-performance experiences, "
                 "engineered for your every winning moment.",
            text_color="#848e9c",
            font=("Arial", 13),
            wraplength=760,
        ).pack(anchor="w", padx=20, pady=(2, 14))

        try: 
            wheel_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/Casino/roulette.png"),
                size=(180, 180),
            )
            slot_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/Casino/SlotMachine.png"),
                size=(180, 180),
            )
        except:
            wheel_pic = slot_pic = None

        games_frame = ctk.CTkFrame(self.menu_casino, fg_color="transparent")
        games_frame.grid(
            row=1, column=0, columnspan=2, padx=18, pady=(16, 8), sticky="w"
        )

        for column in range(2):
            games_frame.grid_columnconfigure(column, weight=1)

        self.btn_wheel = ctk.CTkButton(
            games_frame,
            text="Roulette",
            width=240,
            height=225,
            fg_color="#181a20",
            hover_color="#2b313a",
            text_color="#eaecef",
            corner_radius=8,
            image=wheel_pic,
            compound="top",
            command=lambda: print("ta mere"),
        )
        self.btn_wheel.grid(row=0, column=0, padx=6, pady=(0, 8))

        self.btn_market = ctk.CTkButton(
            games_frame,
            text="Slot machine",
            width=240,
            height=225,
            fg_color="#181a20",
            hover_color="#2b313a",
            text_color="#eaecef",
            corner_radius=8,
            image=slot_pic,
            compound="top",
            command=self.open_slot_machine,
        )
        self.btn_market.grid(row=0, column=1, padx=6, pady=(0, 8))

        ctk.CTkLabel(
            games_frame,
            text="Our precision-crafted, 360-degree decision platform brings "
                 "next-gen chance analytics to every spin.",
            text_color="#848e9c",
            font=("Arial", 13),
            width=240,
            wraplength=230,
            justify="center",
        ).grid(row=1, column=0, padx=6, sticky="n")
        ctk.CTkLabel(
            games_frame,
            text="Activate our high-velocity reward engine, powered by "
                 "multi-reel momentum and proprietary symbol synchronization.",
            text_color="#848e9c",
            font=("Arial", 13),
            width=240,
            wraplength=230,
            justify="center",
        ).grid(row=1, column=1, padx=6, sticky="n")

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
        self.machine_running = False
        self.curr = 1
        
        # Liste de tes images pour l'animation
        self.image_paths = ["Assets/Casino/SlotMachine/7.png", "Assets/Casino/SlotMachine/black-hole.png",
                             "Assets/Casino/SlotMachine/Cherries.png", "Assets/Casino/SlotMachine/diamonds.png",
                             "Assets/Casino/SlotMachine/blossom.png","Assets/Casino/SlotMachine/crown.png",
                             "Assets/Casino/SlotMachine/dvd-player.png","Assets/Casino/SlotMachine/gem.png",
                             "Assets/Casino/SlotMachine/honeycomb.png"]
        
        # Chargement des images en mémoire
        self.loaded_images = []
        for path in self.image_paths:
            try:
                self.loaded_images.append(ctk.CTkImage(dark_image=Image.open(path), size=(400, 400)))
            except:
                pass

        self.rouleaux_frame = ctk.CTkFrame(self, fg_color="black")
        self.rouleaux_frame.pack(pady=40)

        self.slot_label1 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label1.grid(row=0, column=0, padx=10)

        self.slot_label2 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label2.grid(row=0, column=1, padx=10)

        self.slot_label3 = ctk.CTkLabel(self.rouleaux_frame, text="", fg_color="gray20", width=450, height=450, corner_radius=15)
        self.slot_label3.grid(row=0, column=2, padx=10)

        self.label2 = ctk.CTkLabel(self,text="Click and press space to play",text_color="White",font=("Arial",48, "bold"))
        self.label2.pack(pady=10,padx=10)

        if self.loaded_images:
            for lbl in (self.slot_label1, self.slot_label2, self.slot_label3):
                lbl.configure(image=self.loaded_images[0])

        self.bind("<space>",lambda x:self.lancer_machine())
        self.bind("<Escape>",lambda x:self.lancer_machine())
        self.focus_set()

        # Variables de suivi pour les 3 rouleaux
        self.temps_1 = 0
        self.temps_2 = 0
        self.temps_3 = 0

        self.result_label = ctk.CTkLabel(self, text="", font=("Arial", 200, "bold"))
        self.result_label.pack(pady=20)

    def lancer_machine(self):
        """Déclenche l'animation des 3 rouleaux avec des temps d'arrêt échelonnés"""
        if self.machine_running:
            if self.curr == 1:
                self.temps_1 = 0
            elif self.curr == 2:
                self.temps_2 = 0
            elif self.curr == 3:
                self.temps_3 = 0
            self.curr += 1
            return
        self.result_label.configure(text="")
        self.machine_running = True
        self.curr = 1
        
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

    def verify_victory(self):
        if self.index_final_1 == self.index_final_2 == self.index_final_3:
            self.result_label.configure(text="YIPEEEEEEEEEE!!!", text_color="green")
            # Code pour gain argent
        else:
            self.result_label.configure(text="Stupid Loser :()", text_color="red")
            # code pour perte argent
        self.machine_running = False
        self.curr = 1
