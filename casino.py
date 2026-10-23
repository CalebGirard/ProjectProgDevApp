import customtkinter as ctk
import tkinter as tk
from PIL import Image

class Casino(ctk.CTkFrame) :
    def __init__(self, master):
        super().__init__(master, fg_color="black")
        self.pack(fill="both", expand=True)
        self.create_selecter()

    def create_selecter(self):
        self.menu_casino = ctk.CTkFrame(self, fg_color="black")
        self.menu_casino.pack(fill="both", expand=True)

        try: 
            wheel_pic = ctk.CTkImage(dark_image=Image.open("Image/Roulette.png"), size=(80,80))
            market_pic = ctk.CTkImage(dark_image=Image.open("Image/Market.png"), size=(80,80))
            trading_pic = ctk.CTkImage(dark_image=Image.open("Image/Trading.png"), size=(80,80))
            multi_pic = ctk.CTkImage(dark_image=Image.open("Image/Multi.png"), size=(80,80))
            bank_pic = ctk.CTkImage(dark_image=Image.open("Image/Bank.png"), size=(80,80))
        except:
            wheel_pic = None
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None

        self.btn_wheel = ctk.CTkButton(self.menu_casino, text="Casino", image=wheel_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_wheel.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
                
        self.btn_market = ctk.CTkButton(self.menu_casino, text="Market", image=market_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_market.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
                
        self.btn_stats = ctk.CTkButton(self.menu_casino, text="Trading", image=trading_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_stats.grid(row=1, column=0, padx=5, pady=10, sticky="nsew")
                
        self.btn_multi = ctk.CTkButton(self.menu_casino, text="Multi", image=multi_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_multi.grid(row=1, column=1, padx=5, pady=10, sticky="nsew")
                
        self.btn_bank = ctk.CTkButton(self.menu_casino, text="Bank", image=bank_pic, compound="top", command=lambda: print("ta mere"))
        self.btn_bank.grid(row=2, column=0, padx=5, pady=10, sticky="nsew")