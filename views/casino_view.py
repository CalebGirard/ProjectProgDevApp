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
            text="PYNANCE CORP  |  EXCLUSIVE MAKE-O-RICH™ TECHNOLOGIES",
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
        super().__init__(master, fg_color="#0b0e11")
        self.machine_running = False
        self.curr = 1
        self.back_callback = back_callback
        
        self.image_paths = ["Assets/Casino/SlotMachine/7.png", "Assets/Casino/SlotMachine/black-hole.png",
                             "Assets/Casino/SlotMachine/cherries.png", "Assets/Casino/SlotMachine/diamond.png",
                             "Assets/Casino/SlotMachine/blossom.png","Assets/Casino/SlotMachine/crown.png",
                             "Assets/Casino/SlotMachine/dvd-player.png","Assets/Casino/SlotMachine/gem.png",
                             "Assets/Casino/SlotMachine/honeycomb.png"]
        
        self.loaded_images = []
        for path in self.image_paths:
            with Image.open(path) as symbol:
                self.loaded_images.append(
                    ctk.CTkImage(dark_image=symbol.copy(), size=(160, 160))
                )

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(18, 8))
        if self.back_callback is not None:
            ctk.CTkButton(
                header,
                text="<  Casino",
                width=94,
                height=32,
                fg_color="#181a20",
                hover_color="#2b313a",
                text_color="#eaecef",
                command=self.back_callback,
            ).pack(side="left")
        ctk.CTkLabel(
            header,
            text="CASINO  /  SLOT MACHINE",
            text_color="#848e9c",
            font=("Arial", 12, "bold"),
        ).pack(side="right", pady=6)

        ctk.CTkLabel(
            self,
            text="Three reels. One lucky spin.",
            text_color="#eaecef",
            font=("Arial", 28, "bold"),
        ).pack(pady=(5, 2))
        ctk.CTkLabel(
            self,
            text="Match all three symbols to win.",
            text_color="#848e9c",
            font=("Arial", 13),
        ).pack(pady=(0, 14))

        machine_card = ctk.CTkFrame(
            self, fg_color="#181a20", corner_radius=12
        )
        machine_card.pack(padx=32, pady=(0, 12))

        self.rouleaux_frame = ctk.CTkFrame(
            machine_card, fg_color="transparent"
        )
        self.rouleaux_frame.pack(padx=22, pady=(24, 16))

        self.reel_labels = []
        for column in range(3):
            reel = ctk.CTkFrame(
                self.rouleaux_frame,
                fg_color="#0b0e11",
                corner_radius=10,
                width=180,
                height=180,
            )
            reel.grid(row=0, column=column, padx=9)
            reel.grid_propagate(False)
            label = ctk.CTkLabel(reel, text="")
            label.place(relx=0.5, rely=0.5, anchor="center")
            self.reel_labels.append(label)

        if self.loaded_images:
            for label in self.reel_labels:
                label.configure(image=self.loaded_images[0])

        self.result_label = ctk.CTkLabel(
            machine_card,
            text="Ready when you are",
            text_color="#848e9c",
            font=("Arial", 16, "bold"),
            height=32,
        )
        self.result_label.pack(pady=(0, 8))

        self.spin_button = ctk.CTkButton(
            machine_card,
            text="SPIN  ·  SPACE",
            width=240,
            height=50,
            fg_color="#0ecb81",
            hover_color="#0bb878",
            text_color="#0b0e11",
            font=("Arial", 16, "bold"),
            corner_radius=8,
            command=self.lancer_machine,
        )
        self.spin_button.pack(pady=(0, 20))

        self.bind("<space>",lambda x:self.lancer_machine())
        self.bind("<Escape>",lambda x:self.lancer_machine())
        self.focus_set()

        self.temps_1 = 0
        self.temps_2 = 0
        self.temps_3 = 0

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
        self.result_label.configure(
            text="Spinning...",
            text_color="#848e9c",
        )
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
                self.reel_labels[0].configure(image=random.choice(self.loaded_images))
            self.temps_1 -= 80
            self.after(80, self.animer_rouleau_1)
        else:
            if self.loaded_images:
                self.index_final_1 = random.randint(0, len(self.loaded_images) - 1)
                self.reel_labels[0].configure(image=self.loaded_images[self.index_final_1])


    def animer_rouleau_2(self):
        if self.temps_2 > 0:
            if self.loaded_images:
                self.reel_labels[1].configure(image=random.choice(self.loaded_images))
            self.temps_2 -= 80
            self.after(80, self.animer_rouleau_2)
        else:
            # Résultat final pour le rouleau 2
            if self.loaded_images:
                self.index_final_2 = random.randint(0, len(self.loaded_images) - 1)
                self.reel_labels[1].configure(image=self.loaded_images[self.index_final_2])

    def animer_rouleau_3(self):
        if self.temps_3 > 0:
            if self.loaded_images:
                self.reel_labels[2].configure(image=random.choice(self.loaded_images))
            self.temps_3 -= 80
            self.after(80, self.animer_rouleau_3)
        else:
            if self.loaded_images:
                self.index_final_3 = random.randint(0, len(self.loaded_images) - 1)
                self.reel_labels[2].configure(image=self.loaded_images[self.index_final_3])

            self.verify_victory()

    def verify_victory(self):
        if self.index_final_1 == self.index_final_2 == self.index_final_3:
            self.result_label.configure(
                text="JACKPOT!",
                text_color="#0ecb81",
            )
            # Code pour gain argent
        else:
            self.result_label.configure(
                text="NO MATCH - TRY AGAIN",
                text_color="#f6465d",
            )
            # code pour perte argent
        self.machine_running = False
        self.curr = 1
