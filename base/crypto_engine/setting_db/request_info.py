from enum import Enum
from base.crypto_engine.MessageApi.debug import *

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message
from base.crypto_engine import symbols
#from api.base.crypto_engine.setting_db.exchange_info import ExchangeInfo

class RequestType():
    ARBITRAGE = "ARBITRAGE_REQUEST"
    WITHDRAW = "WITHDRAW_REQUEST"
    BUY="BUY_REQUEST"
    SELL="SELL_REQUEST"
    GET_BALANCE="GET_BALANCE_REQUEST"
    GET_ALL_BALANCE="GET_ALL_BALANCE_REQUEST"
    SIMULATION = "SIMULATION_REQUEST"
    FETCH_FOR_ARBITRAGE = "FETCH_FOR_ARBITRAGE_REQUEST" #Highest Fetch priority
    FETCH_FOR_HELP_URGENT = "FETCH_FOR_HELP_URGENT_REQUEST" #Higher Fetch priority
    FETCH_FOR_HELP = "FETCH_FOR_HELP_REQUEST" # lowest fetch priority
    TERMINATE="TERMINATE_REQUEST"

class RequestInfo(Info):

    def __init__(self,handler_name:str,type:str,symbol:str="",buy_exchange=None,sell_exchange=None,rate:float=0,log_file:str="",money:float=0,wait_time:float=0,destination:str="",tag:str="",amount_of_withdraw:float=0,price:float = 0):
        super().__init__() # call parent constructor

        self.__request_type = type
        self.__symbol = symbol
        self.__destination_addres = destination
        self.__tag = tag
        self.__amount_of_withdraw = amount_of_withdraw
        self.__price = price
        self.__handler_name = handler_name
        self.__buy_exchange = buy_exchange
        self.__log_file_name = log_file
        self.__expected_rate = rate
        self.__sell_exchange = sell_exchange
        self.__money_to_spend = money
        self.__wait_time = wait_time

        self._json_message = SimulatorInfoMsg(self)

    def get_handler_name(self):
        return self.__handler_name

    def set_handler_name(self,val:str):
        self.__handler_name = val

    def set_price(self,val:str):
        self.__price = val

    def get_price(self):
        return self.__price

    def set_type(self,val:str):
        self.__request_type = val

    def get_type(self):
        return self.__request_type

    def set_amount(self,val:str):
        self.__amount_of_withdraw = val

    def get_amount(self):
        return self.__amount_of_withdraw

    def set_destination(self,val:str):
        self.__destination_addres = val

    def get_destination(self):
        return self.__destination_addres

    def set_tag(self,val:str):
        self.__tag = val

    def get_tag(self):
        return self.__tag

    def set_buy_exchange(self,exchange):
        self.__buy_exchange = exchange


    def get_buy_exchange(self):
        return self.__buy_exchange

    def set_log_file_name(self,name):
        self.__log_file_name = name

    def get_log_file_name(self):
        return self.__log_file_name

    def set_expected_rate(self,rate):
        self.__expected_rate = rate

    def get_expected_rate(self):
        return self.__expected_rate

    def set_sell_exchange(self,exchange):
        self.__sell_exchange = exchange

    def get_sell_exchange(self):
        return self.__sell_exchange

    def set_money_to_spend(self,money):
        self.__money_to_spend = money

    def get_money_to_spend(self):
        return self.__money_to_spend

    def set_symbol(self,symbol):
        self.__symbol = symbol

    def get_symbol(self):
        return self.__symbol

    def set_wait_time(self,time):
        self.__wait_time = time

    def get_wait_time(self):
        return self.__wait_time






    def push_request(self):
        from base.services.load_balancer import LoadBalancer

        if(LoadBalancer.is_any_handler_healthy(self.__handler_name) is not True):
            error("Koineks service is not healthy now!")
            return -1

        request_file_name = self.get_log_file_name() + ".request"
        try:
            request_dir = symbols.MAIN_REQUEST_FOLDER
            file_path = request_dir + request_file_name
            with (open(file_path, "w")) as request_file:
                request_as_str = str({self.get_log_file_name() : self.to_json() })
                request_as_str = request_as_str.replace('\'','"')

                request_file.write(request_as_str)
            user_feedback("Requqes {:s} pushed".format(str(request_file_name)))
            return 0
        except Exception as e:
            error(str(e))
            return -1

    @staticmethod
    def correct_json_data(data): # this correct given data to json_to_instance , if given data is forgetten with ..._request key.
        keys = data.keys()
        for key in keys:
            if str(key).__contains__("_request"):
                data = data.pop(key)
                return data
        return data

    @staticmethod
    def json_to_instance(data:dict,exchanges=None):

        try:
            data = RequestInfo.correct_json_data(data)
            type = data.__getitem__('request_type')
            handler_name = data.__getitem__('handler_name')
            symbol = ""
            if type != RequestType.GET_ALL_BALANCE and type != RequestType.TERMINATE:
                symbol = data.__getitem__('symbol')
            instance = RequestInfo(handler_name, type, symbol)
        except Exception as e:
            if type != RequestType.GET_ALL_BALANCE: # GET_ALL_BALANCE no need  symbol info
                raise Exception("Fatal Error no must infos given: {:s}".format(str(e)))

        if type == RequestType.WITHDRAW:
            try:
                log_file_name = data.__getitem__('log_file')
                instance.set_log_file_name(log_file_name)

                amount = data.__getitem__('amount')
                instance.set_amount(amount)


                destination = data.__getitem__('destination')
                instance.set_destination(destination)

            except Exception as e: # must data for withdraw request
                debug("no {:s} info for withdraw request".format(str(e)))
                raise Exception("no {:s} info for withdraw request".format(str(e)))

            try:
                tag = data.__getitem__('tag') # not a must (xrp , xlm and some other cryto needs it)
                instance.set_tag(tag)

            except Exception as e:
                debug("{:s} data is not given which is not mandatory ".format(str(e)))
        elif type == RequestType.BUY or type == RequestType.SELL:
            try:
                log_file_name = data.__getitem__('log_file')
                instance.set_log_file_name(log_file_name)
                price = data.__getitem__('price')
                instance.set_price(price)
                amount = data.__getitem__('amount')
                instance.set_amount(amount)
            except Exception as e:
                debug("{:s} data is not given which is not mandatory ".format(str(e)))
        elif type == RequestType.TERMINATE:
            debug("No extra info needed for terminate request")

        elif type == RequestType.GET_BALANCE:
            debug("No extra info needed")

        elif type == RequestType.GET_ALL_BALANCE:
            debug("No extra info needed")


        elif str(type).upper().__contains__("FETCH"):
            log_file_name = data.__getitem__('log_file')
            instance.set_log_file_name(log_file_name)


        else: #Simulation and Arbitrage Request Handle here for now together.

            money_to_spend = data.__getitem__('money')
            wait_time = data.__getitem__('wait_time')
            log_file_name = data.__getitem__('log_file')
            expected_rate = data.__getitem__('expected_rate')



            ask_avarage = data.__getitem__('ask_avarage')

            buy_exchange_name = data.__getitem__('buy_exchange').__getitem__('market')


            sell_exchange_name = data.__getitem__('sell_exchange').__getitem__('market')

            lower_symbol = str(symbol).lower()

            try:
                buy_market_exchange = exchanges.__getitem__(buy_exchange_name + '/' + lower_symbol)
            except Exception as e:
                raise Exception("No exchange: {:s}".format(str(e)))
                #buy_market_exchange = ExchangeInfo.create_dummy_usd_exchange(buy_exchange_name, lower_symbol)
            try:
                sell_market_exchange = exchanges.__getitem__(sell_exchange_name + '/' + lower_symbol)
            except Exception as e:
                raise Exception("No exchange: {:s}".format(str(e)))
                #sell_market_exchange = ExchangeInfo.create_dummy_usd_exchange(sell_exchange_name, lower_symbol)


            buy_market_exchange.set_last_ask(ask_avarage)


            instance.set_buy_exchange(buy_market_exchange)
            instance.set_sell_exchange(sell_market_exchange)
            instance.set_expected_rate(expected_rate)
            instance.set_log_file_name(log_file_name)
            instance.set_money_to_spend(money_to_spend)
            instance.set_wait_time(wait_time)


        return instance




