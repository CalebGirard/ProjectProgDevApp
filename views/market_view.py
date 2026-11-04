import customtkinter as ctk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

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
    def __init__(self, master, controller):
        super().__init__(master, fg_color="#0b0e11")
        self.controller = controller

        # Grid configuration
        self.grid_columnconfigure(0, weight=3)  # Chart + News
        self.grid_columnconfigure(1, weight=1)  # Order execution panel
        self.grid_rowconfigure(1, weight=3)     # Main chart row
        self.grid_rowconfigure(2, weight=1)     # News / bottom tabs row

        self._build_top_bar()
        self._build_chart_area()
        self._build_order_panel()
        self._build_bottom_tabs()

    def _build_top_bar(self):
        bar = ctk.CTkFrame(self, fg_color="#181a20", height=48, corner_radius=0)
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 2))


        # Ticker names
        self.ticker_select = ctk.CTkOptionMenu(
            bar, values=["AAPL", "AVY", "BTC-USD", "MSFT"],
            fg_color="#2b313a", button_color="#363c4e", width=120
        )
        self.ticker_select.pack(side="left", padx=12, pady=8)

        self.name = ctk.CTkLabel(bar, text="International Market Viewer™", font=("Arial", 20, "bold"))
        self.name.pack(side="left", padx=12, pady=8)

        # Quick Stats
        self.price_label = ctk.CTkLabel(
            bar, text="$215.40", font=("Arial", 16, "bold"), text_color="#0ecb81"
        )
        self.price_label.pack(side="left", padx=10)

        stat_text = ctk.CTkLabel(
            bar, text="24h Change: +2.4%   |   Vol: $1.2M", 
            font=("Arial", 12), text_color="#848e9c"
        )
        stat_text.pack(side="left", padx=15)
        
    def _build_chart_area(self):
        chart_frame = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=6)
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=(6, 3), pady=3)

        # Embedded Matplotlib Figure
        fig, ax = plt.subplots(figsize=(6, 4), facecolor="#181a20")
        ax.set_facecolor("#181a20")
        ax.tick_params(colors="#848e9c", labelsize=9)
        for spine in ax.spines.values():
            spine.set_color("#2b313a")
        
        # Test line (replace with candlestick drawing logic)
        ax.plot([1, 2, 3, 4], [210, 212, 209, 215.4], color="#0ecb81", linewidth=1.8)
        ax.grid(True, color="#2b313a", linestyle="--", linewidth=0.5)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=4, pady=4)

    def _build_order_panel(self):
        panel = ctk.CTkFrame(self, fg_color="#181a20", corner_radius=6)
        panel.grid(row=1, column=1, rowspan=2, sticky="nsew", padx=(3, 6), pady=3)

        # Buy / Sell Toggle Buttons
        btn_row = ctk.CTkFrame(panel, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=12)

        buy_btn = ctk.CTkButton(btn_row, text="Buy", fg_color="#0ecb81", hover_color="#0ba367", width=100)
        buy_btn.pack(side="left", expand=True, fill="x", padx=(0, 4))

        sell_btn = ctk.CTkButton(btn_row, text="Sell", fg_color="#2b313a", hover_color="#f6465d", width=100)
        sell_btn.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Inputs
        ctk.CTkLabel(panel, text="Amount (Shares)", text_color="#848e9c", font=("Arial", 11)).pack(anchor="w", padx=14, pady=(10, 0))
        self.amount_entry = ctk.CTkEntry(panel, placeholder_text="0", fg_color="#2b313a", border_width=0)
        self.amount_entry.pack(fill="x", padx=12, pady=4)

        # Quick slider (0% -> 100% of buying power)
        self.slider = ctk.CTkSlider(panel, from_=0, to=100, number_of_steps=4, button_color="#0ecb81")
        self.slider.pack(fill="x", padx=12, pady=12)

        # Execute Button
        exec_btn = ctk.CTkButton(
            panel, text="Place Buy Order", fg_color="#0ecb81", hover_color="#0ba367",
            font=("Arial", 13, "bold"), height=36
        )
        exec_btn.pack(side="bottom", fill="x", padx=12, pady=16)

    def _build_bottom_tabs(self):


        # Scrollable events feed
        news_box = ctk.CTkTextbox(self, fg_color="#121418", text_color="#eaecef", font=("Consolas", 11))
        news_box.grid(row=2, column=0, sticky="nsew", padx=(6, 3), pady=(3, 6))
        news_box.insert("end", "[10:14:02] EVENT: Tech sector rally pushes AAPL past resistance.\n")
        news_box.insert("end", "[10:11:45] BREAKING: Central Bank holds rates steady.\n")
        news_box.configure(state="disabled")