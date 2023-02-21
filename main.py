import config
import tkinter as tk
import logging
# from connectors.bitmex import BitmexClient
from connectors.binance_futures import BinanceFuturesClient
import pprint
from logkeeper import log_keeper
from interface.root_component import Root

if __name__ == "__main__":

    log_keeper("info.log")
    binance = BinanceFuturesClient(config.FUTURES_API_KEY, config.FUTURES_API_SECRET, True)
    # bitmex = BitmexClient(BITMEX_TESTNET_API_PUBLIC, BITMEX_TESTNET_API_SECRET, True)

    root = Root(binance)

    root.mainloop()
