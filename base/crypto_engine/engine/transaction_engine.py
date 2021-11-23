#Author Ozan Ozenoglu ozan.ozenoglu@gmail.com
#File Created at 08.11.2017

'''
Scope of Module:
This module has functions to create/add/work/delete transaction.
'''

from base.crypto_engine.utils import helper as helper
from base.crypto_engine.engine.event import *
from base.crypto_engine.setting_db.request_info import RequestType,RequestInfo
from builtins import float
from random import randint
#due to dependcy of debug to time , impprt time module later than debug module
from base.crypto_engine.MessageApi.debug import *
from time import sleep, time
from base.crypto_engine.symbols import *

import json, requests

MIN_RANDOM_RANGE = 0
MAX_RANDOM_RANGE = 99999999
TRANSACTION_LIFE = 600 * 10 #10min min


class Operation(Producer):

    def dump_operation(self):
        debug("Type:{:s} symbol:{:s} amount:{:f} market{:s}".format(str(self.__operation_type),str(self.__symbol),float(self.__amount),str(self.__market.id)))

    def __init__(self,market , operation_type:str,max_try:int,max_wait:int,params={}):
        super().__init__() # call parent constructor

        self.__amount = 0
        self.__key = ""
        self.__is_completed = False
        self.__address = ""
        self.__limit_price = 0
        self.__operation_type = operation_type
        self.__try_count = 0
        self.__max_try_count = max_try
        self.__wait_time_between_try = max_wait
        self.m_market = market # class Market instance
        self.__market = market.get_market()
        self.__symbol = None
        self.__params = params
        debug("Operation {:s} is created".format(operation_type))
    def get_type(self):
        return self.__operation_type

    def get_completed(self):
        return self.__is_completed
    def set_completed(self,val:bool):
        self.__is_completed = val


    @staticmethod
    def add_consumers_to_transactions(operation_list,consumer_list):
        for operation in operation_list:
            for consumer in consumer_list:
                operation.add_consumer(consumer)


    @staticmethod
    def create_fetch_market_price(market,symbol:str,max_try=3,wait=10):
        operation = Operation(market,Event.FETCH_MARKET_PRICE,max_try,wait)
        operation.__symbol = symbol
        return operation
    @staticmethod
    def create_check_balance(market ,max_try=3,wait=60):
        operation = Operation(market,Event.CHECK_BALANCE_COMMAND,max_try,wait)
        return operation
    @staticmethod
    def create_market_buy(amount:float,market ,symbol:str,max_try=3,wait=60):
        operation = Operation(market,Event.MARKET_BUY_COMMAND,max_try,wait)
        operation.__symbol = symbol
        operation.__amount = amount
        return operation
    @staticmethod
    def create_limit_buy(amount:float,price:float,market,symbol:str,max_try=3,wait=60):
        operation = Operation(market,Event.LIMIT_BUY_COMMAND,max_try,wait)
        operation.__symbol = symbol
        operation.__amount = amount
        operation.__limit_price = price
        return operation
    @staticmethod
    def create_market_sell(amount:float,market ,symbol:str,max_try=3,wait=60):
        operation = Operation(market,Event.MARKET_SELL_COMMAND,max_try,wait)
        operation.__symbol = symbol
        operation.__amount = amount
        return operation
    @staticmethod
    def create_limit_sell(amount:float,price:float,market ,symbol:str,max_try=3,wait=60):
        operation = Operation(market,Event.LIMIT_SELL_COMMAND,max_try,wait)
        operation.__symbol = symbol
        operation.__amount = amount
        operation.__limit_price = price
        return operation
    @staticmethod
    def create_withdraw(amount:float,symbol:str,address:str,market ,max_try=3,wait=60,params={}):
        operation = Operation(market,Event.WITHDRAW_COMMAND,max_try,wait)
        operation.__amount = amount
        operation.__address = address
        operation.__symbol = symbol
        operation.__params = params
        return operation

    @staticmethod
    def create_kraken_withdraw(amount:float,symbol:str,address:str,market ,key:str,max_try=1,wait=2):
        operation = Operation(market,Event.WITHDRAW_COMMAND,max_try,wait)
        operation.__amount = amount
        operation.__address = address
        operation.__symbol = symbol
        operation.__key = key
        return operation

    @staticmethod
    def create_validate_symbol_balance(amount:float,symbol:str,market ,max_try=3,wait=60):
        operation = Operation(market,Event.VALIDATE_SYMBOL_BALANCE,max_try,wait)
        operation.__amount = amount
        operation.__symbol = symbol
        return operation

    @staticmethod
    def create_fetch_order_books(market ,symbol:str,max_try=3,wait=10,online=False): #if online is false then check from ob_service database instead of directly market itself.
        event = Event.FETCH_ORDER_BOOK if online else Event.FETCH_ORDER_BOOK_FROM_DB
        operation = Operation(market, event, max_try, wait)
        operation.__symbol = symbol
        return operation
    
    def get_orderbook_from_db(self, market_name,symbol): #symbol should be like BTC/USD
        data = {'event': 'get_order_book', 'data': None, 'private_key': 'osman_is_my_girl'}
        data.update({'data': {"market_name":market_name, "symbol_pair":symbol} }) #sample symbol should be "BTC/USD"
        str_data = json.dumps(data)
        ret = requests.get("http://ozenoglu.com:8000/api_call", data=str_data)
        ret =  json.loads(ret.content.decode())
        return ret

    def get_result(self):

        if self.__operation_type == Event.WITHDRAW_COMMAND:
            debug("Operation {:s} is started address{:s}".format(self.__operation_type,str(self.__address)))
            if self.__key != "":
                result = self.__market.withdraw(self.__symbol,self.__amount,self.__address,{'key':self.__key}) #if there is a need for key use this
            else:
                result = self.__market.withdraw(self.__symbol,self.__amount,self.__address,self.__params)

            debug("Operation result is {:s} Withdraw Amount{:f}".format(str(result),float(self.__amount)))
            return result
        
        if self.__operation_type == Event.FETCH_ORDER_BOOK_FROM_DB:
            result = None
            debug("Operation {:s} is started".format(self.__operation_type))
            try:
                result = self.get_orderbook_from_db(self.m_market.get_name(),self.__symbol)                
            except Exception as e:
                error("Error during fetching order book from db ex: {:s}".format(str(e)))
                raise e
            return result
                
        if self.__operation_type == Event.FETCH_ORDER_BOOK:
            result = None
            debug("Operation {:s} is started".format(self.__operation_type))
            try:
                result = self.__market.fetch_order_book(self.__symbol)
            except Exception as e :
                warn("Exception occured during fetching market price {:s}".format(str(e)))
                try:
                    if self.m_market.get_name() == "koineks":
                        currency = str(self.__symbol).split('/')[0]
                        fetch_request = RequestInfo("koineks", RequestType.FETCH_FOR_HELP_URGENT, currency)
                        fetch_request.set_log_file_name(currency + "_fetch_urgent_request")
                        fetch_request.push_request()
                        sleep(8)  # wait 8 secs before try again.
                        result = self.__market.fetch_order_book(self.__symbol)
                    else:
                        error("Error during fetching {:s} order book from {:s} error:{:s}".format(str(self.__symbol),self.m_market.get_name(),str(e)))
                except Exception as e:
                    error("Error during handling koineks special operation for fetching order book")
                    raise e
            #debug("Operation result is {:s}".format(result))
            return result


        if self.__operation_type == Event.LIMIT_SELL_COMMAND:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.create_limit_sell_order(self.__symbol,self.__amount,self.__limit_price)
            return result
        if self.__operation_type == Event.MARKET_SELL_COMMAND:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.create_market_sell_order(self.__symbol,self.__amount)
            debug("Operation result is {:s}".format(str(result)))
            return result
        if self.__operation_type == Event.LIMIT_BUY_COMMAND:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.create_limit_buy_order(self.__symbol,self.__amount,self.__limit_price)
            debug("Operation result is {:s}".format(str(result)))
            return result
        if self.__operation_type == Event.MARKET_BUY_COMMAND:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.create_market_buy_order(self.__symbol,self.__amount)

            debug("Operation result is {:s}".format(str(result)))

            return result
        if self.__operation_type == Event.CHECK_BALANCE_COMMAND:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.fetch_balance()
            return result
        if self.__operation_type == Event.FETCH_MARKET_PRICE:
            debug("Operation {:s} is started".format(self.__operation_type))
            result = self.__market.fetch_ticker(self.__symbol)
            debug("Operation result is {:s}".format(str(result)))
            return result

        if self.__operation_type == Event.VALIDATE_SYMBOL_BALANCE:
            debug("Operation {:s} is started".format(self.__operation_type))
            symbol_fbalance = 0
            max_try = 5
            try_count = 0 
            while(symbol_fbalance == 0 and try_count < max_try):
                try_count += 1
                sleep(1)
                data = self.__market.fetch_balance()
                symbol_fbalance = float(helper.find_symbol_fbalance(data,self.__symbol))
                symbol_fbalance = round(symbol_fbalance,4)
                try:
                    self.__amount = round(self.__amount,4)
                    if symbol_fbalance >= self.__amount:
                        debug("There is  enough balance of {:s} balance is:{:f} expecting is:{:f}".format(str(self.__symbol),float(symbol_fbalance), float(self.__amount)))
                        return {"result":True, "balance": symbol_fbalance}
                    else:
                        if(symbol_fbalance != 0): # we got the balance but it is not sufficient 
                            return {"result":False, "balance": symbol_fbalance}
                        else: 
                            continue
                except Exception as e:
                    error("Error during Operation {:s}".format(str(self.__operation_type)))                    
                    return False
        

    def operate(self):
        debug(" operation {:s} will be try to execute".format(self.__operation_type))
        if self.get_completed()== True:
            error("This is already operated operation ") #TODO Find a better way not to trigger already finished operation
            return True

        while(self.__try_count < self.__max_try_count ):
            self.__try_count += 1
            is_exception_occured = False
            result = None
            try:
                result = self.get_result()

            except Exception as e:
                error("Unhalded exception is {:s}".format(str(e)))
                is_exception_occured = True
                self.dump_operation()


            if ( result == None or is_exception_occured or result == False):

                debug("operation is failed ,system will wait before trying again for {:d}".format(self.__try_count))
                sleep(self.__wait_time_between_try)

            else:
                self.set_completed(True)
                consumer_list = self.get_consumer_list()
                debug ("count of registered consumers to notified: {:d}".format(len(consumer_list)))
                debug("CONSUMERS")
                debug(consumer_list)

                event = Event(self,self.m_market, self.__operation_type,self.__symbol, result)
                self.notify_consumers(event)

                del self
                return result
        error("Max try number {:d} is reached operation is aborting..".format(self.__max_try_count))
        event = Event(self, self.m_market, self.__operation_type, self.__symbol, Event.RESULT_FAIL)
        self.notify_consumers(event)
        return None




