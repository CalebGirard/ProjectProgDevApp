import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

# Views

from views.market_view import MarketView

# TODO

# Add proper icons
#
# Add graph visualizer


from casino import Casino

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600+0+0")
        self.iconbitmap("Assets/snake.ico")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color="black")
<<<<<<< HEAD
        self.title("Main Application")
=======
        self.title("Pynance Desktop")
>>>>>>> interface
        self.menu()

    def menu(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.container = ctk.CTkFrame(self, fg_color="black")
        self.container.grid(row=0, column=1, sticky="nsew")

        self.menu_bar = ctk.CTkFrame(
            self, width=56, corner_radius=0, fg_color="#1e1e1e"
        )
        self.menu_bar.grid(row=0, column=0, sticky="ns")
        self.menu_bar.grid_propagate(False)
        self.menu_bar.grid_columnconfigure(0, weight=1)

<<<<<<< HEAD
        try: 
            casino_pic = ctk.CTkImage(dark_image=Image.open("Image/Roulette.png"), size=(80,80))
            market_pic = ctk.CTkImage(dark_image=Image.open("Image/Market.png"), size=(80,80))
            trading_pic = ctk.CTkImage(dark_image=Image.open("Image/Trading.png"), size=(80,80))
            multi_pic = ctk.CTkImage(dark_image=Image.open("Image/Multi.png"), size=(80,80))
            bank_pic = ctk.CTkImage(dark_image=Image.open("Image/Bank.png"), size=(80,80))
        except:
            casino_pic = None
=======
        try:
            logo = ctk.CTkImage(
                dark_image=Image.open("Assets/snake.ico"), size=(24, 24)
            )
            wheel_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/megaphone.png"), size=(24, 24)
            )
            market_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/shopping-cart.png"), size=(24, 24)
            )
            trading_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/globe.png"), size=(24, 24)
            )
            multi_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/users-alt.png"), size=(24, 24)
            )
            bank_pic = ctk.CTkImage(
                dark_image=Image.open("Assets/bank.png"), size=(24, 24)
            )
            settings = ctk.CTkImage(
                dark_image=Image.open("Assets/settings.png"), size=(24, 24)
            )
        except:
            logo = None
            wheel_pic = None
>>>>>>> interface
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None
            settings = None

<<<<<<< HEAD
        self.btn_wheel = ctk.CTkButton(self.menu_bar, text="Casino", fg_color="transparent", image=casino_pic, compound="top", command=lambda: self.show_frame("Casino"))
        self.btn_wheel.grid(row=0, column=0, padx=5, pady=10, sticky="nsew")
        
        self.btn_market = ctk.CTkButton(self.menu_bar, text="Market", fg_color="transparent", image=market_pic, compound="top", command=lambda: self.show_frame("Market"))
        self.btn_market.grid(row=0, column=1, padx=5, pady=10, sticky="nsew")
        
        self.btn_stats = ctk.CTkButton(self.menu_bar, text="Trading", fg_color="transparent", image=trading_pic, compound="top", command=lambda: self.show_frame("Trading"))
        self.btn_stats.grid(row=0, column=2, padx=5, pady=10, sticky="nsew")
        
        self.btn_multi = ctk.CTkButton(self.menu_bar, text="Multi", fg_color="transparent", image=multi_pic, compound="top", command=lambda: self.show_frame("Multi"))
        self.btn_multi.grid(row=0, column=3, padx=5, pady=10, sticky="nsew")
        
        self.btn_bank = ctk.CTkButton(self.menu_bar, text="Bank", fg_color="transparent", image=bank_pic, compound="top", command=lambda: self.show_frame("Bank"))
        self.btn_bank.grid(row=0, column=4, padx=5, pady=10, sticky="nsew")
=======
        button_style = {
            "text": "",
            "width": 40,
            "height": 40,
            "corner_radius": 8,
            "fg_color": "transparent",
            "hover_color": "#2a2d2e",
        }
