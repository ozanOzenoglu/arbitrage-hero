#Author Ozan Ozenoglu ozan.ozenoglu@gmail.com
#File Created at 08.11.2017

'''
Scope of the Module
This module has function to set/read config from config file.
'''

import os
import json

from base.crypto_engine import symbols
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils.market import Market

from base.crypto_engine.setting_db.arbitrage_info import ArbitrageInfo
from base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.crypto_engine.setting_db.market_info import MarketInfo
from base.crypto_engine.setting_db.application_info import ApplicationInfo


#TODO ExchangeInfo should be implemented
class Config:

    CONFIG_FOLDER = ""

    src_path = os.path.abspath("").split(sep='src')[0] + 'src/'
    is_initialised = False
    is_markets_loaded = False
    #is_arbitrage_loaded = False
    is_exchange_loaded = False
    is_tx_fee_loaded = False
    is_market_json = False
    #is_arbitrage_json = False
    is_exchange_json = False
    is_pairs_loaded = False
    market_infos = {}
    market_infos_json ={}
    #arbitrage_infos = {}
    #arbitrage_infos_json = {}
    aribtrage_pairs_infos_json = {}

    #arbitrage_pairs_infos = {}
    tx_fees = {}
    markets = {}
    exchange_infos = {}
    exchange_infos_json = {}


    #arbitrages = [] #There is no arbitrage class so just return arbitrage_infos

    def __init__(self,config_folder:str):
        self.__config_folder = config_folder
        debug("Config class instance is initialised")

    @staticmethod#return ExchangeInfo
    def get_exchange_from_config():
        if(Config.is_exchange_loaded == False):
            Config.load_exchange_configs()
        return Config.exchange_infos


    @staticmethod
    def get_manager_config():
        try:
            with open(symbols.CONFIG_DIR + "manager.config" ,"r") as manager_log_file:
                mngr_ops = json.load(manager_log_file)
                app_info = ApplicationInfo.json_to_instance(mngr_ops)
                return app_info
        except Exception as e:
            error("Error during reading manager.config Ex:{:s}".format(str(e)))
            raise e
    @staticmethod
    def convert_instances_to_json():
        market_keys = Config.market_infos.keys()
        for key in market_keys:
            data = Config.market_infos.__getitem__(key)
            Config.market_infos_json.update({key:data.to_json()})
            #arbitrage_keys = Config.arbitrage_infos.keys()
        '''
        for key in arbitrage_keys:
            data = Config.arbitrage_infos.__getitem__(key)
            Config.arbitrage_infos_json.update({key:data.to_json()})
        '''
        exchange_keys = Config.exchange_infos.keys()
        for key in exchange_keys:
            data = Config.exchange_infos.__getitem__(key)
            Config.exchange_infos_json.update({key:data.to_json()})


    @staticmethod#return Market structure
    def get_markets_from_config():
        if (Config.is_markets_loaded == False):
            Config.load_market_configs()
        return Config.markets


    @staticmethod
    def set_config_folder(path:str):
        if(os.path.exists(path) is not True):
            raise Exception("Config Path does not exists!")
        else:
            if (os.path.exists(path + "markets.config") is not True):
                raise Exception("markets.config file is missing under {:s}!".format(str(path)))
            if (os.path.exists(path + "exchanges.config") is not True):
                raise Exception("exchanges.config file is missing under {:s}!".format(str(path)))
        Config.CONFIG_FOLDER = path
        debug("config folder path is updated with {:s}".format(path))

    @staticmethod
    def init_config_dir():
        if (Config.is_initialised == False):
            if Config.CONFIG_FOLDER == "":
                error("Please Provide Config Folder Location First")
                Config.is_initialised = False
                return
            else:
                if os.path.exists(Config.CONFIG_FOLDER):
                    if  os.path.exists(Config.CONFIG_FOLDER + "/exchanges.config") and os.path.exists(Config.CONFIG_FOLDER + "/markets.config"):
                        Config.src_path = Config.CONFIG_FOLDER
                        Config.is_initialised = True
                    else:
                        error("Some config files are missing.")
                        Config.is_initialised = False

    '''
    @staticmethod
    def get_arbitrage_pairs_from_config():
        if(Config.is_pairs_loaded == False):
            Config.load_arbitrage_pairs_configs()
        return Config.aribtrage_pairs_infos_json
        
    @staticmethod #return info strcuture
    def get_arbitrages_from_config():
        if (Config.is_arbitrage_loaded == False):
            Config.load_arbitrage_configs()
        return Config.arbitrage_infos



    @staticmethod
    def load_arbitrage_pairs_configs():
        Config.init_config_dir()
        with open(Config.src_path + '/arbitrage_pairs.config' , 'r') as arbitrage_pairs_file:
            data = json.load(arbitrage_pairs_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                Config.aribtrage_pairs_infos_json.update({key:val})
        Config.is_pairs_loaded = True


    @staticmethod
    def update_arbitrage_pairs_config():
        Config.init_config_dir()
        with open(Config.src_path + '/arbitrage_pairs.config' , 'w') as arbitrage_pairs_file:
            arbitrage_pairs_file.write(
                base.crypto_engine.utils.helper.convert_dict_to_str(Config.aribtrage_pairs_infos_json))
                
    @staticmethod
    def load_arbitrage_configs():
        Config.init_config_dir()
        with open( Config.src_path + '/arbitrage.config', 'r') as arbitrage_file:
            data = json.load(arbitrage_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                instance = ArbitrageInfo.json_to_instance(val)
                Config.arbitrage_infos.update({key:instance})
        Config.is_arbitrage_loaded = True

    @staticmethod
    def print_arbitrage_configs():
        keys = Config.arbitrage_infos.keys()
        for key in keys:
            data = Config.arbitrage_infos.__getitem__(key)
            print(data.to_json())


    @staticmethod
    def update_arbitrage_configs():
        Config.init_config_dir()
        with open(Config.src_path + '/arbitrage.config', 'w') as arbitrage_file:
            json.dump(Config.arbitrage_infos_json, arbitrage_file)

    @staticmethod
    def print_arbitrage_pairs_configs():
        keys = Config.aribtrage_pairs_infos_json.keys()
        for key in keys:
            data = Config.aribtrage_pairs_infos_json.__getitem__(key)
            print(base.crypto_engine.utils.helper.convert_dict_to_str(data))

'''


    @staticmethod
    def get_arbitrage_from_file(config_name:str):
        path = symbols.ARBITRAGE_CONFIG_DIR + config_name + ".config"
        result = {}
        with open( path, 'r') as arbitrage_file:
            data = json.load(arbitrage_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                instance = ArbitrageInfo.json_to_instance(val)
                result.update({key:instance})
        return result

    @staticmethod
    def load_exchange_configs():
        try:
            Config.init_config_dir()
            try:
                Config.update_fee_list()
            except Exception as e:
                error("Error during fetching fee_list from bittrex {:s}".format(str(e)))
            
            with open(Config.src_path + '/exchanges.config' , 'r') as exchanges_file:
                data = json.load(exchanges_file)
                keys = data.keys()
                print("keys are {:s}".format(str(keys)))
                for key in keys:
                    val = data.__getitem__(key)
                    instance = ExchangeInfo.json_to_instance(val)
                    if (instance == None):
                        error("exchange instance couldn't create for {:s}".format(key))
                        continue
                    try:
                        fee = Config.tx_fees.__getitem__(instance.get_first_symbol())
                    except Exception as e:
                        error("No fee information in list for {:s} 0 will be used!".format(str(instance.get_first_symbol())))
                        fee = 0
                    instance.set_tx_fee(fee)
                    Config.exchange_infos.update({key:instance})
                    print("{:s} is saved".format(str(key)))
            Config.is_exchange_loaded = True
        except Exception as e:
            Config.is_exchange_loaded = False
            error("Exception occured during loading exchange configs {:s}".format(str(e)))

    @staticmethod
    def update_exchange_configs():
        Config.init_config_dir()
        with open(Config.src_path + '/exchanges.config' , 'w') as exchange_file:
            json.dump(Config.exchange_infos_json,exchange_file)

    @staticmethod
    def update_fee_list():
        if Config.is_tx_fee_loaded == True:
            return

        Config.load_market_configs()
        bittrex = Config.markets.__getitem__('bittrex').get_market()

        currencies = bittrex.fetch_currencies()


        for currency in currencies:
            id = currency.__getitem__('id')
            fee = currency.__getitem__('fees')
            Config.tx_fees.update({id: float(fee)})

        symbols.fee_list = Config.tx_fees
        debug("symbols fee list also updated for backward compatibility!")



    @staticmethod
    def load_market_configs():

        if Config.is_markets_loaded == True:
            return

        Config.init_config_dir()
        with open( Config.src_path + '/markets.config', 'r') as markets_file:
            data = json.load(markets_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                instance = MarketInfo.json_to_instance(val)
                Config.market_infos.update({instance.get_name():instance})
                exchange = Market.get_market_by_name(instance.get_name())
                exchange.uid = instance.get_uid()
                exchange.apiKey = instance.get_api_key()
                exchange.secret = instance.get_secret_key()
                market_instance = Market(instance.get_name(),exchange)
                Config.markets.update({instance.get_name():market_instance})
        Config.convert_instances_to_json()
        Config.is_markets_loaded = True


    @staticmethod
    def update_market_configs():
        Config.init_config_dir()
        with open( Config.src_path + '/markets.config', 'w') as markets_file:
            json.dump(Config.market_infos_json, markets_file)


    @staticmethod
    def print_market_configs():
        keys = Config.market_infos.keys()
        for key in keys:
            data = Config.market_infos.__getitem__(key)
            print(data.to_json())



    @staticmethod
    def print_exchange_configs():
        keys = Config.exchange_infos.keys()
        for key in keys:
            data = Config.exchange_infos.__getitem__(key)
            print(data.to_json())


    @staticmethod
    def load_configs():
        Config.load_market_configs()
        Config.load_exchange_configs()
        #Config.load_arbitrage_configs()
        #Config.load_arbitrage_pairs_configs()

        Config.convert_instances_to_json()

    @staticmethod
    def update_configs():
        Config.convert_instances_to_json()
        #Config.update_arbitrage_configs()
        Config.update_exchange_configs()
        Config.update_market_configs()
        #Config.update_arbitrage_pairs_config()

    @staticmethod
    def print_all_configs():
        #Config.print_arbitrage_configs()
        Config.print_market_configs()
        Config.print_exchange_configs()
        #Config.print_arbitrage_pairs_configs()


'''
with open('market_info.json','r') as input_file:
    cex_market_data = json.load(input_file)
    cex_market = MarketInfo.json_to_instance(cex_market_data)
    print(cex_market.to_json())
'''

