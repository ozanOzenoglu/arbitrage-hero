import abc
import os
import json
import time
from base.crypto_engine.setting_db.request_info import RequestType,RequestInfo
from base.crypto_engine.utils import helper
from base.crypto_engine import symbols
from base.crypto_engine.MessageApi.debug import *

def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))

        return result

    return catched

def timeit(method):
    def handle(*args,**kw):
        ts = time.time() * 1000
        method(*args, **kw)
        te = time.time() * 1000
        symbol = args[1].get_symbol()
        user_feedback("{:s} -> {:s} finished in {:d}".format(str(method.__name__), symbol, int(te - ts)))
    return handle

class Handler(metaclass=abc.ABCMeta):

    SRC_FOLDER = os.path.abspath("").split(sep='src')[0] + "src/"
    ORDER_BOOK_DIR = symbols.ORDER_BOOK_DIR


    #Get OrderBOOK RELATED FUNC START HERE

    def get_order_book_file_path(self):
        return self.__order_book_file

    def __init__(self,username:str):
        name = self.get_name()
        self.__balance_info = {"balance_holder":username , "balance_info": {}}
        self.__order_book_file = Handler.ORDER_BOOK_DIR + "/"+name+".json"
        self.__balance_file  = Handler.ORDER_BOOK_DIR + "/"+name+".json"
        self.__ss_path = Handler.SRC_FOLDER + name+"_service/logs/ss/"
        self._ORDER_BOOK = {}
    def get_orderbook_folder_path(self):
        return  Handler.ORDER_BOOK_DIR
    def get_balance_file_path(self):
        return self.__balance_file
    def get_ss_folder_path(self):
        return self.__ss_path

    def update_order_books_file(self):
        order_book_file = self.get_order_book_file_path()
        order_book_dir = self.get_orderbook_folder_path()
        if not os.path.exists(order_book_dir):
            os.makedirs(order_book_dir)
            error("ORDER_BOOK_DIR created first time? , is it new system?")

        with open(order_book_file, 'wb') as outputfile:
            byte_array = bytearray(json.dumps(self._ORDER_BOOK), 'utf8')
            outputfile.write(byte_array)

    def update_order_book_from_file(self):
        order_book_file = self.get_order_book_file_path()
        try:
            with open(order_book_file, "r") as orderbook_file:
                self._ORDER_BOOK = json.loads(orderbook_file.read())
        except Exception as e:
            error("Error during updateing order book from file {:s}".format(str(e)))


    def update_order_book(self, currency: str, orderbook: dict):
        order_book_file = self.get_order_book_file_path()
        order_book_dir = self.get_orderbook_folder_path()
        order_book_locked = helper.try_lock_folder(order_book_dir, max_try_ms=500)  # try max 0.5 sec
        if (order_book_locked == True):
            try:
                self.update_order_book_from_file()
                time_stamp = int(round(time.time() * 1000))
                orderbook.update({'update_time': time_stamp})
                old_orderbook = self._ORDER_BOOK.pop(currency,
                                                     None)  # Delete the currency then update , this way ensure no duplication.
                #is_same = False if old_orderbook == None else (self.is_same(old_orderbook, orderbook))#we don't use is_same logic but in future can be used .

                self._ORDER_BOOK.update({currency: orderbook})  # on the fly
                try:
                    self.update_order_books_file()  # on the disk
                    helper.upload_order_book(order_book_file)
                except Exception as e:
                    error("Exception during writing to file".format((str(e))))
            except Exception as e:
                error("Error during updating order book {:s}".format(str(e)))
            finally:
                if (order_book_locked):
                    helper.release_folder_lock(order_book_dir)
        else:
            error("Couldn't update to order_book , because we couldn't lock the folder")


    @timeit
    def handle_fetch_request(self,request):
        symbol = request.get_symbol()
        browser = self.get_browser()
        try:
            currency_order_book = browser.fetch_order_book(symbol,False) #try without forcing refreshing page (if browser is already on that page)
        except Exception as e:
            try:
                currency_order_book = browser.fetch_order_book(symbol,True) #try force to refresh page even if the browser on that page
            except Exception as e:
                raise Exception("{:s} could not fetched due to : {:s}".format(str(symbol),str(e))) # if we still get error , raise the error to handler_service to decide what to do.

        self.update_order_book(symbol, currency_order_book)
        debug("Updated {:d} asks and {:d} bids for {:s}".format(
            len(currency_order_book.__getitem__('asks')), len(currency_order_book.__getitem__('bids')),
            str(symbol)))

    @timeit
    def handle_buy_request(self,request):
        browser = self.get_browser()
        symbol = request.get_symbol()
        if (str(symbol).__contains__('/')):
            symbol = str(symbol).split(('/'))[0]

        price = str(request.get_price())
        amount = str(request.get_amount())
        browser.buy(symbol,amount,price)


    @timeit
    def handle_sell_request(self,request):
        browser = self.get_browser()
        symbol = request.get_symbol()
        price = str(request.get_price())
        amount = str(request.get_amount())

        browser.sell(symbol,amount,price)




    @timeit
    def handle_update_balance_request(self,request):
        symbol = request.get_symbol()
        debug("Fetching balane info for {:s} started".format(str(symbol)))
        self.update_balance(symbol)

    @timeit
    def handle_withdraw_request(self,request):
        browser = self.get_browser()
        symbol = request.get_symbol()
        time.sleep(1)
        address = request.get_destination()
        amount = str(request.get_amount())
        tag = ""
        if (symbol == "XRP" or symbol == "XLM" or symbol == "XEM"):
            tag = request.get_tag()
            browser.find_by_name("destination_tag")._set_value(tag)

        browser.withdraw(symbol,amount,address,tag)


    #Do not cover with try-catch , because hanlder_service HAVE TO get exception to determine how to go.
    def handle_request(self,request:RequestInfo):
        request_type = request.get_type().upper()
        if request_type == RequestType.FETCH_FOR_HELP:  # Handle every type of fetch request is here
            self.handle_fetch_request(request)

        elif request_type == RequestType.FETCH_FOR_HELP_URGENT:  # Handle every type of fetch request is here
            self.handle_fetch_request(request)

        elif request.get_type() == RequestType.BUY:
            self.handle_buy_request(request)

        elif request.get_type() == RequestType.SELL:
            self.handle_sell_request(request)

        elif request.get_type() == RequestType.GET_BALANCE:
            self.handle_update_balance_request(request)

        elif request.get_type() == RequestType.GET_ALL_BALANCE:
            self.fetch_all_balance()

        elif request.get_type() == RequestType.WITHDRAW:
            self.handle_withdraw_request(request)
        else:
            raise Exception("Not supported Request Type:[{:s}]".format(str(request_type)))

    @classmethod
    def report(file_name,msg):
        user_feedback(msg)
        ''' just print 
        try:
            with open(HelperKoineks.MAIN_LOG_FOLDER + file_name, "a+") as log_file:
                log_file.write(msg+"\n")
                user_feedback("HELPER Logged Msg: " + msg)
        except Exception as e:
            error("Error during report! {:s}".format(str(e)))
        '''

    @trycatch
    def get_balance_info_dict(self):
        return self.__balance_info.__getitem__("balance_info")

    @trycatch
    def get_balance_with_holder(self):
        return self.__balance_info


    @trycatch
    def update_balance(self,symbol:str):
        browser = self.get_browser()
        balance = browser.fetch_balance(symbol)
        self.update_balance_info(symbol, balance)


    @trycatch
    def update_balance_info(self,currency:str,balance:str):
        balance_info_dict = self.get_balance_info_dict()
        time_stamp =  int(round(time.time() * 1000))
        balance_info_dict.pop(currency,None) # Delete the currency then update , this way ensure no duplication.
        balance_info_dict.pop('latest_update',None) # Delete the currency then update , this way ensure no duplication.
        balance_info_dict.update({'latest_update':time_stamp})
        balance_info_dict.update({currency:{'update_time':time_stamp,'balance':balance}})
        self.update_balance_file()
        debug("{:s} balance info is updated {:s} !".format(str(currency),str(balance)))

    @trycatch
    def update_balance_file(self):
        balance_file_path = self.get_balance_file_path()
        order_book_dir = self.get_orderbook_folder_path()
        if not os.path.exists(order_book_dir):
            os.makedirs(order_book_dir)
        with open(balance_file_path, 'wb+') as outputfile:
            info = self.get_balance_with_holder()
            byte_array = bytearray(json.dumps(info),'utf8')
            outputfile.write(byte_array)

    @trycatch
    def fetch_all_balance(self,crypto_markets=symbols.KOINEKS_MARKETS):
        user_feedback("fetch_all_balance is started")
        other_balance_fetched = False
        current_currency_index = 0
        try_count = 0
        currencies_length = len(crypto_markets)
        while other_balance_fetched == False:
            try:
                self.update_balance("TRY")
                while current_currency_index < currencies_length:
                    try_count = try_count + 1
                    currennt_currency = crypto_markets[current_currency_index]
                    self.update_balance(currennt_currency)
                    current_currency_index = current_currency_index + 1
                other_balance_fetched = True
            except Exception as e:
                if (try_count < 5):
                    error("Exception during fetching balance of {:s} error: {:s}".format(str(currennt_currency),str(e)))
                    time.sleep(1)
                else:
                    raise Exception("Error during fetch_all_balance : fetching other_balance:{:s}".format(str(e)))


    @abc.abstractmethod
    def is_healthy(self):
        pass

    @abc.abstractmethod
    def get_name(self):
        pass

    @abc.abstractmethod
    def get_browser(self):
        pass


    @abc.abstractmethod
    def de_init(self):
        pass