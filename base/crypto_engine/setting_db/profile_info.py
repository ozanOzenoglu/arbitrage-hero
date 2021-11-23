from enum import Enum
from random import randint

from base.crypto_engine.MessageApi.debug import *

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message


class AccType(Enum):
    WOOD = 0  # kalas müşteri:D
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    PLATINUM = 4






class ProfileInfo(Info):
    def __init__(self, name: str, surname: str, phone: str, email: str, password: str, pin: str,
                 acc_type: AccType = AccType.WOOD):
        super().__init__()
        self.__name = name
        self.__surname = surname
        self.__phone = phone
        self.__email = email
        self.__password = password
        self.__pin = pin
        self.__id = randint(0, 99999999)  # TODO impelment a incremental unique id create function later.
        self.__acc_type = acc_type
        self._json_message = ProfileInfoMsg(self)
        self.__total_profit = 0
        self.__create_date = str(datetime.now())

#Getter and Setters. I know this not a pythonic way but this is how I eat yogurth( A turkish words.)
    def get_name(self):
        return self.__name
    def set_name(self,name:str):
        self.__name = name
    def get_surname(self):
        return self.__surname
    def set_surname(self,surname:str):
        self.__surname = surname
    def get_phone(self):
        return self.__phone
    def set_phone(self,phone:str):
        self.__phone = phone
    def get_email(self):
        return self.__email
    def set_email(self,email:str):
        self.__email = email
    def get_password(self):
        return self.__password
    def set_password(self,password:str):
        self.__password = password
    def get_pin(self):
        return self.__pin
    def set_pin(self,pin:str):
        self.__pin = pin
    def get_id(self):
        return self.__id
    def get_acctype(self):
        return self.__acc_type
    def set_acctype(self,acctype:str):
        self.__acc_type = acctype
    def get_total_profit(self):
        return self.__total_profit
    def set_total_profit(self,profit:float):
        self.__total_profit = profit
    def get_create_date(self):
        return self.__create_date


class ProfileInfoMsg(Message):
    def __init(self, setting: ProfileInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        result = {'name' : self.__relevent_setting.get_name(),
                  'surname' : self.__relevent_setting.get_surname(),
                  'phone' : self.__relevent_setting.get_phone(),
                  'email': self.__relevent_setting.get_email(),
                  'password' : self.__relevent_setting.get_password(),
                  'pin' : self.__relevent_setting.get_pin(),
                  'id' : self.__relevent_setting.get_id(),
                  'acc_type' : self.__relevent_setting.get_acctype(),
                  'total_profit': self.__relevent_setting.get_total_profit(),
                  'create_date' : self.__relevent_setting.get_create_date()}
        return result