class Transaction(): #internal class
    def __init__(self, operations):
        self.__operation_list = operations
        self.__is_completed = False # if the transaction is completed make it True
        self.__is_error = False # if there is an error during transaction make it True
        self.__error_message = "" # if there is an error during tansaction store the error message here.
        self.__transaction_id = randint(MIN_RANDOM_RANGE,MAX_RANDOM_RANGE) # create a random integer betwen renges.
        self.__created_time = time()
        self.__cretead_time_str = str(datetime.now())
        self.__completed_time = 0
        self.__completed_time_str = ""
        self.__is_experied = False # Make it true if it's expired.
        self.__transaction_life = self.__created_time + TRANSACTION_LIFE
        debug("A new transaction is created with id {:d} at time {:s}".format(self.__transaction_id,self.__cretead_time_str))


    def get_operrations_list(self):
        return self.__operation_list

    def get_transaction_id(self):
        return self.__transaction_id

    def operate(self):

        debug("Transaction with id {:d} is started".format(self.__transaction_id))

        current_time = time()
        if (current_time  > self.__transaction_life): # if the transaction is too old , do not execute it. Market data may be changed.
            self.__is_experied = True
            self.__is_error = True
            self.__error_message = "Expired"
            return False
        else:
            self.__is_completed = True
            self.__completed_time_str = str (datetime.now())
            self.__completed_time = time()
            for operation in self.__operation_list:
                if (operation.operate() == None):
                    error("Transaction with id {:d} is failed:".format(self.__transaction_id))
                    return False

            return True


