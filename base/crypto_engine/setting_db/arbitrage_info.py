from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils.market import Market

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message

class Mode():

    AGGRESSIVE = "AGGRESSIVE" # use all balance when an opportunity is found
    SAFE = "SAFE" # just notify the user
    STEP_BY_STEP = "STEP_BY_STEP" # Just use a constant amount of balance for arrbitrage
    INTELLIGENT = "INTELLIGENT" # Look first , calculate percent and do it

class ArbitrageInfo(Info):
    def __init__(self,market_low:Market, market_high:Market,symbol:str , percent:float , delay:float,active:bool,notify:bool,is_only_notify:bool,stable_count:int,operation_mode:Mode,spend_money_options:list):
        super().__init__() # call parent constructor
        self.__market_low = market_low
        self.__market_high = market_high
        self.__symbol = symbol
        self.__percent = percent
        self.__operation_mode = operation_mode
        self.__delay = delay
        self.__active = active
        self.__notify = notify
        self.__is_only_notify = is_only_notify
        self.__market_stable_count = stable_count
        self.__spend_money_options = spend_money_options
        self._json_message = ArbitrageInfoMsg(self)


    def get_spend_money_options(self):
        return self.__spend_money_options
    def set_spend_money_options(self,val):
        self.__spend_money_options = val

    def get_operation_mode(self):
        return self.__operation_mode
    def set_operation_mode(self,val:Mode):
        self.__operation_mode = val

    def get_notify(self):
        return self.__notify
    def set_notify(self,val:bool):
        self.__notify = notify

    def get_stable_count(self):
        return self.__market_stable_count
    def set_stable_count(self,val:int):
        self.__market_stable_count = val

    def set_active(self,val:bool):
        self.__active = val
    def get_active(self):
        return self.__active

    def set_only_notify(self,val:bool):
        self.__is_only_notify = val

    def get_only_notify(self):
        return self.__is_only_notify

    def get_market_low(self):
        return self.__market_low
    def set_market_low(self,low_market:Market):
        self.__market_low = low_market
    def get_market_high(self):
        return self.__market_high
    def set_market_high(self,market:Market):
        self.__market_high = market
    def get_symbol(self):
        return self.__symbol
    def set_symbol(self,symbol:str):
        self.__symbol = symbol
    def get_percent(self):
        return self.__percent
    def set_percent(self,percent:float):
        self.__percent = percent
    def get_delay(self):
        return self.__delay
    def set_delay(self,val:float):
        self.__delay = val


    @staticmethod
    def json_to_instance(data:dict):
        percent = data.__getitem__('percent')
        operation_mode = data.__getitem__('operation_mode')
        if (str(operation_mode).upper() == Mode.INTELLIGENT):
            operation_mode = Mode.INTELLIGENT
        elif(str(operation_mode).upper() == Mode.AGGRESSIVE):
            operation_mode = Mode.AGGRESSIVE

        try:
            only_notify =(str.lower(data.__getitem__('only_notify')) == 'true')
        except Exception as e:
            only_notify = True

        spend_money_options = data.__getitem__('spend_money_options')
        low_market_id = data.__getitem__('low_market_id')
        high_market_id = data.__getitem__('high_market_id')
        symbol = data.__getitem__('symbol')
        stable_count = data.__getitem__('stable_num')
        delay = data.__getitem__('delay')
        active = (str.lower(data.__getitem__('active')) == 'true') # if True strings , returns true if False string returns False
        notify = (str.lower(data.__getitem__('notify')) == 'true') # if True strings , returns true if False string returns False
        low_market = Market.find_Market_by_name(low_market_id)
        high_market = Market.find_Market_by_name(high_market_id)

        if(low_market == None):
            raise Exception('low market {:s} have not been initialised yet!'.format(low_market_id))
            
        if(high_market == None):
            raise Exception("high market {:s} have not been initialised yet!".format(high_market_id))
            


        instance = ArbitrageInfo(low_market,high_market,symbol,percent,delay,active,notify,only_notify,stable_count,operation_mode,spend_money_options)
        return instance





class ArbitrageInfoMsg(Message):
    def __init__(self, setting:ArbitrageInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        result = {'low_market_id':self.__relevent_setting.get_market_low().get_market().id,
                  'high_market_id':self.__relevent_setting.get_market_high().get_market().id,
                  'symbol':self.__relevent_setting.get_symbol(),
                  'percent':self.__relevent_setting.get_percent(),
                  'delay':self.__relevent_setting.get_delay(),
                  'active': self.__relevent_setting.get_active(),
                  'notify': self.__relevent_setting.get_notify(),
                  'spend_money_options':self.__relevent_setting.get_spend_money_options(),
                  'only_notify' : self.__relevent_setting.get_only_notify(),
                  'stable_num' : self.__relevent_setting.get_stable_count(),
                  'operation_mode' : self.__relevent_setting.get_operation_mode()
                  }
        return result