class SimulatorInfoMsg(Message):
    def __init__(self, setting:RequestInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        type = self.__relevent_setting.get_type()
        if type== RequestType.WITHDRAW:

            symbol = self.__relevent_setting.get_symbol()

            if (str(symbol).upper() == "XRP" or str(symbol).upper() == "XLM"):
                result = {'handler_name': self.__relevent_setting.get_handler_name(),
                          'request_type': self.__relevent_setting.get_type(),
                          'symbol': self.__relevent_setting.get_symbol(),
                          'amount': self.__relevent_setting.get_amount(),
                          'destination': self.__relevent_setting.get_destination(),
                          'tag':self.__relevent_setting.get_tag(),
                          'log_file': self.__relevent_setting.get_log_file_name()
                          }

            else:
                result = {
                    'handler_name': self.__relevent_setting.get_handler_name(),
                    'request_type':self.__relevent_setting.get_type(),
                    'symbol':self.__relevent_setting.get_symbol(),
                    'amount':self.__relevent_setting.get_amount(),
                    'destination':self.__relevent_setting.get_destination(),
                    'log_file':self.__relevent_setting.get_log_file_name()
                }

        elif type== RequestType.BUY or type == RequestType.SELL:
            result = {'request_type': self.__relevent_setting.get_type(),
                      'symbol': self.__relevent_setting.get_symbol(),
                      'amount': self.__relevent_setting.get_amount(),
                      'price': self.__relevent_setting.get_price(),
                      'log_file': self.__relevent_setting.get_log_file_name(),
                      'handler_name': self.__relevent_setting.get_handler_name()}

        elif  type.upper() == RequestType.GET_BALANCE:
            result = {'request_type':self.__relevent_setting.get_type(),
                      'symbol':self.__relevent_setting.get_symbol(),
                      'handler_name': self.__relevent_setting.get_handler_name()}

        elif  type.upper() == RequestType.GET_ALL_BALANCE:
            result = {'request_type':self.__relevent_setting.get_type(),
                      'handler_name': self.__relevent_setting.get_handler_name()}

        elif type.upper() == RequestType.TERMINATE:
            result = {"request_type":self.__relevent_setting.get_type(),
                      'handler_name': self.__relevent_setting.get_handler_name()}

        elif type.upper().__contains__("FETCH"):
            result = {"symbol":self.__relevent_setting.get_symbol(),
                      "request_type":self.__relevent_setting.get_type(),
                      'log_file':self.__relevent_setting.get_log_file_name(),
                      'handler_name': self.__relevent_setting.get_handler_name()
                      }

        else:
            result = {'buy_exchange':{'symbol':self.__relevent_setting.get_buy_exchange().get_first_symbol(),'market':self.__relevent_setting.get_buy_exchange().related_market().get_name()},
                      'ask_avarage':self.__relevent_setting.get_buy_exchange().get_last_ask(),
                      'sell_exchange':{'symbol':self.__relevent_setting.get_sell_exchange().get_first_symbol(),'market':self.__relevent_setting.get_sell_exchange().related_market().get_name()},
                      'expected_rate':self.__relevent_setting.get_expected_rate(),
                      'wait_time': 0 if self.__relevent_setting.get_wait_time() == None else self.__relevent_setting.get_wait_time() ,
                      'money':self.__relevent_setting.get_money_to_spend(),
                      'symbol':self.__relevent_setting.get_symbol(),
                      'request_type': self.__relevent_setting.get_type(),
                      'log_file':self.__relevent_setting.get_log_file_name(),
                      'handler_name': self.__relevent_setting.get_handler_name()
                      }
        return result
