import customtkinter as ctk
import tkinter as tk
from PIL import Image
import random
from assets import Assets

class CasinoView(ctk.CTkFrame) :
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.casino_frames = {}
        self.create_selecter()
        self.assets = Assets("Assets")

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
                dark_image=Image.open(self.assets.getAssetPath("roulette.png")),
                size=(180, 180),
            )
            slot_pic = ctk.CTkImage(
                dark_image=Image.open(self.assets.getAssetPath("SlotMachine.png")),
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
            command=self.open_roulette,
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
        self.roulette_view = Roulette(self.container_casino, back_callback=self.return_menu)
        self.roulette_view.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.roulette_view.lower()

        self.slot_view = SlotMachine(self.container_casino, back_callback=self.return_menu)
        self.slot_view.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.slot_view.lower()

    def open_roulette(self):
        """Roulette premier plan"""
        self.roulette_view.tkraise()

    def open_slot_machine(self):
        """Machine à sous premier plan"""
        self.slot_view.tkraise()

    def return_menu(self):
        """Casino premier plan"""
        self.menu_casino.tkraise()

class Roulette(ctk.CTkFrame):
    def __init__(self, master, back_callback=None):
        super().__init__(master, fg_color="black")
        #self.pack(fill="both", expand=True)

        if back_callback:
            self.btn_back = ctk.CTkButton(self, text="Retour Casino", command=back_callback, width=120, height=35, fg_color="gray30",hover_color="gray40")
            self.btn_back.place(x=20, y=20)

        self.spinning = False
        self.angle_actuel = 0

        self.roulette_wheel = [("Green", "0"), ("Red", "32"), ("Black", "15"), ("Red", "19"), ("Black", "4"),
            ("Red", "21"), ("Black", "2"), ("Red", "25"), ("Black", "17"), ("Red", "34"),
            ("Black", "6"), ("Red", "27"), ("Black", "13"), ("Red", "36"), ("Black", "11"),
            ("Red", "30"), ("Black", "8"), ("Red", "23"), ("Black", "10"), ("Red", "5"),
            ("Black", "24"), ("Red", "16"), ("Black", "33"), ("Red", "1"), ("Black", "20"),
            ("Red", "14"), ("Black", "31"), ("Red", "9"), ("Black", "22"), ("Red", "18"),
            ("Black", "29"), ("Red", "7"), ("Black", "28"), ("Red", "12"), ("Black", "35"),
            ("Red", "3"), ("Black", "26")]

        try:
            self.original_image = Image.open("Assets/Casino/Roulette/Roulette.png").resize((300, 300), Image.Resampling.LANCZOS)
        except:
            self.original_image = Image.new("RGBA", (300, 300), (34, 139, 34, 255))

        self.wheel_container = ctk.CTkFrame(self, fg_color="transparent")
        self.wheel_container.pack(pady=20)

        self.lbl_pointer = ctk.CTkLabel(self.wheel_container, text="▼", font=("Arial", 24, "bold"), text_color="yellow")
        self.lbl_pointer.pack(pady=(0, 5))

        self.wheel_label = ctk.CTkLabel(self.wheel_container, text="")
        self.wheel_label.pack()
        self.update_wheel_image(0)

        self.lbl_instruction = ctk.CTkLabel(self, text="Clic on SPACE", font=("Arial", 22, "bold"), text_color="white")
        self.lbl_instruction.pack(pady=5)

        self.lbl_result = ctk.CTkLabel(self, text="", font=("Arial", 28, "bold"))
        self.lbl_result.pack(pady=10)

        self.bind("<space>", lambda x: self.lancer_roulette())
        self.focus_set()

    def update_wheel_image(self, angle):
        """Pivote l'image originale"""
        rotated_img = self.original_image.rotate(angle, resample=Image.Resampling.NEAREST, expand=False)
        self.ctk_image = ctk.CTkImage(dark_image=rotated_img, size=(300, 300))
        self.wheel_label.configure(image=self.ctk_image)

    def lancer_roulette(self):
        if self.spinning:
            return
        
        self.spinning = True
        self.lbl_result.configure(text="")

        winning_index = random.randint(0, len(self.roulette_wheel) - 1)
        self.winning_color, self.winning_number = self.roulette_wheel[winning_index]

        degrees_per_pocket = 360 / len(self.roulette_wheel)
        target_relative_angle = winning_index * degrees_per_pocket

        tours_complets = 360 * 3

        current_mod = self.angle_actuel % 360
        extra_degrees = (target_relative_angle - current_mod) % 360
        self.degrees_left = tours_complets + extra_degrees

        self.animer_etape()

    def animer_etape(self):
        if self.degrees_left > 0.5:
            pas = max(self.degrees_left / 10, 1)
            self.angle_actuel += pas
            self.degrees_left -= pas

            self.update_wheel_image(self.angle_actuel % 360)
            self.after(15, self.animer_etape)
        else:
            # Fin de l'animation : on cale l'image pile sur la case gagnante
            winning_index = next(i for i, (col, num) in enumerate(self.roulette_wheel) if num == self.winning_number and col == self.winning_color)
            degrees_per_pocket = 360 / len(self.roulette_wheel)
            
            self.angle_actuel = winning_index * degrees_per_pocket
            self.update_wheel_image(self.angle_actuel)
            
            self.afficher_resultat_final(self.winning_color, self.winning_number)
            self.spinning = False

    def afficher_resultat_final(self, color, number):
        text_color = "red" if color == "Red" else ("green" if color == "Green" else "white")
        self.lbl_result.configure(text=f"Résultat : {number} ({color})", text_color=text_color)


class SlotMachine(ctk.CTkFrame):
    def __init__(self, master, back_callback=None):
        super().__init__(master, fg_color="#0b0e11")
        self.machine_running = False
        self.curr = 1
<<<<<<< HEAD
        self.back_callback = back_callback

        self.assets = Assets("Assets")

        img_list = ["7.png","black-hole.png","cherries.png","diamond.png","blossom.png","crown.png","dvd-player.png","gem.png","honeycomb.png"]

        self.image_paths = self.assets.getAssetPathList(img_list)

=======
            
        self.image_paths = ["Assets/Casino/SlotMachine/7.png", "Assets/Casino/SlotMachine/black-hole.png",
                             "Assets/Casino/SlotMachine/cherries.png", "Assets/Casino/SlotMachine/diamond.png",
                             "Assets/Casino/SlotMachine/blossom.png","Assets/Casino/SlotMachine/crown.png",
                             "Assets/Casino/SlotMachine/dvd-player.png","Assets/Casino/SlotMachine/gem.png",
                             "Assets/Casino/SlotMachine/honeycomb.png"]
        
>>>>>>> 8c164602a2a08f09f1d0e81de7183027bce9fa24
        self.loaded_images = []
        for path in self.image_paths:
            with Image.open(path) as symbol:
                self.loaded_images.append(
                    ctk.CTkImage(dark_image=symbol.copy(), size=(160, 160))
                )

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=28, pady=(18, 8))
        if back_callback is not None:
            self.btn_back = ctk.CTkButton(
                header,
                text="Retour Casino",
                command=back_callback,
                width=120,
                height=35,
                fg_color="gray30",
                hover_color="gray40",
            )
            self.btn_back.pack(side="left")
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
