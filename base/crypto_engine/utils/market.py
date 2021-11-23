import modified_ccxt
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.engine.transaction_engine import Operation
from base.crypto_engine.utils import helper
from base.crypto_engine import symbols
class Market:
    created_market = {} #created market dictionary.. on the fly..

    @staticmethod
    def find_Market_by_name(name:str):
        try:
            return Market.created_market.__getitem__(name)
        except Exception as e:
            error('The {:s} market could not find'.format(str(name)))
            return None

    @staticmethod
    def get_market_by_name(name:str):
        if(type(name) != type("")):
            raise TypeError("Please give the name of the Market")
        else:
            return Markets.get_market(name)


    @staticmethod
    def create_market(name:str):
        try:
            exchange = Market.get_market_by_name(name)
            return Market(name, exchange)
        except Exception as e:
            error("Error during creating market {:s}".format(str(e)))
            return None

    def __init__(self, name:str, market:modified_ccxt.Exchange):
        self.__market = market
        self.__name = name
        self.__exchanges= {}
        Market.created_market.update({name:self})

    def get_market(self):
        return self.__market
    def get_name(self):
        return self.__name
    def add_exchange_info(self,exchange):
        self.__exchanges.update({exchange.get_symbol():exchange})

    def get_order_book(self,symbol:str,IsOnline=symbols.FETCH_ORDERBOOK_ONLINE): # if IsOnline True, fetch from directly markets
        try:
            fetch_order_book_op = Operation.create_fetch_order_books(self,symbol,online=IsOnline)
            result = fetch_order_book_op.operate()
            if result == None:
                raise Exception("Orderbook is fetched None from DB ,try online?")
            return result        
        except Exception as e:#if this case fail we may try here the old fetching method from market itself?
            error('error during get order book {:s}'.format(str(e)))
            try:
                fetch_order_book_op = Operation.create_fetch_order_books(self,symbol,online=True)
                result = fetch_order_book_op.operate()
                if(result != None):
                    user_feedback("We couldn't fetch {:s} from db ,instead fetched it online from market:{:s}..".format(str(symbol),str(self.get_name() ) ) )
                else:
                    error("Fatal Error, we can't fetch the orderbook for {:s} from {:s} in anyway!!".format(str(symbol), str(self.get_name())))
                    raise Exception("Orderbook Couldn't fetch from {:s}".format(str(self.get_name())))                                     
                return result
            except Exception as e:
                error("Error during fetching symbol {:s} from {:s} online after trying db service!".format(str(symbol),str(self.get_name())))
                return None

    def __get_curency__(self,symbol:str):
        try:
            return symbol.split('/')[1]
        except Exception as e:
            error("Error during getting currency of symbol {:s} error:{:s}".format(str(symbol),str(e)))
            return "CurrencyError"

    def __get_avg_(self,symbol:str,type:str,total:int):
        reliable = True
        currency = self.__get_curency__(symbol)
        result = {'currency': currency}

        try:
            if (symbol.__contains__("TRY") is not True):
                total = helper.convert_try_to_usd(total)
            order_book = self.get_order_book(symbol)
            if (order_book == None):
                error("{:s} order_book is None!".format(str(self.get_name())))
                return -1
            else:
                orders = order_book.__getitem__(type)
                try:
                    avg = helper.get_avarage_price_for_money(orders, total)
                except Exception as e:
                    reliable = False
                    avg = helper.avarage_price_for_first_n(orders,10)
                best = helper.get_best_price(orders)
                result.update({'reliable':reliable})
                if (currency == "TRY"):  # convert to usd
                    result.update({"avg_try": avg})
                    result.update({"best_try": best})
                    avg = helper.convert_try_to_usd(avg)
                    best = helper.convert_try_to_usd(best)
                    result.update({'avg_usd': avg})
                    result.update({'best_usd': best})
                elif (currency == "USD" or currency == "USDT"):
                    result.update({"avg_usd": avg})
                    result.update({"best_usd": best})
                    avg = helper.convert_usd_to_try(avg)
                    best = helper.convert_usd_to_try(best)
                    result.update({'avg_try': avg})
                    result.update({'best_try': best})
                return result
        except Exception as e:
            error('error during get avarage {:s} error:{:s}'.format(str(type),str(e)))
            return -1

    def get_avarage_bid(self,symbol,total:int = symbols.INTELLIGENT_AVARAGE_MONEY_TRY): # total : from how much orders we get avarage
        return self.__get_avg_(symbol,"bids",total)

    def get_avarage_ask(self, symbol, total: int = symbols.INTELLIGENT_AVARAGE_MONEY_TRY):  # total : from how much orders we get avarage
        return self.__get_avg_(symbol, "asks", total)

    
    def get_fixed_fees(self):
        
        fixed_fees = {
            'funding' : {
                "withdraw": {
                    'TRY': 3.0,
                    'BTC': 0.0007,
                    'ETH': 0.005,
                    'USDT': 3.0,
                    'LTC': 0.01,
                    'DOGE': 2,
                    'BCH': 0.001,
                    'DASH': 0.002,
                    'BTG': 0.001,
                    'ZEC': 0.001,
                    'ETC': 0.003,
                    'XEM': 1,
                    'XLM': 0.3,
                    'XRP': 1,
                    'ADA': 1,
                    'NEO': 0,
                    'DOT': 0.1,
                    'EOS': 0.1,
                    'TRX': 2.5,
                    'USDC': 5,
                    'USDT': 1,
                    'XTZ': 1,
                    'ATOM': 0.005,
                    'LINK': 0.33,
                    
                }
                
            }
        }
        return fixed_fees
        
        
    
    def get_withdraw_fee(self, symbol):
        market = self.get_market() #get buy market
        try:
            withdraw_fee_rate = market.fees.__getitem__('funding').__getitem__(
                'taker').__getitem__(symbol)
        except Exception as e:
            try:
                withdraw_fee_rate = self.get_fixed_fees().__getitem__('funding').__getitem__('withdraw').__getitem__(symbol) #TODO: btcturk case ? fix it
            except Exception as e:
                error("Error during fetching market taker&withdraw fees withdraw_fee supposed as Zero(0) e:{:s}".format(str(e)))
                withdraw_fee_rate = 0 #TODO: Fix this workaround!
        return withdraw_fee_rate
        
    
    def get_trade_fee(self):
        market = self.get_market() #get buy market        
        try:
            ask_taker_fee = market.fees.__getitem__('trading').__getitem__('taker') * 100
        except Exception as e:
            try:                
                ask_taker_fee = market.fees.__getitem__('trading').__getitem__('maker') * 100                
            except Exception as e:
                error("Error during fetching market taker&withdraw fees withdraw_fee supposed as Zero(0) e:{:s}".format(str(e)))
                ask_taker_fee = 0 #TODO: Fix this workaround!
                market.fees.__getitem__('trading').update({"taker":0})
        return ask_taker_fee


class Markets:
    is_initialised = False
    markets = {}

    def __init__(self):
        self.markets ={}
        pass

    @staticmethod
    def init_markets():
        if Markets.is_initialised == False:
            for id in modified_ccxt.exchanges:
                debug(id + " is added into markets...")
                targetClass = getattr(modified_ccxt, id)
                instance = targetClass()
                Markets.markets.update({id: instance})
                Markets.is_initialised = True
        else:
            error("Markets class is already initialised!")

    @staticmethod
    def get_market(id:str):
        if (Markets.is_initialised == False):
            Markets.init_markets()
            debug("Markets are initialised")
        return Markets.markets.__getitem__(id)