>>>>>>> interface

        self.menu_bar.grid_rowconfigure(6, weight=1)
        self.logo = ctk.CTkLabel(self.menu_bar, image=logo, text="")
        self.logo.grid(row=0, column=0, padx=8, pady=(8, 20))

        self.btn_wheel = ctk.CTkButton(
            self.menu_bar,
            image=wheel_pic,
            command=lambda: self.show_frame("Wheel"),
            **button_style,
        )
        self.btn_wheel.grid(row=3, column=0, padx=8, pady=2)

        self.btn_shop = ctk.CTkButton(
            self.menu_bar,
            image=market_pic,
            command=lambda: self.show_frame("Shop"),
            **button_style,
        )
        self.btn_shop.grid(row=2, column=0, padx=8, pady=2)

        self.btn_market = ctk.CTkButton(
            self.menu_bar,
            image=trading_pic,
            command=lambda: self.show_frame("Market"),
            **button_style,
        )
        self.btn_market.grid(row=1, column=0, padx=8, pady=2)

        self.btn_multi = ctk.CTkButton(
            self.menu_bar,
            image=multi_pic,
            command=lambda: self.show_frame("Multi"),
            **button_style,
        )
        self.btn_multi.grid(row=4, column=0, padx=8, pady=2)

        self.btn_bank = ctk.CTkButton(
            self.menu_bar,
            image=bank_pic,
            command=lambda: self.show_frame("Bank"),
            **button_style,
        )
        self.btn_bank.grid(row=5, column=0, padx=8, pady=2)

        self.btn_settings = ctk.CTkButton(
            self.menu_bar,
            image=settings,
            command=lambda: self.show_frame("Settings"),
            **button_style,
        )
        self.btn_settings.grid(row=7, column=0, padx=8, pady=10)

        self.navigation_buttons = {
            "Wheel": self.btn_wheel,
            "Market": self.btn_market,
            "Shop": self.btn_shop,
            "Multi": self.btn_multi,
            "Bank": self.btn_bank,
            "Settings": self.btn_settings,
        }
        self.frames = {}
        self.init_frames()
        self.show_frame("Trading")

    def init_frames(self):
<<<<<<< HEAD
        for F in ("Casino", "Market", "Trading", "Multi", "Bank"):
            frame = ctk.CTkFrame(self.container, fg_color="black")
            self.frames[F] = frame
            frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.casino_view = Casino(self.frames["Casino"])

        for F in ("Market", "Trading", "Multi", "Bank"):
            label = ctk.CTkLabel(self.frames[F], text=f"Vue : {F}", font=("Arial", 24, "bold"), text_color="LightSkyBlue")
=======
        frame = ctk.CTkFrame(self.container)
        self.frames["Market"] = frame

        label = ctk.CTkLabel(
            frame, text=f"TODO", font=("Arial", 20, "bold"), text_color="White"
        )
        label.pack(expand=True)

        frame.place(relx=0, rely=0, relwidth=1, relheight=1)

        for F in ("Wheel", "Shop", "Multi", "Bank", "Settings"):
            frame = ctk.CTkFrame(self.container)
            self.frames[F] = frame

            label = ctk.CTkLabel(
                frame, text=f"Vue : {F}", font=("Arial", 20, "bold"), text_color="White"
            )
>>>>>>> interface
            label.pack(expand=True)


    def show_frame(self, page_name):
        """Fait passer au premier plan la vue demandée"""
        frame = self.frames[page_name]
        frame.tkraise()
        for name, button in self.navigation_buttons.items():
            button.configure(fg_color="#2d2d30" if name == page_name else "transparent")

        titles = {
            "Casino": "Application - Royal Casino",
            "Market": "Application - Market",
            "Trading": "Application - Trading",
            "Multi": "Application - Multiplayer",
            "Bank": "Application - Bank"
        }

        self.title(titles.get(page_name, "Main Application"))


if __name__ == "__main__":
    app = MainApp()
    app.mainloop()
