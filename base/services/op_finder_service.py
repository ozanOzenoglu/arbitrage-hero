#Author Ozan Ozenoglu ozan.ozenoglu@gmail.com
#File Created at 08.11.2017


'''
Scope of Module:
This module is command line interface module which take commands from command line and parse them and execute them
'''

from threading import Thread
from time import sleep
import os
import copy
import datetime

from api.base.crypto_engine.utils.config_manager import Config
from api.base.crypto_engine.utils.op_finder_ng import OpportunityFinderNG
from api.base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.services.i_watchable_service import IWatchableService
from api.base.crypto_engine.symbols import *
from api.base.crypto_engine.MessageApi.debug import *



class OPFinderService(IWatchableService):


    def __init__(self,arbitrage_config_name:str,markets,exchanges):
        self.__markets = markets
        self.__exchanges = exchanges
        self.__name = "OP_FINDER_SERVICE"
        self.__config_name = arbitrage_config_name
        self.__table_title = arbitrage_config_name
        debug("OpFinderService init started with started config name {:s}".format(str(self.__config_name)))
        self.__arbitrrages = Config.get_arbitrage_from_file(self.__config_name)
        super().__init__(self.__name,-1)

    def get_table_title(self):
        return self.__table_title
    def get_config_name(self):
        return self.__config_name

    def init(self):
        self.__init__(self.__config_name,self.__markets , self.__exchanges)
        return self

    def start(self):
        debug("OpFinderService is started")
        op_finder_pool = {}
        working_threads = {}
        arbitrages = self.__arbitrrages
        exchanges = self.__exchanges
        table_title = self.__table_title
        arbitrage_keys = arbitrages.keys()
        for arbitrage_name in arbitrage_keys:
            arbitrage = arbitrages.__getitem__(arbitrage_name)
            if arbitrage.get_active() == False:
                debug("Arbitrage {:s} is disabled".format(str(arbitrage_name)))
                continue  # skip if the arbitrage is not activated
            buy_market = arbitrage.get_market_low().get_name()
            sell_market = arbitrage.get_market_high().get_name()

            alarm_percent = arbitrage.get_percent()
            is_only_notify = arbitrage.get_only_notify()

            is_notify_active = arbitrage.get_notify()
            symbol = arbitrage.get_symbol()
            symbol = str.lower(symbol)
            delay = arbitrage.get_delay()
            spend_money = arbitrage.get_spend_money_options()

            #ArbitrageTable.set_files_name(table_title) #no need anymore thnks to table_service

            try:
                low_market_exchange = exchanges.__getitem__(buy_market + '/' + symbol)
            except Exception as e:
                low_market_exchange = ExchangeInfo.create_dummy_usd_exchange(buy_market, symbol)
            try:
                high_market_exchange = exchanges.__getitem__(sell_market + '/' + symbol)
            except Exception as e:
                high_market_exchange = ExchangeInfo.create_dummy_usd_exchange(sell_market, symbol)

            thread_name = buy_market + "-" + sell_market + "-" + symbol + "_op_finder"

            op_finder = OpportunityFinderNG(delay, low_market_exchange, high_market_exchange, alarm_percent,
                                            is_only_notify, is_notify_active,spend_money)

            op_finder_copy = copy.deepcopy(op_finder)
            op_finder_pool.update({thread_name: op_finder_copy})

            op_finder_start_thread = Thread(target=op_finder.start, name=thread_name)

            op_finder_start_thread.start()
            working_threads.update({thread_name: op_finder_start_thread})

            sleep(2)

        print ("All Threads are started , Total count it {:d}".format(int(len(working_threads))))
        self.start_watchdog(working_threads,op_finder_pool)



    def watch_dog_log(self,msg:str):
        try:
            now = str(datetime.now())
            msg = now + " : " +msg + "\n"
            Debug.log(msg,self.__name + "_watch_dog")
        except Exception as e:
            error("Error during watch_dog logging {:s}".format(str(e)))

    def start_watchdog(self,working_threads,op_finder_pool):
        #WATCHDOG STARTS HERE
        while True:
            thread_remove_list = []
            new_started_thread = {}
            for thread_name in working_threads:
                thread = working_threads.__getitem__(thread_name)
                sleep(1) # don't use all cpu power pls.
                if thread.is_alive() != True:
                    error("WATCH DOG: Found DEAD Thread {:s}".format(str(thread_name)) )
                    self.watch_dog_log("WATCH DOG: Found DEAD Thread {:s}".format(str(thread_name)))
                    thread_remove_list.append(thread_name)

                    copy_op_finder = op_finder_pool.__getitem__(thread_name)
                    new_thread = Thread(target=copy_op_finder.start , name = thread_name )
                    new_started_thread.update({thread_name:new_thread})

                    new_thread.start()
                    sleep(1)

            try:
                for dead_thread in thread_remove_list:
                    working_threads.pop(dead_thread)
                    user_feedback("Old dead {:s} thread is removed from working threads".format(str(dead_thread)))
                    self.watch_dog_log("Old dead {:s} thread is removed from working threads".format(str(dead_thread)))
            except Exception as e:
                error("Error occuring while removing therad thread from working threads")
                self.watch_dog_log("Error occuring while removing therad thread from working threads")

            try:
                for thread_name in new_started_thread:
                    thread  = new_started_thread.__getitem__(thread_name)
                    working_threads.update({thread_name:thread})
                    user_feedback("New started {:s} thread added to working thread.".format(str(thread_name)))
                    self.watch_dog_log("New started {:s} thread added to working thread.".format(str(thread_name)))
            except Exception as e:
                error("Error occuring while adding new therad to working threads ")
                self.watch_dog_log("Error occuring while adding new therad to working threads")
