'''
@author:Ozan
@Description: this serice is supposed to be used for fetch markets order books via api
then send them to server/api for android app.
TODO: implement the service. it's not even half implemented..
'''

import os,  sys

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]

sys.path.append(module_path)

import time , requests
import json

from api.base.crypto_engine.MessageApi.debug import *
from api.base.services.i_watchable_service import IWatchableService
from api.base.crypto_engine.utils.market import Market,Markets

def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__),str(e)))

        return result

    return catched

class OrderBookService(IWatchableService):
    DEFAULT_UPDATE_PERIOD = 10000
    SERVER_URL = "http://ozenoglu.com:8000/api_call"
    


    def create_try_symbols(symbols:[]):
        return [str(symbol.upper()) + "/TRY" for symbol in symbols]
    
    def create_usd_symbols(symbols:[]):
        return [str(symbol.upper()) + "/USD" for symbol in symbols]
    
    def create_symbols(second_symbol,symbols:[]):
        return [str(symbol.upper()) + "/" + second_symbol for symbol in symbols]
    

    
    MIN_DEFAULT_COINS = ["BTC","XRP","ETH","LTC","XLM"]; #TODO: Increase it
    DEFAULT_MARKET_SYMBOLS = {"cex": create_usd_symbols(["BTC","XRP","XLM","ETH","LTC","BCH","USDT","DOT","ADA","ATOM","LINK","NEO","TRX","XTZ","TRX","USDC","USDT"]),
                            "kraken":create_usd_symbols(["BTC","XRP","XLM","ETH","LTC","BCH"]),
                            "btcturk": create_try_symbols(["BTC","XRP","ETH","XLM","LTC","ADA","ATOM","LINK","NEO","TRX","XTZ","TRX","USDC","USDT","EOS"]),
                            "binance": create_symbols("USDT",["BTC","XRP","ETH","XLM","LTC"]),
                            "poloniex": create_symbols("USDT",["BTC","XRP","ETH","LTC"]),
                            "gdax": create_symbols("USD",["BTC","XRP","ETH","LTC","XLM"]),
                            "bitfinex": create_symbols("USD",["BTC","XRP","ETH","LTC"]),
                            "bitstamp": create_symbols("USD",["BTC","XRP","ETH","LTC"]), #XLM and BCH not supoorted ?
                            "bittrex": create_symbols("USDT",MIN_DEFAULT_COINS)
                            }
    def get_default_symbols_for_market(self, market):
        try:
            symbols = OrderBookService.DEFAULT_MARKET_SYMBOLS.get(market)
            if symbols == None:
                error("Symbols are None, you need to fix it!")#TODO:Fix here
                return OrderBookService.DEFAULT_MARKET_SYMBOLS.get("cex")
            return symbols
        except Exception as e:
            return create_usd_symbols(OrderBookService.MIN_DEFAULT_COINS)
    
    #TODO: This is very bad way, we need to on fly understand which symbols will be used in order to arbitrage table and configure itself in order to this..

    @trycatch
    def __init__(self , market_name:str,  update_period:int = 10 ,  symbols:tuple = None):
        self.__market_name = market_name
        self.__symbols = symbols if symbols is not None else self.get_default_symbols_for_market(market_name)
        self.__update_period = update_period
        self.__market  = Market.create_market(market_name)
        self.__orber_book = {"market_name":self.__market_name}
        super().__init__(self.__market_name + "_OB_SERVICE")

    @trycatch
    def send_server(self):
        data = {'event': 'upload_order_book', 'data': None, 'private_key': 'osman_is_my_girl'}
        data.update({'data': json.dumps(self.__orber_book)})
        str_data = json.dumps(data)
        ret = requests.get(OrderBookService.SERVER_URL, data=str_data)
        debug("{:s} ob is updated , result: {:s} ".format(str( self.__market_name ), str(ret.content)))
        self.get_orderbook() ##TODO: remove this self-test line

    @trycatch
    def get_orderbook(self):
        data = {'event': 'get_order_book', 'data': None, 'private_key': 'osman_is_my_girl'}
        data.update({'data': {"market_name":self.__market_name, "symbol_pair":"XRP/TRY"} })
        str_data = json.dumps(data)
        ret = requests.get(OrderBookService.SERVER_URL, data=str_data)
        return ret

    def start(self):

        while(True):
            for currency in self.__symbols:
                try:
                    r = self.__market.get_order_book(currency,IsOnline = True) # fetch directly from market , not out dabase. We're the one who updateting the db..
                    if (r.get("asks") == None):
                        error("order book does not include asks! ob:" + r.content)
                        continue
                    self.__orber_book.update({currency:r})
                    user_feedback("{:s} __ {:s} __ updated!".format(str(self.__market_name),currency))
                except Exception as e:
                    error("Error during fetching prices e:{:s}".format(str(e)))
            try:
                self.send_server()
                time.sleep(self.__update_period)
            except Exception as e:
                error("Error during sending price info to db_server")





    def init(self):
        return self.__init__(self.__market_name,self.__symbols,self.__update_period)
    
    
if __name__ == '__main__':
    ob_service = OrderBookService("btcturk" , 20)
    ob_service.start_service()
