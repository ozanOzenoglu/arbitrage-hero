from base.crypto_engine.MessageApi.debug import *

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message


class MarketInfo(Info):
    def __init__(self,name:str,api:str,secret:str,balances:dict=None,prices:dict=None,uid:str=None):
        super().__init__() # call parent constructor
        self.__market_name = name
        self.__api_key = api
        self.__secret_key = secret
        self.__prices = prices
        self.__balances = balances
        self._json_message = MarketInfoMsg(self)
        self.__uid = uid


    def get_uid(self):
        return self.__uid
    def set_uid(self,val:str):
        self.__uid = val

    def get_api_key(self):
        return self.__api_key
    def set_api_key(self,api_key:str):
        self.__api_key = api_key
    def get_secret_key(self):
        return self.__secret_key
    def set_secret_key(self,secret_key):
        self.__secret_key = secret_key
    def get_prices(self):
        return self.__prices
    def set_prices(self,prices:dict):
        self.__prices = prices
    def get_balance(self):
        return self.__balances
    def set_balance(self,balance:dict):
        self.__balances = balance
    def get_name(self):
        return self.__market_name
    def set_name(self,name:str):
        self.__market_name = name

    @staticmethod
    def json_to_instance(data:dict):
        uid = None
        api_key = data.__getitem__('api_key')
        name = data.__getitem__('name')
        secret_key = data.__getitem__('secret_key')
        try:
            uid = data.__getitem__('uid')
        except Exception as e:
            debug("market {:s} has no uid attribute".format(name))

        if (uid != None):
            instance = MarketInfo(name,api_key,secret_key,None,None,uid)
            return instance
        else:
            instance = MarketInfo(name,api_key,secret_key)
            return instance


class MarketInfoMsg(Message):
    def __init__(self, setting:MarketInfo):
        self.__relevent_setting = setting


    def _to_string(self):

        result = {'name':self.__relevent_setting.get_name(),
                 'api_key': self.__relevent_setting.get_api_key(),
                 'secret_key': self.__relevent_setting.get_secret_key()}
        if  (self.__relevent_setting.get_uid() != None):
            result.update({'uid':self.__relevent_setting.get_uid()})

        return result