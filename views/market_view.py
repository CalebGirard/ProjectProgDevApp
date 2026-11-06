import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt
from engine import Engine
"""

UI STRUCTURE :

+---------------------------------------------------------------------------------------------+
| TOP BAR: [Ticker Dropdown] | $83,109.38 (+1.48%) | 24h High: $84k | 24h Low: $81k | Cash: $10k|
+----------------------------------------------------+--------------------+--------------------+
|                                                    | MIDDLE (20%):      | RIGHT (25%):       |
|  LEFT (55%):                                       | ORDER BOOK / TICK  | ORDER PANEL        |
|                                                    |                    |                    |
|  - Candlestick Chart (Matplotlib Canvas)           | [ Asks (Red)     ] | [ Buy ]  [ Sell ]  |
|  - Timeframe toggles [1m][5m][1h]                  | ------------------ | ------------------ |
|                                                    | Current Price      | Type: Market/Limit |
|                                                    | ------------------ | Shares / Amount    |
|                                                    | [ Bids (Green)   ] | Slider: 25% 50% 100|
|                                                    |                    | Total: $...        |
|                                                    |                    | [ PLACE ORDER BTN ]|
+----------------------------------------------------+--------------------+--------------------+
| BOTTOM TABS (Height: ~180px):                                                                |
| [ Current Positions ]  [ Active Orders ]  [ News & Breaking Events Feed ]                    |
| > "FED announces interest rate hike: Tech sector drops 4%"                                  |
+---------------------------------------------------------------------------------------------+

"""


