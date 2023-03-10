import tkinter as tk
from interface.styling import *
import typing
from models import *
from interface.autocomplete_widget import AutoComplete
from interface.scrollable_frame import ScrollableFrame
from database import WorkspaceData
import config
from binance.um_futures import UMFutures


class WatchList(tk.Frame):
    def __init__(self, binance_contracts: typing.Dict[str, Contract], *args, **kwargs):
        # def __init__(self, binance_contracts: typing.Dict[str, Contract], bitmex_contracts: typing.Dict[str, Contract], *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = WorkspaceData()

        self.binance_symbols = list(binance_contracts.keys())
        # self.bitmex_symbols = list(bitmex_contracts.keys())

        self._commands_frame = tk.Frame(self, bg=BG_COLOR)
        self._commands_frame.pack(side=tk.TOP)

        self._table_frame = tk.Frame(self, bg=BG_COLOR)
        self._table_frame.pack(side=tk.TOP)

        self._binance_label = tk.Label(
            self._commands_frame, text="Binance", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        self._binance_label.grid(row=0, column=0)

        self._binance_entry = AutoComplete(self.binance_symbols, self._commands_frame, fg=FG_COLOR, justify=tk.CENTER,
                                           insertbackground=FG_COLOR, bg=BG_COLOR_2)

        self._binance_entry.bind("<Return>", self._add_binance_symbol)
        self._binance_entry.grid(row=1, column=0)

        # self._bitmex_label = tk.Label(self._commands_frame, text="Bitmex", bg=BG_COLOR, fg=FG_COLOR, font=BOLD_FONT)
        # self._bitmex_label.grid(row=0, column=1)

        # self._bitmex_entry = AutoComplete(self.bitmex_symbols, self._commands_frame, fg=FG_COLOR, justify=tk.CENTER,
        #                                   insertbackground=FG_COLOR, bg=BG_COLOR_2)
        # self._bitmex_entry.bind("<Return>", self._add_bitmex_symbol)
        # self._bitmex_entry.grid(row=1, column=1)

        self.body_widgets = dict()

        self._headers = ["symbol", "exchange", "bid", "ask", "remove", "buy", "sell"]
        self._headers_frame = tk.Frame(self._table_frame, bg=BG_COLOR)

        self._col_width = 11

        for idx, h in enumerate(self._headers):
            header = tk.Label(self._headers_frame, text=h.capitalize() if h != "Remove" else "",
                              bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT, width=self._col_width)
            header.grid(row=0, column=idx)

        # header = tk.Label(self._headers_frame, text="",
        #                   bg=BG_COLOR, fg=FG_COLOR, font=GLOBAL_FONT, width=2)
        # header.grid(row=0, column=len(self._headers))

        self._headers_frame.pack(side=tk.TOP, anchor="nw")

        self._body_frame = ScrollableFrame(self, bg=BG_COLOR, height=250)
        self._body_frame.pack(side=tk.TOP, anchor="nw", fill=tk.X)

        for h in self._headers:
            self.body_widgets[h] = dict()
            if h in ["bid", "ask"]:
                self.body_widgets[h + "_var"] = dict()
                self.body_widgets[h + "_var"] = dict()

        self._body_index = 1

        saved_symbols = self.db.get("watchlist")
        for s in saved_symbols:
            self._add_symbol(s['symbol'], s['exchange'])

    def _remove_symbol(self, b_index: int):
        for h in self._headers:
            self.body_widgets[h][b_index].grid_forget()
            del self.body_widgets[h][b_index]

    def _buy_symbol(self, b_index: int):
        list_symbol = []
        um_futures_client = UMFutures()

        print(um_futures_client.time())

        um_futures_client = UMFutures(key=config.FUTURES_API_KEY,
                                      secret=config.FUTURES_API_SECRET, base_url='https://testnet.binancefuture.com')
        
        saved_symbols = self.db.get("watchlist")
        for h in saved_symbols:
            list_symbol += [h['symbol']]

        print(list_symbol)
        print("buy symbol", list_symbol[b_index-1])
        params = {
            'symbol': list_symbol[b_index-1],
            'side': 'BUY',
            'type': 'MARKET',
            'quantity': 0.002,
        }

        response = um_futures_client.new_order(**params)
        print(response)
    def _sell_symbol(self, b_index: int):
        list_symbol = []
        um_futures_client = UMFutures()

        print(um_futures_client.time())

        um_futures_client = UMFutures(key=config.FUTURES_API_KEY,
                                      secret=config.FUTURES_API_SECRET, base_url='https://testnet.binancefuture.com')
        
        saved_symbols = self.db.get("watchlist")
        for h in saved_symbols:
            list_symbol += [h['symbol']]

        print(list_symbol)
        print("buy symbol", list_symbol[b_index-1])
        params = {
            'symbol': list_symbol[b_index-1],
            'side': 'SELL',
            'type': 'MARKET',
            'quantity': 0.002,
        }

        response = um_futures_client.new_order(**params)
        print(response)

    # TODO: Instead of en entry box, it may be better to use tk.OptionMenu... we already have the keys list above.
    # using select box may eliminate typing mistakes or upper-lower case mistakes

    def _add_binance_symbol(self, event):
        symbol = event.widget.get()

        if symbol in self.binance_symbols:
            self._add_symbol(symbol, "Binance")
            event.widget.delete(0, tk.END)

    # def _add_bitmex_symbol(self, event):
    #     symbol = event.widget.get()

    #     if symbol in self.bitmex_symbols:
    #         self._add_symbol(symbol, "Bitmex")
    #         event.widget.delete(0, tk.END)

    def _add_symbol(self, symbol: str, exchange: str):
        b_index = self._body_index

        self.body_widgets["symbol"][b_index] = tk.Label(self._body_frame.sub_frame, text=symbol, bg=BG_COLOR,
                                                        fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)

        self.body_widgets["symbol"][b_index].grid(row=b_index, column=0)

        self.body_widgets["exchange"][b_index] = tk.Label(self._body_frame.sub_frame, text=exchange, bg=BG_COLOR,
                                                          fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets["exchange"][b_index].grid(row=b_index, column=1)

        self.body_widgets["bid_var"][b_index] = tk.StringVar()
        self.body_widgets["bid"][b_index] = tk.Label(self._body_frame.sub_frame,
                                                     textvariable=self.body_widgets["bid_var"][b_index], bg=BG_COLOR,
                                                     fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets["bid"][b_index].grid(row=b_index, column=2)

        self.body_widgets["ask_var"][b_index] = tk.StringVar()
        self.body_widgets["ask"][b_index] = tk.Label(self._body_frame.sub_frame,
                                                     textvariable=self.body_widgets["ask_var"][b_index], bg=BG_COLOR,
                                                     fg=FG_COLOR_2, font=GLOBAL_FONT, width=self._col_width)
        self.body_widgets["ask"][b_index].grid(row=b_index, column=3)

        self.body_widgets['remove'][b_index] = tk.Button(self._body_frame.sub_frame, text="X",
                                                         bg="darkred", fg=FG_COLOR, font=GLOBAL_FONT, width=9,
                                                         command=lambda: self._remove_symbol(b_index))
        self.body_widgets['remove'][b_index].grid(row=b_index, column=4)
        self.body_widgets['buy'][b_index] = tk.Button(self._body_frame.sub_frame, text="B",
                                                      bg="darkred", fg=FG_COLOR, font=GLOBAL_FONT, width=9,
                                                      command=lambda: self._buy_symbol(b_index))
        self.body_widgets['buy'][b_index].grid(row=b_index, column=5)
        self.body_widgets['sell'][b_index] = tk.Button(self._body_frame.sub_frame, text="S",
                                                      bg="darkred", fg=FG_COLOR, font=GLOBAL_FONT, width=9,
                                                      command=lambda: self._sell_symbol(b_index))
        self.body_widgets['sell'][b_index].grid(row=b_index, column=6)

        self._body_index += 1
