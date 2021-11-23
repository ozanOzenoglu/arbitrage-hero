from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils.market import Market
import json
from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message


class ExchangeInfo(Info):
    def __init__(self,market:Market,symbol:str,address:str,fee:float=0,tag:str=""):
        self._json_message = ExchangeInfoMsg(self)
        self.__market = market
        self.__symbol= symbol
        symbols = symbol.split('/')
        if (len(symbols) < 2):
            error("Symbols given incorrect , given symbols is {:s} , expected is (A/B)".format(symbol))
            return
        else:
            self.__first_symbol=symbols[0]
            self.__second_symbol = symbols[1]
        self.__address = address
        self.__tag = tag
        self.__last_price = 0
        self.__last_bid = 0
        self.__last_ask = 0
        self.__last_avg_ask = 0
        self.__last_avg_bid = 0
        self.__first_symbol_balance = 0
        self.__second_symbol_balance = 0
        self.__tx_fee = fee

    def set_tx_fee(self,val:float):
        self.__tx_fee = val
    def get_tx_fee(self):
        return self.__tx_fee

    def set_first_balance_info(self,new_balance:float):
        self.__first_symbol_balance = new_balance

    def set_second_balance_info(self,new_balance:float):
        self.__second_symbol_balance = new_balance

    def get_first_symbol_balance_info(self):
        return float(self.__first_symbol_balance)

    def get_second_symbol_balance_info(self):
        return float(self.__second_symbol_balance)

    def set_last_price(self,last_price):
        self.__last_price = last_price

    def set_last_bid(self,last_bid):
        self.__last_bid  = last_bid

    def set_avg_bid(self,avg_bid:float):
        self.__last_avg_bid = avg_bid

    def get_avg_bid(self):
        return self.__last_avg_bid

    def set_avg_ask(self,avg_ask:float):
        self.__last_avg_ask = avg_ask

    def get_avg_ask(self):
        return self.__last_avg_bid

    def set_last_ask(self,last_ask):
        self.__last_ask = last_ask

    def get_last_price(self):
        return float(self.__last_price)

    def get_last_ask(self):
        return float(self.__last_ask)
    def get_last_bid(self):
        return self.__last_bid

    def related_market(self):
        return self.__market

    def get_tag(self):
        return self.__tag

    def set_tag(self,val:str):
        self.__tag = val

    def get_market(self,type:str=""):#ccxtExchange
        if type=='modified_ccxt':
            error("don't forget to remove modified_ccxt type")

        return self.__market.get_market() # return modified_ccxt.Exchange insnce

    def to_string(self,objType=None):
        result = {'market_name':self.get_market().id,
                  'symbol':self.__symbol,
                  'address':self.__address,
                  'last_ask':self.__last_ask,
                  'last_bid':self.__last_bid,
                  'last_price':self.__last_price,
                  'first_symbol_balance:' : self.__first_symbol_balance,
                  'second_symbol_balance': self.__second_symbol_balance,
                  'tx_fee':self.__tx_fee
                  }

        if ExchangeInfo.tagable_currency(self.__symbol):
            if self.__tag != "":
                result.update({'tag':self.__tag})
            else:
                error("Tag info must be given!")
                raise Exception("No Tag info is given for Exchange : {:s}/{:s}".format(self.get_market().id , self.__symbol))


        return result

    def get_symbol(self):
        return self.__symbol
    def get_first_symbol(self):
        return self.__first_symbol
    def get_second_symbol(self):
        return self.__second_symbol

    def get_address(self):
        return self.__address

    @staticmethod
    def json_to_instance(data:dict):
        try:
            market_name = data.__getitem__('market_name')
            symbol  = data.__getitem__('symbol')
            address = data.__getitem__('address')
            fee = 0 # TODO: bugfix it.
            market = Market.find_Market_by_name(market_name)
            if market == None:
                raise Exception('Market with name {:s} has not been initialised yet!')

            if ExchangeInfo.tagable_currency(symbol):
                try:
                    tag = data.__getitem__('tag')
                except Exception as e:
                    error("Tag couldn't find for {:s}".format(str(json.dumps(data))))
                    raise e
            else:
                tag = ""

            instance = ExchangeInfo(market,symbol,address,fee,tag)
            return instance
        except Exception as e:

            error(str(e))
            return None

    #Helper functions

    @staticmethod
    def tagable_currency(currenyc:str):
        if (currenyc.upper().__contains__("XRP") or currenyc.upper().__contains__("XLM") or currenyc.upper().__contains__("XEM")):
            return True
        else:
            return False

    @staticmethod
    def create_dummy_btc_exchange(market_name:str,symbol:str):
        symbol = str.upper(symbol) + "/" + 'BTC'
        dummy_data = {'market_name':market_name,'symbol':symbol,'address':'dummy_address'}
        dummy_instance = ExchangeInfo.json_to_instance(dummy_data)
        return dummy_instance

    @staticmethod
    def create_dummy_usd_exchange(market_name:str,symbol:str):
        if market_name == "bittrex" or market_name == "binance" or market_name == "poloniex":
            second_symbol = "USDT"
        else:
            second_symbol = "USD"
        if market_name == "vebit" or market_name == "koineks" or market_name =="koinim" or market_name == "btcturk":
            second_symbol = "TRY"
        tag_needed = ExchangeInfo.tagable_currency(symbol)        
        symbol = str.upper(symbol) + "/" + second_symbol
        if tag_needed:
            dummy_data = {'market_name':market_name,'symbol':symbol,'address':'dummy_address' ,"tag":"dummy_tag"}
        else:            
            dummy_data = {'market_name':market_name,'symbol':symbol,'address':'dummy_address'}
        dummy_instance = ExchangeInfo.json_to_instance(dummy_data)
        return dummy_instance

    @staticmethod
    def create_dummy_exchange(market_name: str, symbol: str):
        if market_name == 'bittrex' and symbol.__contains__('USD'):
            symbol = symbol.replace('USD','USDT')

        
        tag_needed = ExchangeInfo.tagable_currency(symbol)
        symbol = str.upper(symbol)
        
        if tag_needed:
            dummy_data = {'market_name':market_name,'symbol':symbol,'address':'dummy_address' ,"tag":"dummy_tag"}
        else:            
            dummy_data = {'market_name':market_name,'symbol':symbol,'address':'dummy_address'}

        dummy_instance = ExchangeInfo.json_to_instance(dummy_data)
        return dummy_instance


class ExchangeInfoMsg(Message):
    def __init__(self,setting:ExchangeInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        result = {'market_name':self.__relevent_setting.related_market().get_name(),
                  'symbol':self.__relevent_setting.get_symbol(),
                  'address':self.__relevent_setting.get_address()}
        return result