class MarketView(ctk.CTkFrame):
    def __init__(self, master, controller, engine:Engine):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        self.engine = engine

        self.current_stock = list(self.engine.market.stocks.values())[
            0
        ]  # Default to the first stock

        # Time views

        self.time_views = {"1W": 7, "1M": 30, "6M": 180, "1Y":365, "ALL": None}
        self.current_time_view = 30

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)  # Main chart row
        self.grid_rowconfigure(2, weight=1)  # News / bottom tabs row

        self.top_bar_builder()
        self.graph_area_builder()
        self.order_panel_builder()
        self.bottom_tabs_builder()
        self.engine.onMarketLoaded = self.reload_stocks

    def reload_stocks(self):
        options = self._get_dropdown_options()
        self.name_select.configure(values=options)
        self.name_select.set(options[0])
        self.switch_data(options[0])

    def _get_dropdown_options(self):
        # Format: "Apple (AAPL)"
        return sorted(
            [f"{s.name} ({s.ticker})" for s in self.engine.market.stocks.values()]
        )

    def switch_data(self, stock_name):
        found = self.engine.market.find_stock_by_long_name(stock_name)
        if found is not None:
            self.current_stock = found
            self.refresh()

    def top_bar_builder(self):
        bar = ctk.CTkFrame(self, fg_color="#181a20", height=48, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 2))

        # Dropdown menu
        options = self._get_dropdown_options()
        self.name_select = ctk.CTkComboBox(
            bar,
            values=options,
            command=self.switch_data,
            fg_color="#2b313a",
            button_color="#363c4e",
            border_width=0,
            width=180,
        )
        self.name_select.set(options[0] if options else "")
        self.name_select.pack(side="left", padx=12, pady=8)

        # Clavier pour l'autocompletion
        self.name_select.bind("<KeyRelease>", self._filter_combobox)
        self.name_select.bind("<Tab>", self._select_first_match)
        self.name_select.bind("<Return>", self._select_first_match)

        # Titre
        self.name = ctk.CTkLabel(
            bar, text="International Market Viewer™", font=("Arial", 20, "bold")
        )
        self.name.pack(side="left", padx=12, pady=8)

        # Stats
        self.price_label = ctk.CTkLabel(
            bar,
            text=f"${self.current_stock.price:.2f}",
            font=("Arial", 16, "bold"),
            text_color="#0ecb81",
        )
        self.price_label.pack(side="left", padx=10)

        self.stat_text = ctk.CTkLabel(
            bar,
            text=f"Last move: {_latest_change_pct(self.current_stock):+.2f}%  |  Market cap: ${number_formatter(self.current_stock.market_cap)} {self.current_stock.currency}",
            font=("Arial", 12),
            text_color="#848e9c",
        )
        self.stat_text.pack(side="left", padx=10)


        # User argent

        self.user_cash = ctk.CTkLabel(
            bar,
            text=f"⭐ {str(self.engine.database.getPath(f"cash:{self.engine.username}"))} $ ⭐",
            font=("Arial", 20, "bold"),
            text_color="#0ecb81",
        )
        self.user_cash.pack(side="right", padx=20)

        

        button_style = {
            "width": 40,
            "height": 40,
            "corner_radius": 8,
            "hover_color": "#2a2d2e",
        }


        # Overlay

        self.time_buttons = {}

        for label, view in self.time_views.items():
            button = ctk.CTkButton(
                bar,
                text=label,
                command=lambda selected_view=view: self.set_current_view(selected_view),
                fg_color=(
                    "#2d2d30" if view == self.current_time_view else "transparent"
                ),
                **button_style,
            )
            button.pack(side="right", padx=5)
            self.time_buttons[label] = button

    def _filter_combobox(self, event):
        if event.keysym in ("Return", "Tab", "Up", "Down", "Left", "Right"):
            return

        query = self.name_select.get().strip().lower()
        all_options = self._get_dropdown_options()

        filtered = [opt for opt in all_options if query in opt.lower()]
        self.name_select.configure(values=filtered if filtered else all_options)

    def set_current_view(self, view):
        self.current_time_view = view
        self._update_time_button_styles()
        self.refresh()

    def _update_time_button_styles(self):
        for label, view in self.time_views.items():
            self.time_buttons[label].configure(
                fg_color=(
                    "#2d2d30" if view == self.current_time_view else "transparent"
                )
            )

    def _select_first_match(self, event):
        """Auto select le premier stock quand le user fait tab"""
        valid_options = self.name_select._values

        if valid_options:
            first_choice = valid_options[0]
            self.name_select.set(first_choice)
            self.switch_data(first_choice)

        return "break"

    def graph_area_builder(self):
        chart_frame = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=6)
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=3)

        self.fig, self.ax = plt.subplots(facecolor="#181a20")

        self.style_chart()

        history, history_start = _history_window(
            self.current_stock.history, self.current_time_view
        )
        previous_close = (
            self.current_stock.history[history_start - 1] if history_start > 0 else None
        )
        candlesticker(self.ax, history, history_start, previous_close)
        self.ax.grid(True, color="#2b313a", linestyle="--", linewidth=0.5)
        self.fig.tight_layout()

        # Sauvegarde du canvas en variable d'instance
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def order_panel_builder(self):
        panel = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=6)
        panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(3, 6), pady=3)

        ctk.CTkLabel(
            panel,
            text="MARKET PULSE",
            text_color="#eaecef",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=14, pady=(14, 8))

        breadth_card = ctk.CTkFrame(panel, fg_color="#121418", corner_radius=8)
        breadth_card.pack(fill="x", padx=12, pady=(0, 12))

        ctk.CTkLabel(
            breadth_card,
            text="MARKET BREADTH",
            text_color="#848e9c",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", padx=10, pady=(8, 2))
        self.market_breadth_label = ctk.CTkLabel(
            breadth_card,
            text="",
            text_color="#eaecef",
            font=("Arial", 12, "bold"),
        )
        self.market_breadth_label.pack(anchor="w", padx=10)
        self.market_breadth_bar = ctk.CTkProgressBar(
            breadth_card,
            height=6,
            fg_color="#f6465d",
            progress_color="#0ecb81",
        )
        self.market_breadth_bar.pack(fill="x", padx=10, pady=(6, 9))

        ctk.CTkLabel(
            panel,
            text="TOP MOVERS · YESTERDAY",
            text_color="#848e9c",
            font=("Arial", 10, "bold"),
        ).pack(anchor="w", padx=14, pady=(0, 4))
        self.mover_buttons = []
        for _ in range(4):
            button = ctk.CTkButton(
                panel,
                text="",
                anchor="w",
                height=30,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#2b313a",
                font=("Consolas", 11),
            )
            button.pack(fill="x", padx=10, pady=1)
            self.mover_buttons.append(button)

        # Buy / Sell Toggle Buttons
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)

        buy_btn = ctk.CTkButton(
            btn_row,
            text="Buy",
            fg_color="#0ecb81",
            hover_color="#0ba367",
            width=100,
            command=lambda: self.sales_or_buys_executer(1000),
        )
        buy_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        sell_btn = ctk.CTkButton(
            btn_row,
            text="Sell",
            fg_color="#f6465d",
            hover_color="#f6465d",
            width=100,
            command=lambda: self.sales_or_buys_executer(-1000),
        )
        sell_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Clavier
        ctk.CTkLabel(
            panel, text="Amount (Shares)", text_color="#848e9c", font=("Arial", 11)
        ).pack(anchor="w", padx=14, pady=(10, 0))
        self.amount_entry = ctk.CTkEntry(
            panel, placeholder_text="0", fg_color="#2b313a", border_width=0
        )
        self.amount_entry.pack(fill="x", padx=12, pady=4)

        self.slider = ctk.CTkSlider(
            panel, from_=0, to=100, number_of_steps=4, button_color="#0ecb81"
        )
        self.slider.pack(fill="x", padx=12, pady=12)

        self._refresh_market_pulse()


    # Ventes et achats

    def sales_or_buys_executer(self, x):
        user_cash = self.engine.database.getPath(f"cash:{self.engine.username}")
        spending = user_cash - x * self.current_stock.price

        if user_cash > spending:
            return
        
        self.engine.database.setPath(f"cash:{self.engine.username}", spending)
        if x <= 0:
            if self.engine.hosting:
                self.current_stock.sell(abs(x))
                return
            else:
                self.engine.database.sendAsClient("/sell "+self.current_stock.ticker+" "+str(abs(x)))
                return
        if self.engine.hosting:
            self.current_stock.buy(x)
        else:
            self.engine.database.sendAsClient("/buy "+self.current_stock.ticker+" "+str(x))

    def bottom_tabs_builder(self):
        # Scrollable events feed
        self.news_box = ctk.CTkTextbox(
            self, fg_color="#121418", text_color="#eaecef", font=("Consolas", 11)
        )
        self.news_box.grid(row=2, column=0, sticky="nsew", padx=(6, 3), pady=(3, 6))
        self.news_box.configure(state="disabled")

    def refresh(self):
        self.price_label.configure(text=f"${self.current_stock.price:.2f}")
        self.stat_text.configure(
            text=f"Last move: {_latest_change_pct(self.current_stock):+.2f}%  |  Market cap: ${number_formatter(self.current_stock.market_cap)} {self.current_stock.currency}"
        )
        self._refresh_market_pulse()

        next_event = self.engine.database.get("next_event")
        if getattr(self.engine, "hosting", False) and self.engine.eventer.event_list:
            event = self.engine.eventer.event_list[0]
            next_event = {
                "headline": event["headline"],
                "scope": event["scope"],
                "play_probability": event["play_probability"]
            }

        self.news_box.configure(state="normal")
        self.news_box.delete("1.0", "end")
        if next_event:
            self.news_box.insert(
                "end",
                f"{next_event['scope'].upper()} - "
                f"{next_event['headline']}\n"
            )
        else:
            self.news_box.insert("end", "No event is queued yet.\n")
        self.news_box.configure(state="disabled")

        # Refresh le graphique
        self.ax.clear()

        self.style_chart()

        history, history_start = _history_window(
            self.current_stock.history, self.current_time_view
        )
        previous_close = (
            self.current_stock.history[history_start - 1] if history_start > 0 else None
        )
        candlesticker(self.ax, history, history_start, previous_close)
        self.ax.grid(True, color="#2b313a", linestyle="--", linewidth=0.5)

        self.fig.tight_layout()

        cash = self.engine.database.getPath(f"cash:{self.engine.username}")
        cash = number_formatter(cash) if cash else "ERROR"
        self.user_cash.configure(text=f"⭐ {cash} $ ⭐")
        self.canvas.draw()

    def _refresh_market_pulse(self):
        stocks = list(self.engine.market.stocks.values())
        changes = [(stock, _latest_change_pct(stock)) for stock in stocks]
        advancing = sum(change > 0 for _, change in changes)
        declining = sum(change < 0 for _, change in changes)
        unchanged = len(changes) - advancing - declining

        breadth_text = f"{advancing} up  ·  {declining} down"
        if unchanged:
            breadth_text += f"  ·  {unchanged} flat"
        self.market_breadth_label.configure(text=breadth_text)
        self.market_breadth_bar.set(advancing / len(changes) if changes else 0)

        movers = sorted(changes, key=lambda item: abs(item[1]), reverse=True)
        for button, (stock, change) in zip(self.mover_buttons, movers):
            button.configure(
                text=f"{stock.ticker:<6} {stock.price:>9,.2f} {change:+6.2f}%",
                text_color="#0ecb81" if change >= 0 else "#f6465d",
                command=lambda selected=stock: self.switch_data(
                    f"{selected.name} ({selected.ticker})"
                ),
            )

    def style_chart(self):
        self.ax.set_facecolor("#181a20")
        self.ax.tick_params(colors="#848e9c", labelsize=9)
        for spine in self.ax.spines.values():
            spine.set_color("#2b313a")

    def reset(self):
        self.current_stock = list(self.engine.market.stocks.values())[0]
        
        new_options = self.engine.market.get_names()
        self.name_select.configure(values=new_options)
        self.name_select.set(new_options[0] if new_options else "")
        
        self.refresh()