class TransactionEngine:
    def __init__(self):
        self.transactions = []
        self.completed_transactions = []
        self.failed_transactions = []
        self.__is_in_wait_mode = False # initial of transaction engine wait mode is false , user is expected to start first.

    def create_and_add_transaction(self, operations):
        if (type(operations) is not type ([])):
            if (type(operations) == type(Operation()) ):
                my_operations = []
                my_operations.append(operations)
                operations = my_operations
            else:
                raise Exception("Un supported format for operation list , type {:s}".format(str(type(operations))))


        new_transaction = Transaction(operations)
        self.transactions.append(new_transaction)
        debug("New transaction with id {:d} is created".format(new_transaction.get_transaction_id()))
        if (self.__is_in_wait_mode == True): # if it's in wait mode start engine.
            self.start_engine()

    def __get_next_transaction(self):
        if (len(self.transactions) > 0): # bugfix: out of index exception
            return self.transactions[0] # return first transaction in the list
        else:
            return None

    def __remove_transaction(self,transaction_to_delete:Transaction):
        if (len(self.transactions) >= 1):
            self.transactions.remove(transaction_to_delete)
            debug("Transaction with id {:d} is deleted".format(transaction_to_delete.get_transaction_id()))
        else:
            error("Tried to remove transaction but it's already empty!")

    def start_engine(self):

        next_transaction = self.__get_next_transaction()
        while (next_transaction is not None):
            operation_list = next_transaction.get_operrations_list()
            size = len(operation_list)
            debug("next transaction id {:s} , operations list len {:d} ".format(str(next_transaction.get_transaction_id()),size))
            if size >= 1:
                index = 0
                for operation in operation_list:
                    type = operation.get_type()
                    debug("Operation{:d} type {:s}".format(int(index),str(type)))
                    operation.dump_operation()
                    index = index + 1
            result = next_transaction.operate()
            if (result == True):
                try:
                    self.completed_transactions.append(next_transaction)
                    self.__remove_transaction(next_transaction)
                    next_transaction = self.__get_next_transaction()
                except Exception as e:
                    error("ALL TRANSACTIONS ABORTED , Exception is occured {:s}".format(str(e)))
                    self.transactions.clear() # abort all transactions
                    return
            else:
                error("Transaction Engine couldn't finish Transaction with id: {:d}".format(next_transaction.get_transaction_id()))
                self.failed_transactions.append(next_transaction)
                self.__remove_transaction(next_transaction)
                next_transaction = None
                return False
        self.__is_in_wait_mode = True # wait for until next transaction is created.
        debug("Transaction engine is in wait mode date: {:s}".format(str(datetime.now())))









#print(okcoinusd().fetch_ticker(BTC_USD))

'''
transaction_engine = TransactionEngine()
market  = okcoinusd()
fetch_price_operation = Operation.create_fetch_market_price(market, BTC_USD)
fetch_price_operation.add_consumer(self)
operation_list = []
operation_list.append(fetch_price_operation)
transaction_engine.create_and_add_transaction(operation_list)
transaction_engine.start_engine()
'''
