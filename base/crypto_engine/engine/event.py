#Abstract class of Producer

from base.crypto_engine.MessageApi.debug import *

class Event:
    ''''''
    LIMIT_BUY_COMMAND = "LIMIT_BUY"
    LIMIT_SELL_COMMAND = "LIMIT_SELL"
    MARKET_BUY_COMMAND = "MARKET_BUY"
    MARKET_SELL_COMMAND = "MARKET_SELL"
    WITHDRAW_COMMAND = "WITHDRAW_COMMAND"
    CHECK_BALANCE_COMMAND = "CHECK_BALANCE"
    FETCH_MARKET_PRICE = "FETCH_MARKET_PRICE"
    VALIDATE_SYMBOL_BALANCE = "VALIDATE_SYMBOL_BALANCE"
    FETCH_ORDER_BOOK = "FETCH_ORDER_BOOK"
    FETCH_SYMBOL_BALANCE = "FETCH_SYMBOL_BALANCE"
    RESULT_FAIL = "RESULT_FAIL"
    FETCH_ORDER_BOOK_FROM_DB = "FETCH_ORDER_BOOK_FROM_DB"



    def __init__(self,sender,source_market,event_type:str,operation_symbol:str,data):
        self.__data = data
        self.__sender = sender
        self.__type = event_type
        self.__source_market = source_market
        self.__operation_symbol = operation_symbol

    def get_type(self):
        return self.__type
    def get_source_market(self):
        return self.__source_market
    def get_sender(self):
        return self.__sender
    def get_data(self):
        return self.__data
    def get_symbol(self):
        return self.__operation_symbol

class Consumer:

    def to_string(self):
        return str(type(self))

    def handle_event(self,event:Event):
        print("Event is RECEIVED in class {:s}".format(str(type(self))))
        print(event.get_data())


class Producer:

    def __init__(self):
        self.__consumer_list = []


    def notify_consumers(self,event:Event):
        consumer_list = self.__consumer_list
        for consumer in consumer_list:
            consumer.handle_event(event)


    def add_consumer(self,consumer):
        debug("consumer is adding")
        debug(consumer.to_string())
        if (self.__consumer_list.__contains__(consumer) != True):
            self.__consumer_list.append(consumer)
        else:
            error("Consumer is already added")
    #def operate(self):

    def get_consumer_list(self):
        return self.__consumer_list
