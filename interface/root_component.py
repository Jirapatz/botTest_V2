"""
COMPONENTS=
- Watchlist
- Logging
- Strategies
-Trades
"""
import json
import logging
import tkinter as tk
from tkinter.messagebox import askquestion
from interface.styling import *
from interface.logging_component import Logging
# from connectors.bitmex import BitmexClient
from connectors.binance_futures import BinanceFuturesClient
from interface.watchlist_component import WatchList
from interface.trades_component import TradesWatch
from interface.strategy_component import StrategyEditor
import threading
logger = logging.getLogger()


class Root(tk.Tk):
    def __init__(self, binance: BinanceFuturesClient):
    # def __init__(self, binance: BinanceFuturesClient, bitmex: BitmexClient):
        super().__init__()

        self.binance = binance
        # self.bitmex = bitmex

        self.title("Cryptocurrency Trading Bot")
        self.protocol("WM_DELETE_WINDOW", self._ask_before_close)

        self.configure(bg=BG_COLOR)

        self.main_menu = tk.Menu(self)
        self.configure(menu=self.main_menu)

        self.workspace_menu = tk.Menu(self.main_menu, tearoff=False)
        self.main_menu.add_cascade(label="Workspace", menu=self.workspace_menu)
        self.workspace_menu.add_command(label="Save Workspace", command=self._save_workspace)

        self._left_frame = tk.Frame(self, bg=BG_COLOR)
        self._left_frame.pack(side=tk.LEFT)

        self._right_frame = tk.Frame(self, bg=BG_COLOR)
        self._right_frame.pack(side=tk.RIGHT)

        self._watchlist_frame = WatchList(self.binance.contracts, self._left_frame, bg=BG_COLOR)
        # self._watchlist_frame = WatchList(self.binance.contracts, self.bitmex.contracts,
        #                                   self._left_frame, bg=BG_COLOR)
        self._watchlist_frame.pack(side=tk.TOP)

        self.logging_frame = Logging(self._left_frame, bg=BG_COLOR)
        self.logging_frame.pack(side=tk.TOP)

        self._strategy_frame = StrategyEditor(self, self.binance, self._right_frame, bg=BG_COLOR)
        # self._strategy_frame = StrategyEditor(self, self.binance, self.bitmex, self._right_frame, bg=BG_COLOR)
        self._strategy_frame.pack(side=tk.TOP)

        self._trades_frame = TradesWatch(self.binance, self._right_frame, bg=BG_COLOR)
        # self._trades_frame = TradesWatch(self.binance, self.bitmex, self._right_frame, bg=BG_COLOR)
        self._trades_frame.pack(side=tk.TOP)

        self._update_ui()

    def _ask_before_close(self):
        result = askquestion("Confirmation", "Do you really want to exit the application?")
        if result == "yes":
            self.binance.reconnect = False
            # self.bitmex.reconnect = False
            self.binance.ws.close()
            # self.bitmex.ws.close()

            self.destroy()

    def _save_workspace(self):
        # Watchlist
        watchlist_symbols = []
        for key, value in self._watchlist_frame.body_widgets['symbol'].items():
            symbol = value.cget("text")
            exchange = self._watchlist_frame.body_widgets['exchange'][key].cget("text")

            watchlist_symbols.append((symbol, exchange, ))

        self._watchlist_frame.db.save("watchlist", watchlist_symbols)

        # TODO: research the difference between get() and cget()
        # Strategies
        strategies = []

        strat_widgets = self._strategy_frame.body_widgets

        for b_index in strat_widgets['contract']:
            strategy_type = strat_widgets['strategy_type_var'][b_index].get()
            contract = strat_widgets['contract_var'][b_index].get()
            timeframe = strat_widgets['timeframe_var'][b_index].get()
            balance_pct = strat_widgets['balance_pct'][b_index].get()
            take_profit = strat_widgets['take_profit'][b_index].get()
            stop_loss = strat_widgets['stop_loss'][b_index].get()

            extra_params = dict()
            for param in self._strategy_frame.extra_params[strategy_type]:
                code_name = param['code_name']

                extra_params[code_name] = self._strategy_frame.additional_parameters[b_index][code_name]

            strategies.append((strategy_type, contract, timeframe, balance_pct, take_profit, stop_loss,
                               json.dumps(extra_params)))

        self._strategy_frame.db.save("strategies", strategies)

        self.logging_frame.add_log("Workspace Saved Successfully!")

    def _update_ui(self):

        # Logs

        # for log in self.bitmex.logs:
        #     if not log["displayed"]:
        #         self.logging_frame.add_log(log['log'])
        #         log['displayed'] = True

        for log in self.binance.logs:
            if not log["displayed"]:
                self.logging_frame.add_log(log['log'])
                log['displayed'] = True

        # Trades and Logs

        for client in [self.binance]:
        # for client in [self.binance, self.bitmex]:
            try:

                for b_index, strategy in client.strategies.items():
                    for log in strategy.logs:
                        if not log['displayed']:
                            self.logging_frame.add_log(log['log'])
                            log['displayed'] = True

                    for trade in strategy.trades:
                        if trade.time not in self._trades_frame.body_widgets['symbol']:  # we can select any column
                            self._trades_frame.add_trade(trade)

                        if trade.contract.platform == "binance":
                            precision_pnl = trade.contract.price_decimals
                        else:
                            precision_pnl = 8   # pnl will always be in xbt for bitmex (??)

                        pnl_str = "{0:.{prec}f}".format(trade.pnl, prec=precision_pnl)
                        self._trades_frame.body_widgets['pnl_var'][trade.time].set(pnl_str)
                        self._trades_frame.body_widgets['status_var'][trade.time].set(trade.status.capitalize())

            except RuntimeError as e:
                logger.error("RuntimeError while looping through strategies dictionary: %s", e)

        # Watchlist Prices

        try:
            for key, value in self._watchlist_frame.body_widgets['symbol'].items():
                symbol = self._watchlist_frame.body_widgets['symbol'][key].cget('text')
                exchange = self._watchlist_frame.body_widgets['exchange'][key].cget('text')

                if exchange == "Binance":
                    # if symbol not in self.binance.contracts:
                    #     continue

                    # if symbol not in self.binance.prices:
                    #     self.binance.get_bid_ask(self.binance.contracts[symbol])
                    #     print("BIDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD",self.binance.get_bid_ask(self.binance.contracts[symbol]))
                    #     continue
                    self.binance.get_bid_ask(self.binance.contracts[symbol])
                    precision = self.binance.contracts[symbol].price_decimals

                    prices = self.binance.prices[symbol]

                if prices['bid'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['bid'], prec=precision)
                    print("price_str: ", price_str)
                    self._watchlist_frame.body_widgets['bid_var'][key].set(price_str)
                if prices['ask'] is not None:
                    price_str = "{0:.{prec}f}".format(prices['ask'], prec=precision)
                    self._watchlist_frame.body_widgets['ask_var'][key].set(price_str)
                
        except RuntimeError as e:
            logger.error("RuntimeError while looping through watchlist dictionary: %s", e)

        self.after(1500, self._update_ui)
        # t = threading.Thread(target=self.binance.ws.close())
        # t.start()