import time,importlib

from api.base.crypto_engine.setting_db.request_info import RequestType,RequestInfo
from api.base.crypto_engine.MessageApi.debug import *
from api.base.services.load_balancer import LoadBalancer
from api.base.services.i_watchable_service import IWatchableService


class OB_Fresh_Guard_Service(IWatchableService):

    def __init__(self,market_class_name:str,currency_set:tuple):
        self.__currencies_to_watch = currency_set
        self.__market_class_name = market_class_name
        module = importlib.import_module("api.modified_ccxt."+ str(market_class_name))
        market_class = getattr(module,market_class_name)
        self.__market = market_class()
        self.__is_healthy = True
        super().__init__("{:s}_OB_FRESH_GUARDIAN".format(str(market_class_name)),-1)


    def init(self):
        self.__init__(self.__market_class_name,self.__currencies_to_watch)
        return self

    def is_data_fresh(self,symbol:str):
        try:
            self.__market.fetch_order_book(symbol, params={"from_file": True , 'need_fresh':True})
            return True
        except Exception as e:
            return False

    def update_currency(self,currency:str):
        fetch_request = RequestInfo(self.__market_class_name,RequestType.FETCH_FOR_HELP_URGENT, currency)
        fetch_request.set_symbol(currency)
        fetch_request.set_log_file_name(currency + "_fetch_urgent_request")
        fetch_request.push_request()

    def start(self):
        error("###### OB FRESH GUY IS STARTED ######")
        while LoadBalancer.is_any_handler_healthy(self.__market_class_name) == False:
            time.sleep(10)
            error("No any helper yet")

        while self.__is_healthy:
            for currency in self.__currencies_to_watch:
                is_fresh = self.is_data_fresh(currency)
                if (is_fresh == False):
                    self.update_currency(currency)
                    debug("currency fetch request".format(str(currency)))
                else:
                    debug("currency is fresh {:s}".format(str(currency)))
            time.sleep(15)
