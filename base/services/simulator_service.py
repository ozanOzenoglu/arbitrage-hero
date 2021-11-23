
import json
import threading
import os
from api.base.crypto_engine.utils.config_manager import Config
from base.services.i_watchable_service import IWatchableService
from api.base.crypto_engine.utils.helper import convert_dict_to_str
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine.utils.simulator import Simulator
from api.base.crypto_engine.utils.arbitrage import Arbitrage
from api.base.crypto_engine import symbols

import time
from third_party.watchdog.observers import Observer
from third_party.watchdog.events import PatternMatchingEventHandler
import signal


class SimulatorService(IWatchableService):

    REQUEST_DIR =  symbols.SIMULATOR_REQUEST_DIR
    LOG_FOLDER = symbols.SIMULATOR_LOG_DIR
    MIN_TIME_INTERVAL_BETWEEN_TWO_ARBITRAGES = 10* 60 * 1000 # 10mins
    is_healthy = True



    @staticmethod
    def get_log_folder():
       return Simulator.LOG_FOLDER


    def __init__(self):
        self.__request_dir = symbols.SIMULATOR_REQUEST_DIR
        self.__log_dir = symbols.SIMULATOR_LOG_DIR
        if (os.path.exists(self.__request_dir) and os.path.isdir(self.__request_dir)) is not True :
            os.makedirs(self.__request_dir)
        if (os.path.exists(self.__log_dir) and os.path.isdir(self.__log_dir)) is not True:
            os.makedirs(self.__log_dir)

        self.__new_requests = []
        self.__koineks_arbitrages = []
        self.__simulator_samples = []
        self._service_name = "SimulatorService"

        self.__exchanges = Config.get_exchange_from_config()

        self.__transfer_fees = Config.tx_fees
        super().__init__(self._service_name,-1)
        user_feedback("Simulator Service is initialised!")

    def init(self):
        self.__init__()
        return self

    def add_new_requests(self,new_requests):
        self.__new_requests += new_requests

    def parse_requests(self,request_file):

        with(open(request_file,"r")) as request_file:
            request = []
            data = json.load(request_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                request.append( OpportunityInfo.json_to_instance(val))
            return request

    @staticmethod
    def push_simulator_request(op_info:OpportunityInfo):
        if(SimulatorService.is_service_healthy() is not True):
            return -1
        name = op_info.get_buy_market() + "_" + op_info.get_sell_market() + "_" + op_info.get_currency()
        request_file_name = name + ".request"
        try:
            file_path = symbols.SIMULATOR_REQUEST_DIR + request_file_name
            with(open (file_path , "w")) as request_file:
                op_info_as_dict =  op_info.to_json()
                request_as_str = json.dumps(op_info_as_dict)
                request_file.write(request_as_str)
            return 0
        except Exception as e:
            error(str(e))
            return -1


    @staticmethod
    def is_service_healthy():
        return True # Need to be fixed (system so slow) until then disabled..
        #return SimulatorService.is_healthy

    def find_transfer_time(self,currency:str):
        time = symbols.transfer_time_list.__getitem__(currency.upper())
        return time

    def start_thread_for_request(self,request:OpportunityInfo):
        simulator = Simulator(request)
        buy_market = request.get_buy_market()
        sell_market = request.get_sell_market()
        currency = request.get_currency()
        simulator_name = buy_market + "_" + sell_market + "_" + currency
        transfer_time = self.find_transfer_time(request.get_currency())
        request_thread = threading.Thread(target=simulator.start_simulation, name=simulator_name , args=[transfer_time])
        request_thread.start()


    def process_request(self):

        if (len(self.__new_requests) > 0 ): #if we have new request process them and remove from the list.

            current_request = self.__new_requests.pop()


            while (current_request != None):
                try:
                    self.start_thread_for_request(current_request)
                except Exception as e:
                    error(str(e))
                try:
                    if ( len(self.__new_requests) > 0):
                        current_request = self.__new_requests.pop()
                    else:
                        current_request = None
                except Exception as e :
                    error(str(e))


    @staticmethod
    def destructor(a, b):
        print("Simulator Destructor delete debug file {:s}".format(symbols.DEBUG_LEVEL_FILE))
        SimulatorService.is_healthy = False

        if (os.path.exists(symbols.DEBUG_LEVEL_FILE)):
            os.remove(symbols.DEBUG_LEVEL_FILE)
        exit(0)




    def start(self):
        user_feedback("simulator service is started")
        observer = Observer()
        handler = MyHandler()
        handler.save_service(self)
        observer.schedule(MyHandler(), path= self.__request_dir)
        observer.start()
        try:
            while SimulatorService.is_service_healthy():
                self.process_request()
                time.sleep(1)

        except KeyboardInterrupt:
            observer.stop()

        observer.stop()

class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.request"]

    service_instance = None

    def save_service(self,service_instance):
       MyHandler.service_instance = service_instance

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print( event.src_path, event.event_type ) # print now only for degug
        if (str(event.event_type) == "modified"):
            try:
                new_requests  = MyHandler.service_instance.parse_requests(event.src_path)
                os.remove(event.src_path)
                MyHandler.service_instance.add_new_requests(new_requests)

            except Exception as e:
                error("Error during request parsing : {:s}".format(str(e)))

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)






