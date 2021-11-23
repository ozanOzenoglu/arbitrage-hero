from crypto_engine.utils.config_manager import Config

from base.crypto_engine.setting_db import ArbitrageInfo
from base.crypto_engine.setting_db import Info
from base.crypto_engine.setting_db import Message


class ArbitragePairsInfo(Info):

    @staticmethod
    def get_pairs():
        result = {}
        pairs = Config.get_arbitrage_pairs_from_config()
        keys = pairs.keys()
        for key in keys:
            data = pairs.__getitem__(key)
            instance = ArbitragePairsInfo.json_to_instance(data)
            result.update({key:instance})

    def __init__(self,arbitrage_low:ArbitrageInfo,arbitrage_high:ArbitrageInfo,percent:float):
        super().__init__() # call parent constructor
        self.__arbitrage_low = arbitrage_low
        self.__arbitrage_high = arbitrage_high
        self.__percent = percent

        self._json_message = ArbitragePairsInfoMsg(self)

    def get_arbitrage_low(self):
        return self.__arbitrage_low
    def set_arbitrage_low(self,arbitrage:ArbitrageInfo):
        self.__arbitrage_low = arbitrage

    def get_arbitrage_high(self):
        return self.__arbitrage_high

    def set_arbitrage_high(self, arbitrage: ArbitrageInfo):
        self.__arbitrage_high = arbitrage

    def get_percent(self):
        return self.__percent

    def set_percent(self,val:float):
        self.__percent = val


    @staticmethod
    def json_to_instance(data:dict):
        percent = data.__getitem__('percent')
        low_arbitrage_name = data.__getitem__('low_arbitrage')
        high_arbitrage_name = data.__getitem__('high_arbitrage')
        arbitrages = Config.get_arbitrages_from_config()
        low_arbitrage = arbitrages.__getitem__(low_arbitrage_name)
        high_arbitrage = arbitrages.__getitem__(high_arbitrage_name)


        instance = ArbitragePairsInfo(low_arbitrage,high_arbitrage,percent)
        return instance





class ArbitragePairsInfoMsg(Message):
    def __init__(self, setting:ArbitragePairsInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        low_arbitrage_low_market_name = self.__relevent_setting.get_arbitrage_low().get_market_low().get_market().id
        low_arbitrage_high_market_name = self.__relevent_setting.get_arbitrage_low().get_market_high().get_market().id
        low_arbitrage_symbol = self.__relevent_setting.get_arbitrage_low().get_symbol()
        low_arbitrage_symbol = str.lower(low_arbitrage_symbol)
        high_arbitrage_symbol = self.__relevent_setting.get_arbitrage_high().get_symbol()
        high_arbitrage_symbol = str.lower(high_arbitrage_symbol)
        high_arbitrage_low_market_name = self.__relevent_setting.get_arbitrage_high().get_market_low().get_market().id
        high_arbitrage_high_market_name = self.__relevent_setting.get_arbitrage_high().get_market_high().get_market().id


        result = {'low_arbitrage':low_arbitrage_low_market_name + '/' + low_arbitrage_high_market_name + '/' + low_arbitrage_symbol,
                  'high_arbitrage':high_arbitrage_low_market_name + '/' + high_arbitrage_high_market_name + '/' + high_arbitrage_symbol,
                  'percent': self.__relevent_setting.get_percent()
                  }
        return result


Config.load_market_configs()
Config.load_exchange_configs()

Config.load_arbitrage_pairs_configs()
pairs = Config.get_arbitrage_pairs_from_config()

keys = pairs.keys()
for key in keys:
    data = pairs.__getitem__(key)
    instance = ArbitragePairsInfo.json_to_instance(data)
    print(instance.to_json())