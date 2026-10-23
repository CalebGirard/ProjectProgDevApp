import customtkinter as ctk
import tkinter as tk
from PIL import Image

from casino import Casino

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MainApp(ctk.CTk): 
    def __init__(self):
        super().__init__()
        self.geometry("800x600+0+0")
        self.after(0, lambda:self.state('zoomed'))
        self.configure(fg_color="black")
        self.title("Application Principale")
        self.menu()

    def menu(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="black")
        self.container.grid(row=0, column=0, sticky="nsew")

        self.menu_bar = ctk.CTkFrame(self, height=100, corner_radius=0)
        self.menu_bar.grid(row=1, column=0, sticky="ew")
        for i in range(5):
            self.menu_bar.grid_columnconfigure(i, weight=1)

        try: 
            casino_pic = ctk.CTkImage(dark_image=Image.open("Image/Roulette.png"), size=(80,80))
            market_pic = ctk.CTkImage(dark_image=Image.open("Image/Market.png"), size=(80,80))
            trading_pic = ctk.CTkImage(dark_image=Image.open("Image/Trading.png"), size=(80,80))
            multi_pic = ctk.CTkImage(dark_image=Image.open("Image/Multi.png"), size=(80,80))
            bank_pic = ctk.CTkImage(dark_image=Image.open("Image/Bank.png"), size=(80,80))
        except:
            casino_pic = None
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None

        self.btn_wheel = ctk.CTkButton(self.menu_bar, text="Casino", image=casino_pic, compound="top", command=lambda: self.show_frame("Casino"))
        self.btn_wheel.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
        
        self.btn_market = ctk.CTkButton(self.menu_bar, text="Market", image=market_pic, compound="top", command=lambda: self.show_frame("Market"))
        self.btn_market.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        self.btn_stats = ctk.CTkButton(self.menu_bar, text="Trading", image=trading_pic, compound="top", command=lambda: self.show_frame("Trading"))
        self.btn_stats.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")
        
        self.btn_multi = ctk.CTkButton(self.menu_bar, text="Multi", image=multi_pic, compound="top", command=lambda: self.show_frame("Multi"))
        self.btn_multi.grid(row=0, column=3, padx=5, pady=10, sticky="nsew")
        
        self.btn_bank = ctk.CTkButton(self.menu_bar, text="Bank", image=bank_pic, compound="top", command=lambda: self.show_frame("Bank"))
        self.btn_bank.grid(row=0, column=4, padx=5, pady=10, sticky="nsew")

        self.frames = {}
        self.init_frames()
        self.show_frame("Trading")

    def init_frames(self):
        for F in ("Casino", "Market", "Trading", "Multi", "Bank"):
            frame = ctk.CTkFrame(self.container, fg_color="black")
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.casino_view = Casino(self.frames["Casino"])

        for F in ("Market", "Trading", "Multi", "Bank"):
            label = ctk.CTkLabel(self.frames[F], text=f"Vue : {F}", font=("Arial", 24, "bold"), text_color="LightSkyBlue")
            label.pack(expand=True)


    def show_frame(self, page_name):
        """Fait passer au premier plan la vue demandée"""
        frame = self.frames[page_name]
        frame.tkraise()


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()