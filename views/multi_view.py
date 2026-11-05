import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from engine import Engine
from Database import Database

class MultiView(ctk.CTkFrame):
    def __init__(self, master, controller, engine:Engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller
        self.engine = engine
        self.autoUpdate = False
        
        self.connectedView = ConnectedFrame(self,self.engine.database,engine,self.disconnectCallback)
        self.connectedView.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.connectedView.lower()

        self.engine.database.connFailedCallback = self.disconnectCallback

        self.createInitMenu()

    def connectGame(self):
        self.connectedView.tkraise()
        self.engine.hosting = False
        self.engine.database.killDatabase()
        self.engine.database.setHost(False)
        self.engine.database.setUsername(self.usernameEntry.get())
        self.engine.username = self.usernameEntry.get()
        self.engine.database.connectToDatabase(self.codeEntry.get())
        self.after(5000,self.showConnView)

    def disconnectCallback(self):
        self.engine.database.setUsername("host")
        if self.engine.hosting:
            self.engine.database.killDatabase()
        else:
            self.engine.database.disconnect(True)
            self.engine.database.setHost(True)
        self.engine.rebuild()
        self.connectedView.lower()

    def hostGame(self):
        self.engine.database.openRoom()
        self.connectedView.code = self.engine.database.code
        self.after(1000,self.showConnView)

    def showConnView(self):
        self.connectedView.start(self.engine.database.code)
        self.connectedView.tkraise()
        self.connectedView.autoUpdate = True
        self.connectedView.refresh_ui()

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

        self.usernameEntry = ctk.CTkEntry(card, placeholder_text="Enter your name", height=42)
        self.usernameEntry.grid(row=7, column=0, padx=32, pady=(6, 20), sticky="ew")
 
        ctk.CTkLabel(card, text="ROOM CODE", font=("Arial",11,"bold"), text_color="#848e9c").grid(row=8, column=0, padx=32, sticky="w")

        self.codeEntry = ctk.CTkEntry(card, placeholder_text="e.g. stupid-astroid-1", height=42)
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
    def __init__(self, master, database:Database=None, engine:Engine=None, on_disconnect=None):
        super().__init__(master, fg_color="#0b0e11")
        self.database = database
        self.engine = engine
        self.on_disconnect = on_disconnect
        self.code = ""
        self.autoUpdate = False

    def copyCode(self):
        self.clipboard_clear()
        self.clipboard_append(self.code)
        print("Code coppied to clipboard")

    def createConnectedMenu(self):
        self.initframe = ctk.CTkFrame(self, fg_color="#0b0e11")
        self.initframe.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.initframe.grid_columnconfigure(0, weight=1)
        self.initframe.grid_columnconfigure(1, weight=2)
        self.initframe.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(self.initframe, fg_color="#181a20", corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 2))

        self.code_label = ctk.CTkLabel(bar, text=f"Room: {self.code or '------'}", font=("Arial", 20, "bold"))
        self.code_label.pack(side="left", padx=12, pady=8)

        self.status_label = ctk.CTkLabel(bar, text="Connecting...", text_color="#848e9c", font=("Arial", 12))
        self.status_label.pack(side="left", padx=12)

        ctk.CTkButton(bar, text="Copy Room Code", width=100, fg_color="#2b313a",hover_color="#227700", command=self.copyCode).pack(side="left", padx=12, pady=8)

        ctk.CTkButton(bar, text="Disconnect", width=100, fg_color="#2b313a",hover_color="#f6465d", command=self.disconnect,).pack(side="right", padx=12, pady=8)

        players = ctk.CTkFrame(self.initframe, fg_color="#181a20", corner_radius=6)
        players.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=3)

        ctk.CTkLabel(players, text="Players", font=("Arial", 14, "bold")).pack( anchor="w", padx=12, pady=(10, 4))

        self.players_box = ctk.CTkTextbox(players, fg_color="#121418", text_color="#eaecef", font=("Consolas", 12))
        self.players_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        chat = ctk.CTkFrame(self.initframe, fg_color="#181a20", corner_radius=6)
        chat.grid(row=1, column=1, sticky="nsew", padx=(3, 6), pady=3)

        ctk.CTkLabel(chat, text="Live chat", font=("Arial", 14, "bold")).pack(anchor="w", padx=12, pady=(10, 4))
        self.chat_box = ctk.CTkTextbox(chat, fg_color="#121418", text_color="#eaecef", font=("Consolas", 12),state="disabled")
        self.chat_box.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.chat_entry = ctk.CTkEntry(chat, fg_color="#121418",height=48, text_color="#eaecef", font=("Consolas", 12))
        self.chat_entry.pack(side="left",fill="x",expand=True,padx=8, pady=(0, 8))
        self.chat_entry.bind("<Return>", self.sendChat)
        self.chat_send_btn = ctk.CTkButton(chat, text="Send Message", width=100, fg_color="#2b313a",hover_color="#0f5509", command=self.sendChat)
        self.chat_send_btn.pack(side="right", padx=12, pady=8)

    def sendChat(self, event=None):
        if self.engine.hosting:
            self.engine.rawMsgCallback("host",{"type":"raw","data":self.chat_entry.get()})
        else:
            self.database.sendAsClient(self.chat_entry.get())
        
    def start(self, code=""):
        self.code = code
        if not hasattr(self, "initframe"):
            self.createConnectedMenu()
        self.code_label.configure(text=f"Room: {self.code}")
        self.autoUpdate = True
        self.refresh_ui()

    def stop(self):
        self.autoUpdate = False

    def disconnect(self):
        self.stop()
        if self.on_disconnect:
            self.on_disconnect()

    def _set_text(self, box, text):
        box.configure(state="normal")
        box.delete("1.0", "end")
        box.insert("end", text)
        box.configure(state="disabled")

    def refresh_ui(self):
        db = self.database
        if db:
            names = [db.username] + (list(db.connections.keys()) if db.host else [])

            txt = ""
            for n in names:
                txt += f"{n}{' (host)' if db.host and n == db.username else ''}" + "\n"
            self._set_text(self.players_box, txt)
            
            connected = db.host and db.sigRoomRunning or db.canSend
            self.status_label.configure(text="Connected" if connected else "Waiting...",text_color="#0ecb81" if connected else "#848e9c")

            chat = db.get("messages") or []
            txt = ""
            for msg in chat[-40:]:
                txt += msg["username"] + " > " + msg["message"] + "\n"
            self._set_text(self.chat_box, txt)
            self.chat_box.see("end") 

        if self.autoUpdate:
            self.after(1000, self.refresh_ui)