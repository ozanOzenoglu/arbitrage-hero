
from time import sleep
import json
import datetime

import base.crypto_engine.utils.helper as helper
from base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.crypto_engine.symbols import *
from base.crypto_engine.utils.config_manager import Config
from base.crypto_engine.engine.event import Consumer, Event
from base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine.utils.fcm import FCM

from base.crypto_engine.engine.transaction_engine import Operation, TransactionEngine


class Trader(Consumer):
    LAST_TRADER_TIME = None
    def __init__(self):
        debug("Trader is initalised")
        self.__transaction_engine = TransactionEngine()
        self.__buying_exchange = None
        self.__selling_exchange = None
        self.__avaiable_balance = 0
        self.__buying_market_first_symbol = None
        self.__buying_market_second_symbol = None
        self.__min_second_symbol_balance = 40
        self.__expected_rate = 0
        self.__bought_amount = 0
        self.__money_to_spend = 0
        self.__log_file_path = ""
        self.__tx_fee = None
        self.__operation_fee = 0
        self.__arbitrage_start_time = 0

        self.__balance_after_buy = 0
        self.__expected_received_amount = 0
        self.__expected_bought_coins = 0
        self.__symbol_address = None
        self.__send_op_params = None

        '''
        #if  you would like to implement one day , a limit buy/sell arbitrage take a look this previous coded samples.
            last_ask = self.__buying_exchange.get_last_price() # we set minumum last ask to last_price for buying exchange in op_finder.
            avarage_market_price = helper.get_twothousandth_higher_price(last_ask)
            amount_to_buy = second_symbol_balance / avarage_market_price
            amount_to_buy = amount_to_buy - (amount_to_buy/100) # buy a bit less than we afford.



            buy_op = Operation.create_limit_buy(amount_to_buy,avarage_market_price,self.__buying_exchange.related_market(),buy_symbol,5,2)


            #Kraken sample

            if (self.__buying_exchange.get_market().id == "kraken"):
                if (self.__buying_market_first_symbol == ETH):
                    send_op = Operation.create_kraken_withdraw(amount_to_buy,self.__buying_market_first_symbol,symbol_addres,self.__buying_exchange.related_market(),"cex-eth",20,3) # wait 10 secs between 1 try
                elif (self.__buying_market_first_symbol == XRP):
                    send_op = Operation.create_kraken_withdraw(amount_to_buy, self.__buying_market_first_symbol,
                                                               symbol_addres, self.__buying_exchange.related_market(),
                                                               "cex-xrp", 20, 3)  #  wait 10 secs between 1 try
                else:
                    error("Unsupported currency{:s} for kraken ".format(str(self.__buying_market_first_symbol)))
                    return


            else:
        '''

    def get_transaction_fee(self,market:str,currency:str): # TODO fetch it from config file .
        transaction_fee = 0
        if (market == "koineks"):  # set transaction  fee for koineks here.
            if (currency == "BTC"):
                transaction_fee = 0.0007
            elif (currency== "ETH"):
                transaction_fee = 0.005
            elif (currency == "LTC"):
                transaction_fee = 0.01
            elif (currency == "DASH"):
                transaction_fee = 0.002
            elif (currency == "DOGE"):
                transaction_fee = 2
            elif (currency == "XRP"):
                transaction_fee = 1
            elif (currency== "XLM"):
                transaction_fee = 0.3
            elif (currency== "XEM"):
                transaction_fee = 1
            elif (currency== "BCH"):
                transaction_fee = 0.001
            elif (currency== "BTG"):
                transaction_fee = 0.001
            else:
                raise Exception("Unsupported currency name for koineks : {:s}".format(str(currency)))
        elif market == "btcturk":
            transaction_fee =  0 # 0 for now.

        else:
            raise Exception("Unsupported Market {:s}".format(str(market)))

        return float(transaction_fee)





    def handle_event(self, event: Event):
        
        if event.get_type() == Event.LIMIT_SELL_COMMAND:
            success = event.get_data().__getitem__('success')
            amount = event.get_data().__getitem__('amount')
            symbol = event.get_data().__getitem__('symbol')
            price = event.get_data().__getitem__('price')
            if success is True:
                msg = "Trader Succeed Symbol: " + symbol + " Amount: " + str(amount) + " Price: " + str(price)      
            else :                
                msg = "Trader FAILED Symbol: " + symbol + " Amount: " + str(amount) + " Price: " + str(price)
            FCM.send_topic_message("Arbitrage Trader","FINISHED", msg, "new_opportunity")
            helper.send_mail("notify.arbitrage@gmail.com", msg)  
            error("Trader is completed : {:s}".format(str(msg))) 


        elif event.get_type() == Event.CHECK_BALANCE_COMMAND:

            self.__arbitrage_start_time = str(datetime.now())
            data = event.get_data()
            source_market = event.get_source_market()
            free_balance = helper.find_free_balance(data)
            second_symbol_balance = free_balance.__getitem__(self.__buying_market_second_symbol)
            if (float(second_symbol_balance) < self.__money_to_spend):
                error(
                    "There is not sufficent amount of money({:f}{:s}) to buy {:s}".format(float(second_symbol_balance),
                                                                                          str(
                                                                                              self.__buying_market_second_symbol),
                                                                                          str(
                                                                                              self.__buying_market_first_symbol)))
                FCM.send_topic_message("Arbitrage Trader","INSUFFICENT MONEY FOR TRADER for: " + self.__buying_market_first_symbol,"trader sufficient money", "new_opportunity")
                self.__money_to_spend = float(second_symbol_balance)

            balance_before_buy = free_balance.__getitem__(self.__buying_market_first_symbol)
            self.__buying_exchange.set_second_balance_info(second_symbol_balance)

            buy_symbol = self.__buying_market_first_symbol + '/' + self.__buying_market_second_symbol
            self.__buy_symbol = buy_symbol
            

            avarage_ask = helper.convert_usd_to_try(self.__buying_exchange.get_last_ask())
            self.__avarage_ask = avarage_ask

            # operation_fee = self.__buying_exchange.get_fee() #TODO: save operation fee to exchange.config and fetch if from there or fetch somewhere else amk
            operation_fee = 0.32
            operation_fee = operation_fee / 100

            amount_to_buy = self.__money_to_spend / avarage_ask

            expected_bought_coins = amount_to_buy
            self.__expected_bought_coins = expected_bought_coins

            fee = expected_bought_coins * operation_fee

            self.__operation_fee = float(fee)

            expected_bought_coins = expected_bought_coins - fee

            balance_after_buy = float(balance_before_buy) + expected_bought_coins
            self.__balance_after_buy = float(balance_after_buy)

            self.__expected_received_amount = expected_bought_coins



            buy_op = Operation.create_market_buy(self.__money_to_spend, self.__buying_exchange.related_market(),
                                                 buy_symbol, 2, 1)
            # validate_buy = Operation.create_validate_symbol_balance(balance_after_buy,self.__buying_market_first_symbol,self.__buying_exchange.related_market(),2,1) # wait 1 secs between total 60 tries
            # send_op = Operation.create_withdraw(expected_bought_coins,self.__buying_market_first_symbol,symbol_addres,self.__buying_exchange.related_market(),2,1,send_op_params) # wait 10 secs between 1 try
            # validate_send = Operation.create_validate_symbol_balance(balance_before_buy, self.__buying_market_first_symbol, self.__selling_exchange.related_market(), 2, 1)  # wait 1 secs between total 60 tries

            # validate_receive = Operation.create_validate_symbol_balance(expected_received_amount,self.__buying_market_first_symbol,self.__selling_exchange.related_market(),5,1) # wait 100 min to receive the currency.

            # buy , validate , send , sell operations to give in a transaction..

            op_list = [buy_op]

            consumer_list = []
            consumer_list.append(self)
            Operation.add_consumers_to_transactions(op_list, consumer_list)
            error("CHECK_BALANCE completed")
            self.__transaction_engine.create_and_add_transaction(op_list)
            return



        elif event.get_type() == Event.MARKET_BUY_COMMAND or event.get_type() == Event.LIMIT_BUY_COMMAND:
            error("Buy Event is recevied")
            try:
                data = event.get_data()  # bought currency data
                if (type(data) == type({})):
                    debug("Buy Operation data: type is dict val: {:s}".format(helper.convert_dict_to_str(data)))
                elif type(data) == type(""):
                    debug("Buy operation data: type is str val: {:s}".format(data))
                else:
                    debug("Buy operation data type is unknowon ant it's {:s}".format(str(type(data))))

                try:
                    amount = -1
                    spent_money = float(data.__getitem__('data').__getitem__('quantity'))
                    amount = spent_money / self.__avarage_ask
                    
                    if (amount >= 0 ):
                        gap = self.__expected_bought_coins - amount
                        if (gap > 0):
                            self.__balance_after_buy = self.__balance_after_buy - gap # don't try to validate that you couldn't buy.
                            self.__expected_received_amount = self.__expected_received_amount - gap # if I bought less than I wanted /could someone else stole cheap my coins before me. :/

                        self.__bought_amount = amount

                except Exception as e:
                    error("No amount data for buy operation!")

                validate_buy = Operation.create_validate_symbol_balance(self.__balance_after_buy,
                                                                        self.__buying_market_first_symbol,
                                                                        self.__buying_exchange.related_market(), 5,
                                                                        6)  # wait 1 secs between total 60 tries

                validate_buy.add_consumer(self)
                operation_list = []
                operation_list.append(validate_buy)
                
                error("MARKET_BUY_COMMAND completed")
                self.__transaction_engine.create_and_add_transaction(operation_list)

            except Exception as e:
                error("Error during reporting market buy command {:s}".format(str(e)))

       


        elif event.get_type() == Event.VALIDATE_SYMBOL_BALANCE:
            data = event.get_data()
            source_market = event.get_source_market()
            balance = data.__getitem__("balance")
            balance = helper.get_tenthousandth_lower_price(balance)                
            price = round(self.__expected_price,4)
            balance = round(balance,4)
            sell_op = Operation.create_limit_sell(balance, price,source_market ,self.__buy_symbol,3,60)
            sell_op.add_consumer(self)
            operation_list = []
            operation_list.append(sell_op)
            error("VALIDATE_SYMBOL_BALANCE completed")
            self.__transaction_engine.create_and_add_transaction(operation_list)


        return

    def save_trader_info(self, buying_exchange: ExchangeInfo,money_to_spend: float,  expected_price: float):
        error("doing arbitrage now")
        self.__buying_exchange = buying_exchange
        self.__money_to_spend = int(money_to_spend)
        
        self.__expected_price = expected_price
        # cex.privatePostGetAddress(cex.extend({'currency':'XRP'}))
        self.__buying_market_first_symbol = self.__buying_exchange.get_first_symbol()
        self.__buying_market_second_symbol = self.__buying_exchange.get_second_symbol()
        print("buying market first symbol: {:s}".format(str(self.__buying_market_first_symbol)))
        print("buying market second symbol {:s}".format(str(self.__buying_market_second_symbol)))

    def start_trader(self):
        if (Trader.LAST_TRADER_TIME is None):
             Trader.LAST_TRADER_TIME = time.time()
        elif(time.time() - Trader.LAST_TRADER_TIME < 1000 * 60):
            return
            

        operation_list = []
        get_first_symbol_balance_op = Operation.create_check_balance(self.__buying_exchange.related_market())

        get_first_symbol_balance_op.add_consumer(self)

        operation_list.append(get_first_symbol_balance_op)
        debug("trader is started")
        self.__transaction_engine.create_and_add_transaction(operation_list)
        self.__transaction_engine.start_engine()
