import abc

from enum import Enum

class LoginErrors(Enum):
    RE_LOGIN = "NEED TO RE LOGIN"
    TRY_AGAIN = "TRY AGAIN"
    NEED_TO_WAIT = "NEED TO WAIT"
    WRONG_SMS_CODE = "WRONG SMS CODE"
    WEIRD_CONDITION = "WEIRD CONDITION"

'''
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils.market import Market

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message
from base.crypto_engine.setting_db.profile_info import ProfileInfo
'''
'''
This class is base class for browser classes such as koineks_browser , 
btcturk_browser which are supposed to actions such as read_balance , read order book of a crypto etc.
'''

import os, requests, sys, threading, multiprocessing

from third_party.splinter import Browser
from api.base.crypto_engine import symbols

#class Browser(abc.ABC): is the same with below line
class MainBrowser(metaclass=abc.ABCMeta):

    module_path = os.path.dirname(os.path.abspath(__file__))
    module_path = module_path.split('api')[0]

    selenium_driver_path = module_path + "api/selenium_drivers/"
    geckod_driver_path = selenium_driver_path + "geckodriver"
    phantomjs_driver_path = selenium_driver_path + "phantomjs"
    drivers = {'firefox': geckod_driver_path, 'phantomjs': phantomjs_driver_path}

    def __init__(self,username,password,driver_name,headless):
        self.__username = username
        self.__password = password
        self.__driver_name = driver_name
        driver_path = MainBrowser.drivers.__getitem__(driver_name)
        if (driver_name == "phantomjs"):
            self._browser = Browser(driver_name=driver_name, executable_path=driver_path)
        else:
            self._browser = Browser(driver_name=driver_name, executable_path=driver_path, headless=headless)
        self._driver = self._browser.driver
        self.__driver_pid = str(self._driver.service.process.pid)
        self.__user = username



    def get_user(self):
        return self.__user

    def get_pass(self):
        return self.__password

    def get_driver_name(self):
        return self.__driver_name

    def get_driver_pid(self):
        return self.__driver_pid

    def get_driver(self):
        return self._driver


    def get_selenium_browser(self):
        return self._browser

    def quit(self):
        self._browser.quit()

    @abc.abstractmethod
    def login(self):
        pass

    @abc.abstractmethod
    def fetch_balance(self,symbol:str):
        pass

    @abc.abstractmethod
    def go_to_market(self,market:str):
        pass

    @abc.abstractmethod
    def fetch_order_book(symbol:str,force_go_to_market:bool=False):
        pass

    @abc.abstractmethod
    def withdraw(self,currency:str,amount:float,address:str,tag:str=""):
        pass

    @abc.abstractmethod
    def get_ss(self):
        pass

    @abc.abstractmethod
    def buy(self,symbol:str,amount:float,price:float):
        pass

    @abc.abstractmethod
    def sell(self,symbol:str,amount:float,price:float):
        pass