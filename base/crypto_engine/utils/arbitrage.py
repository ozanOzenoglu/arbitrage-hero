
from time import sleep
import json
import datetime

import base.crypto_engine.utils.helper as helper
from base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.crypto_engine.symbols import *
from base.crypto_engine.utils.config_manager import Config
from base.crypto_engine.engine.event import Consumer, Event
from base.crypto_engine.MessageApi.debug import *

from base.crypto_engine.engine.transaction_engine import Operation, TransactionEngine


class Arbitrage(Consumer):

    def __init__(self):
        debug("Arbitrage is initalised")
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




    def __report(self, msg):

        try:
            android_alarm(msg)
            user_feedback(msg)
        except Exception as e:
            error("Error during android_alarm and user_feedback")

        with open(self.__log_file_path, 'wb') as outputfile:
            byte_array = bytearray(json.dumps(msg), 'utf8')
            outputfile.write(byte_array)

    def handle_event(self, event: Event):
        if event.get_type() == Event.MARKET_SELL_COMMAND:
            data = event.get_data()

            data_as_str = ""

            try:
                data_as_str = str(data)
                self.__report(data_as_str)
            except Exception as e:
                try:
                    error("MARKET SELL COMMAND Result could not converted to string! it's type  {:s}".format(
                        str(type(data))))
                except Exception as e:
                    error("During handling exception another exception occured it's :{:s}".format(str(e)))

            started_time = self.__arbitrage_start_time.split(':')
            started_min = float(started_time[1])
            started_sec = float(started_time[2])

            end = str(datetime.now())

            end_time = end.split(':')
            end_min = float(end_time[1])
            end_sec = float(end_time[2])

            total_secs = (end_min - started_min) * 60 + (end_sec - started_sec)

            secs = total_secs % 60

            mins = int(total_secs / 60)

            arbitrage_report_msg = "Arbitrage is done Invest Money {:f}{:s} from {:s} to {:s} using {:s} Buying Price:{:f} S{:s} spent time {:d}:{:d}".format(
                float(self.__money_to_spend),
                str(self.__buying_market_second_symbol),
                str(self.__buying_exchange.get_market().id),
                str(self.__selling_exchange.get_market().id),
                str(self.__buying_market_second_symbol),
                float(self.__buying_exchange.get_last_ask()),
                str(self.__buying_market_first_symbol),
                int(mins),
                int(secs))
            self.__report(arbitrage_report_msg)
            error("Arbitrage is finished byy")
            exit(31)


        elif event.get_type() == Event.CHECK_BALANCE_COMMAND:

            error("Balance check event is recevied")

            self.__arbitrage_start_time = str(datetime.now())

            data = event.get_data()



            source_market = event.get_source_market()

            if source_market == self.__selling_exchange.related_market(): #Selling Market Second Balance Fetch Operation

                free_balance = helper.find_free_balance(data)
                first_symbol_balance = free_balance.__getitem__(self.__buying_market_first_symbol) # how much money we already have before arbitrage operation in selling exchange!

                self.__selling_exchange.set_first_balance_info(first_symbol_balance)
                debug("In Market:{:s} Current {:s} balance is {:f}".format(str(self.__selling_exchange.related_market().get_name()),
                                                                       str(self.__buying_market_first_symbol),
                                                                       float(first_symbol_balance)))
                return









            free_balance = helper.find_free_balance(data)
            second_symbol_balance = free_balance.__getitem__(self.__buying_market_second_symbol)

            if (float(second_symbol_balance) < self.__money_to_spend):
                error(
                    "There is not sufficent amount of money({:f}{:s}) to buy {:s}".format(float(second_symbol_balance),
                                                                                          str(
                                                                                              self.__buying_market_second_symbol),
                                                                                          str(
                                                                                              self.__buying_market_first_symbol)))
                return

            balance_before_buy = free_balance.__getitem__(self.__buying_market_first_symbol)
            self.__buying_exchange.set_second_balance_info(second_symbol_balance)

            buy_symbol = self.__buying_market_first_symbol + '/' + self.__buying_market_second_symbol

            symbol_address = self.__selling_exchange.get_address()
            self.__symbol_address = symbol_address
            avarage_ask = self.__buying_exchange.get_last_ask()

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

            error("before buy {:f} bought{:f} fee {:f} after bought {:f}".format(float(balance_before_buy),
                                                                                 float(expected_bought_coins),
                                                                                 float(fee),
                                                                                 float(balance_after_buy)))

            # expected_received_amount = expected_bought_coins - self.__tx_fee.__getitem__(self.__buying_market_first_symbol)
            fee_key = self.__buying_market_first_symbol + '/' + self.__buying_market_second_symbol
            transaction_fee = 0
            try:
                transaction_fee = self.get_transaction_fee(self.__buying_exchange.related_market().get_name(),self.__buying_market_first_symbol)
                #transaction_fee = self.__tx_fee.__getitem__(fee_key)
            except Exception as e:
                error("transaction fee couldn't found for {:s} , {:f} will be used as default".format(str(fee_key),
                                                                                                      float(0.01)))
                transaction_fee = 0.01





            expected_received_amount = expected_bought_coins - transaction_fee  # tx_fee is transaction fee , differs from operatinal fee in market
            # buying_fee = self.__tx_fees.__getitem__(self.__buying_market_first_symbol) #Calculate fee to estimate expected receving fund

            self.__expected_received_amount = expected_received_amount

            # buy , validate , send , sell operations to give in a transaction..

            # Operations in buying exchange market in order , BUY -> VALIDATE -> SEND -> VALIDATE

            buy_market_name = self.__buying_exchange.related_market().get_name()
            sell_market_name = self.__selling_exchange.related_market().get_name()

            log_file_name = buy_market_name + "_" + sell_market_name + "_" + self.__buying_market_first_symbol

            send_op_params = {"log_file_name": log_file_name}
            self.__send_op_params = send_op_params

            if ExchangeInfo.tagable_currency(self.__buying_market_first_symbol):
                tag = self.__selling_exchange.get_tag()
                send_op_params.update({"tag": tag})

            #self.__money_to_spend = 0  # don't buy anything mak
            #BURADA KOINEKS ISE PRICE HESAPLA VER!

            if (self.__buying_exchange.related_market().get_name() == "koineks"):
                buy_op = Operation.create_limit_buy(amount_to_buy,avarage_ask,self.__buying_exchange.related_market(),buy_symbol,2,1)
            else:
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
                    price = -1
                    price = data.__getitem__('price')


                except Exception as e:
                    debug("No price data for buy operation!")

                try:
                    amount = -1
                    amount = float(data.__getitem__('data').__getitem__('quantity'))

                    if (amount >= 0 ):
                        gap = self.__expected_bought_coins - amount
                        if (gap > 0):
                            self.__balance_after_buy = self.__balance_after_buy - gap # don't try to validate that you couldn't buy.
                            self.__expected_received_amount = self.__expected_received_amount - gap # if I bought less than I wanted /could someone else stole cheap my coins before me. :/

                        self.__bought_amount = amount
                        self.__report("Bought {:f}{:s} price:{:f}".format(float(amount),  str(self.__buying_market_first_symbol),  float(price)))

                except Exception as e:
                    debug("No amount data for buy operation!")



                validate_buy = Operation.create_validate_symbol_balance(self.__balance_after_buy,
                                                                        self.__buying_market_first_symbol,
                                                                        self.__buying_exchange.related_market(), 5,
                                                                        6)  # wait 1 secs between total 60 tries

                validate_buy.add_consumer(self)
                operation_list = []
                operation_list.append(validate_buy)

                self.__transaction_engine.create_and_add_transaction(operation_list)

            except Exception as e:
                error("Error during reporting market buy command {:s}".format(str(e)))

        elif event.get_type() == Event.WITHDRAW_COMMAND:
            debug("Currency Send Event is recevied")
            debug("result is {:s}".format(str(event.get_data())))
            data = event.get_data()
            if (type(data) == dict):
                amount = data.__getitem__('amount')
            else:
                amount = event.get_data()  # bought currency data

            if (type(amount) is not float):
                try:
                    error("Probably we got error , cos withdraw result is {:s}".format(str(event.get_data())))
                    android_alarm("FATAL ERROR NEED ATTENTION , ARBITRAGE COULDN'T COMPLETE , DO IT YOURSELF : {:s} -> {:s} : {:s} : {:f}".format(str(self.__buying_exchange.related_market().get_name()),
                                                                                                                                                      str(self.__selling_exchange.related_market().get_name()),
                                                                                                                                                      str(self.__buying_market_first_symbol),
                                                                                                                                                      float(self.__expected_received_amount)))
                    android_alarm("WITHDRAW_COMMAND RESULT : {:s}".format(str(data)))
                except Exception as e:
                    error("WTF MAN!: {:s}".format(str(e)))
                    exit(-3131)



            total_second_symbol_balance = self.__selling_exchange.get_first_symbol_balance_info() + self.__expected_received_amount
            validate_receive = Operation.create_validate_symbol_balance(total_second_symbol_balance,
                                                                        self.__buying_market_first_symbol,
                                                                        self.__selling_exchange.related_market(), 150,
                                                                        2)  #  wait 100 min to receive the currency.
            validate_receive.add_consumer(self)
            operation_list = []
            operation_list.append(validate_receive)
            self.__transaction_engine.create_and_add_transaction(operation_list)

            android_alarm("Sent {:f}{:s} ".format(float(amount), str(self.__buying_market_first_symbol)))



        elif event.get_type() == Event.VALIDATE_SYMBOL_BALANCE:
            data = event.get_data()
            error("validate symbol balance data is received")
            print("data is {:s}".format(str(data)))
            source_market = event.get_source_market()

            if (data == "RESULT_FAIL"):
                if source_market == self.__buying_exchange.related_market():  # Validate buy Operation
                    error("Couldn't validate bought coins !")
                    return
                else:
                    error("Coins bought and sent but couldn't received in given time!")
                    android_alarm("Coins in the air!! {:s}".format(self.__log_file_path))
            if source_market == self.__buying_exchange.related_market(): #Validate buy Operation

                if (str(data).upper().__contains__('TRUE') is not True):
                    error("validate balance for is failed")
                    return

                #SEEENNNDDD
                send_op = Operation.create_withdraw(self.__bought_amount, self.__buying_market_first_symbol,
                                                    self.__symbol_address, self.__buying_exchange.related_market(), 2,
                                                    1,
                                                    self.__send_op_params)  #  wait 10 secs between 1 try
                send_op.add_consumer(self)
                operation_list = []
                operation_list.append(send_op)

                self.__transaction_engine.create_and_add_transaction(operation_list)


            elif source_market == self.__selling_exchange.related_market(): #Validate Receive Operation

                #BURADA_KOINEKSSE PRICE_HESAPLA_VER

                if (source_market.get_name() == "koineks"):
                    raise Exception("Not implemented yet")


                sell_op = Operation.create_market_sell(self.__expected_received_amount,
                                                       self.__selling_exchange.related_market(),
                                                       self.__selling_exchange.get_symbol(), 10, 1)

                sell_op.add_consumer(self)

                operation_list = []
                operation_list.append(sell_op)
                self.__transaction_engine.create_and_add_transaction(operation_list)

        return

    def save_arbitrage_info(self, buying_exchange: ExchangeInfo, selling_exchange: ExchangeInfo, expected_rate: float,
                            money_to_spend: float, log_file_path: str, tx_fee: dict):
        print("doing arbitrage now")
        self.__buying_exchange = buying_exchange
        self.__selling_exchange = selling_exchange
        self.__expected_rate = expected_rate
        self.__money_to_spend = money_to_spend
        self.__log_file_path = log_file_path
        self.__tx_fee = tx_fee
        # cex.privatePostGetAddress(cex.extend({'currency':'XRP'}))
        self.__buying_market_first_symbol = self.__buying_exchange.get_first_symbol()
        self.__buying_market_second_symbol = self.__buying_exchange.get_second_symbol()
        print("buying market fs: {:s}".format(str(self.__buying_market_first_symbol)))
        print("buying market ss {:s}".format(str(self.__buying_market_second_symbol)))

    def start_arbitrage(self):
        if (self.__money_to_spend >= 100):
            error("Invest Money Guard is HEERREEE , money to wish to spend {:f}".format(float(self.__money_to_spend)))

        operation_list = []
        get_first_symbol_balance_op = Operation.create_check_balance(self.__buying_exchange.related_market())
        get_second_symbol_balance_op = Operation.create_check_balance(self.__selling_exchange.related_market())

        get_first_symbol_balance_op.add_consumer(self)
        get_second_symbol_balance_op.add_consumer(self)

        operation_list.append(get_first_symbol_balance_op)
        operation_list.append(get_second_symbol_balance_op)
        debug("arbitrage is started")
        self.__transaction_engine.create_and_add_transaction(operation_list)
        self.__transaction_engine.start_engine()
