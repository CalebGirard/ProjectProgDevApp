from engine import Engine

import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

# Views

from views.market_view import MarketView
from views.shop_view import ShopView
from views.bank_view import BankView
from views.casino_view import CasinoView
from views.multi_view import MultiView
from views.settings_view import SettingsView


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class MainApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600+0+0")
        self.engine = Engine()
        self.iconbitmap("Assets/snake.ico")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color="black")
        self.title("Pynance Desktop")
        self.menu()
        self.run_clock()


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

        try:
            logo = ctk.CTkImage(
                dark_image=Image.open("Assets/snake.ico"), size=(24, 24)
            )
            casino_pic = ctk.CTkImage(
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
            casino_pic = None
            market_pic = None
            trading_pic = None
            multi_pic = None
            bank_pic = None
            settings = None

        button_style = {
            "text": "",
            "width": 40,
            "height": 40,
            "corner_radius": 8,
            "fg_color": "transparent",
            "hover_color": "#2a2d2e",
        }

        self.menu_bar.grid_rowconfigure(6, weight=1)
        self.logo = ctk.CTkLabel(self.menu_bar, image=logo, text="")
        self.logo.grid(row=0, column=0, padx=8, pady=(8, 20))

        self.btn_casino = ctk.CTkButton(
            self.menu_bar,
            image=casino_pic,
            command=lambda: self.show_frame("Casino"),
            **button_style,
        )
        self.btn_casino.grid(row=3, column=0, padx=8, pady=2)

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
            "Casino": self.btn_casino,
            "Market": self.btn_market,
            "Shop": self.btn_shop,
            "Multi": self.btn_multi,
            "Bank": self.btn_bank,
            "Settings": self.btn_settings,
        }
        self.frames = {}
        self.init_frames()
        self.show_frame("Market")

    def init_frames(self):
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)
        # Map a string key to the respective class
        page_classes = {
            "Casino": CasinoView,
            "Shop": ShopView,
            "Market": MarketView,
            "Bank": BankView,
            "Multi": MultiView,
            "Settings": SettingsView,
        }

        for name, FrameClass in page_classes.items():
            # Instantiate each frame inside self.container
            frame = FrameClass(master=self.container, controller=self, engine=self.engine)
            self.frames[name] = frame

            # Stack all frames into the exact same cell
            frame.grid(row=0, column=0, sticky="nsew")

    def show_frame(self, page_name: str):
        """Brings the requested page to the front without re-creating it."""
        frame = self.frames[page_name]
        frame.tkraise()

        if hasattr(frame, "refresh"):
            frame.refresh()

        for name, button in self.navigation_buttons.items():
            button.configure(
                fg_color="#2d2d30" if name == page_name else "transparent"
            )

    def run_clock(self):
        self.engine.tick()

        market_view = self.frames.get("Market")

        if market_view and market_view.winfo_viewable():
            market_view.refresh()

        self.after(2000, self.run_clock)


    def destroy(self):
        self.quit()

if __name__ == "__main__":
    app = MainApp()
    app.mainloop()