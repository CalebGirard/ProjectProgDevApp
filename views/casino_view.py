import customtkinter as ctk
import tkinter as tk
from PIL import Image
import random

class CasinoView(ctk.CTkFrame) :
    def __init__(self, master, controller, engine):
        super().__init__(master, fg_color="black")
        self.controller = controller
        self.pack(fill="both", expand=True)
        self.casino_frames = {}
        self.create_selecter()

    def create_selecter(self):
        self.container_casino = ctk.CTkFrame(self, fg_color="black")
        self.container_casino.pack(fill="both", expand=True)
        
        self.menu_casino = ctk.CTkFrame(self.container_casino, fg_color="black")
        self.menu_casino.pack(fill="both", expand=True)

        try: 
            wheel_pic = ctk.CTkImage(dark_image=Image.open("Assets/Casino/roulette.png"), size=(320,320))
            slot_pic = ctk.CTkImage(dark_image=Image.open("Assets/Casino/SlotMachine.png"), size=(320,320))
        except:
            wheel_pic = None
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None

        self.btn_wheel = ctk.CTkButton(self.menu_casino, text="Roulette", fg_color="transparent", image=wheel_pic, compound="top", command=self.open_roulette)
        self.btn_wheel.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
                
        self.btn_market = ctk.CTkButton(self.menu_casino, text="Slot machine", fg_color="transparent", image=slot_pic, compound="top", command=self.open_slot_machine)
        self.btn_market.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")

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
            self.btn_back = ctk.CTkButton(self, text="← Retour Casino", command=back_callback, width=120, height=35, fg_color="gray30",hover_color="gray40")
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
        super().__init__(master, fg_color="black")
        #self.pack(fill="both", expand=True)
        self.machine_running = False
        self.curr = 1

        if back_callback:
            self.btn_back = ctk.CTkButton(self, text="← Retour Casino", command=back_callback, width=120, height=35, fg_color="gray30",hover_color="gray40")
            self.btn_back.place(x=20, y=20)

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
            self.result_label.configure(text="YIPEEEEEE!!!", text_color="green")
            # Code pour gain argent
        else:
            self.result_label.configure(text="Stupid Loser :()", text_color="red")
            # code pour perte argent
        self.machine_running = False
        self.curr = 1
