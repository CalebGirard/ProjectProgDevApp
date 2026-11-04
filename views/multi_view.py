import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from engine import Engine

class MultiView(ctk.CTkFrame):
    def __init__(self, master, controller, engine:Engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.engine = engine
        self.autoUpdate = False
        
        self.connectedView = ConnectedFrame(self)
        self.connectedView.lower()

        self.createInitMenu()

    def connectGame(self):
        self.connectedView.tkraise()
        self.engine.hosting = False
        self.engine.database.killDatabase()
        self.engine.database.setHost(False)
        self.engine.database.setUsername(self.usernameEntry.get())
        self.engine.database.connectToDatabase(self.codeEntry.get())
        self.after(5000,self.showConnView)

    def hostGame(self):
        self.engine.database.openRoom()
        self.after(1000,self.showConnView)

    def showConnView(self):
        self.connectedView.tkraise()
        self.connectedView.autoUpdate = True
        self.connectedView.update()

    def createInitMenu(self):
        self.initframe = ctk.CTkFrame(self, fg_color="#0b0e11")
        self.initframe.place(relx=0, rely=0, relwidth=1, relheight=1)
 
        # Centered card
        card = ctk.CTkFrame(
            self.initframe,
            fg_color="#161a1e",
            corner_radius=16,
            border_width=1,
            border_color="#2b3139",
            width=520,
            height=520
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.grid_propagate(False)
        card.grid_columnconfigure(0, weight=1)
 
        ctk.CTkLabel(card, text="Multiplayer", font=("Arial",18,"bold"), text_color="#eaecef").grid(row=0, column=0, padx=32, pady=(32, 2), sticky="w")
        ctk.CTkLabel(card, text="Host a room or join a friend's game.",font=("Arial",13), text_color="#848e9c").grid(row=1, column=0, padx=32, pady=(0, 24), sticky="w")

        self.hostButton = ctk.CTkButton(
            card, text="Host Game", 
            font=("Arial",14,"bold"), 
            height=46, 
            corner_radius=10,
            fg_color="#f0b90b", 
            text_color="#0b0e11",
            command=self.hostGame,
        )
        self.hostButton.grid(row=4, column=0, padx=32, sticky="ew")

        divider = ctk.CTkFrame(card, fg_color="transparent")
        divider.grid(row=5, column=0, padx=32, pady=20, sticky="ew")
        divider.grid_columnconfigure((0, 2), weight=1)

        ctk.CTkFrame(divider, height=1, fg_color="#2b3139").grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(divider, text="OR", font=("Arial",11,"bold"), text_color="#848e9c").grid(row=0, column=1, padx=12)

        ctk.CTkFrame(divider, height=1, fg_color="#2b3139").grid(row=0, column=2, sticky="ew")

        ctk.CTkLabel(card, text="USERNAME", font=("Arial",11,"bold"), text_color="#848e9c").grid(row=6, column=0, padx=32, sticky="w")

        self.usernameEntry = ctk.CTkEntry(card, placeholder_text="e.g. AB12CD", height=42)
        self.usernameEntry.grid(row=7, column=0, padx=32, pady=(6, 20), sticky="ew")
 
        ctk.CTkLabel(card, text="ROOM CODE", font=("Arial",11,"bold"), text_color="#848e9c").grid(row=8, column=0, padx=32, sticky="w")

        self.codeEntry = ctk.CTkEntry(card, placeholder_text="Enter your name", height=42)
        self.codeEntry.grid(row=9, column=0, padx=32, pady=(6, 14), sticky="ew")
 
        self.joinButton = ctk.CTkButton(
            card, text="Join Game", font=("Arial",14,"bold"), height=46, corner_radius=10,
            fg_color="#0ecb81", text_color="#0b0e11",
            command=self.connectGame,
        )
        self.joinButton.grid(row=10, column=0, padx=32, sticky="ew")
 
        self.usernameEntry.bind("<Return>", lambda e: self.codeEntry.focus())
        self.codeEntry.bind("<Return>", lambda e: self.connectGame())

class ConnectedFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color="#0b0e11")

        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)     # Main chart row
        self.grid_rowconfigure(2, weight=1)     # News / bottom tabs row

        self.autoUpdate = False
        
    def update(self):

        if self.autoUpdate:
            self.after(1000,self.update)