def number_formatter(valeur):
    valeur = float(valeur)
    if valeur >= 1e12:
        return f"{valeur / 1e12:.2f}T"
    if valeur >= 1e9:
        return f"{valeur / 1e9:.2f}B"
    elif valeur >= 1e6:
        return f"{valeur / 1e6:.2f}M"
    elif valeur >= 1e3:
        return f"{valeur / 1e3:.2f}k"
    return str(valeur)


MAX_CANDLES = 100


def _latest_change_pct(stock):
    if len(stock.history) < 2 or stock.history[-2] <= 0:
        return 0.0
    return (stock.history[-1] - stock.history[-2]) / stock.history[-2] * 100


def _history_window(history, time_view):
    if time_view is None:
        return history, 0
    start = max(0, len(history) - time_view)
    return history[start:], start


def candlesticker(ax, prices, start_index=0, previous_close=None):
    candle_sizer = max(1, (len(prices) + MAX_CANDLES - 1) // MAX_CANDLES)

    for start in range(0, len(prices), candle_sizer):
        samples = prices[start : start + candle_sizer]
        opening = (
            previous_close
            if start == 0 and previous_close is not None
            else prices[start - 1] if start > 0 else samples[0]
        )
        closing = samples[-1]
        high = max(max(samples), opening)
        low = min(min(samples), opening)
        color = "#0ecb81" if closing >= opening else "#f6465d"
        x = start_index + start + (len(samples) - 1) / 2

        ax.plot([x, x], [low, high], color=color, linewidth=1)
        ax.add_patch(
            Rectangle(
                (
                    x - len(samples) * 0.3,
                    min(opening, closing),
                ),
                len(samples) * 0.6,
                abs(closing - opening),
                facecolor=color,
                edgecolor=color,
                linewidth=1,
            )
        )
    if prices:
        ax.set_xlim(start_index - 0.5, start_index + len(prices) - 0.5)
    ax.set_xlabel(f"{candle_sizer} samples per candle", color="#848e9c")
