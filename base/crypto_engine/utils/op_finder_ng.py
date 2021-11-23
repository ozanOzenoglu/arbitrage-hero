import time
import os
import threading
import json

from api.base.crypto_engine.utils import helper
from api.base.crypto_engine.utils.arbitrage import Arbitrage
from api.base.crypto_engine.utils.trader import Trader
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.crypto_engine.MessageApi.debug import *
from base.services.simulator_service import SimulatorService
from api.base.crypto_engine import symbols
from api.base.crypto_engine.utils.fcm import FCM

MAX_OP_NG_INSTANCE_AT_ONCE = 4
MAX_RUNNING_THREAD_SEM = threading.Semaphore(MAX_OP_NG_INSTANCE_AT_ONCE)
    
class OpportunityFinderNG:

    def __init__(self, delay: int , buy_exchange:ExchangeInfo,sell_exchange:ExchangeInfo,alarm_percent:int,is_only_notify:bool,is_notify_active:bool,invest_options:list):
        self.__delay = delay
        self.__healthy = True
        self.__buy_exchange = buy_exchange
        self.__sell_exchange = sell_exchange
        self.__alarm_percent = alarm_percent
        self.__is_only_notify = is_only_notify
        self.__is_notify_active = is_notify_active
        self.__curency = str(buy_exchange.get_first_symbol()).upper()
        self.__invest_options = invest_options
        self.__processing_op_queue = []
        self.__last_notification_time = None

        try:
            self.__buy_market = buy_exchange.related_market() #TODO change related_market methot as getMarket()
            self.__sell_market = sell_exchange.related_market()
        except Exception as e:
            error("Error fetching market {:s}".format(str(e)))
            self.__healthy = False



    def start_arbitrage(self,new_op:OpportunityInfo):

        if self.__is_only_notify == True:
            debug("arbitrage did not start due to only notify flag is set")
            SimulatorService.push_simulator_request(new_op)
        else:
            if new_op.get_buy_market() == "btcturk":
                trader = Trader()
                spend_money = new_op.get_buying_money()
                trader.save_trader_info(self.__buy_exchange, spend_money, new_op.get_avg_bid_try())
                trader_thread = threading.Thread(target = trader.start_trader, name = "Trader")
                trader_thread.start()
            else:
                arbitrage_op = Arbitrage()
                arbitrage_op.save_arbitrage_info(self.__buy_exchange, self.__sell_exchange, new_op.get_percent(), new_op.get_buying_money(), symbols.ARBITRAGE_LOG_FILE,new_op.get_tx_fee())
                arbitrage_thread = threading.Thread(target = arbitrage_op.start_arbitrage, name = "Arbitrage")
                arbitrage_thread.start()


    

    def notify_subscribers(self,op:OpportunityInfo):
        if self.__is_notify_active:
            try:
                jsonMsg = op.get_json()
                jsonStr = json.dumps(jsonMsg)
                simple_msg = op.to_simple_msg()
                try:
                    helper.send_mail("notify.arbitrage@gmail.com",simple_msg)
                except Exception as e:
                    error("Error during sending email notification e: {:s}".format(str(e)))
                try:
                    FCM.send_topic_message("Arbitrage Hero","New Opportunity",jsonStr, "new_opportunity")
                except Exception as e:
                    error("Error during sending android notification Ex: {:s}".format(str(e)))
                
            except Exception as e:
                error("Error during notify_subscribers {:s}".format(str(e)))



    def mark_best_op(self, list):
        current_max_percent = -999
        max_percent_index = None
        index = 0
        while index < len(self.__processing_op_queue):
            current_op = self.__processing_op_queue[index]
            percent = current_op.get_percent()
            if max_percent_index == None or current_max_percent < percent:
                max_percent_index = index
                current_max_percent = percent
            index = index + 1
        list[max_percent_index].set_table_candidate(True)
        list.append( list[max_percent_index].get_key())


    def process_new_op(self,new_op:OpportunityInfo): #here we will do things about new percent like notify subsribers , drawing table and doing arbitrage so on.
        percent = new_op.get_percent()
        # new_op.push() #send to table_service
        if (percent > symbols.WEIRD_PERCENT_THRESHOLD):
            try:
                error("Percent is too high than a normal value")
                with open(symbols.WEIRD_BUG_PATH, "a+") as weird_bug_file:
                    weird_bug_file.write(
                        "TOO HIGH PERCENT CALCULATED: {:f} Op_INFO: {:s}".format(float(percent), str(new_op.to_json())))
            except Exception as e:
                error("Error during handling high percent {:s}".format(str(e)))
            return

        if percent > self.__alarm_percent:
            now = int(time().time())
            if(now - self.__last_notification_time > symbols.NOTIFICATION_TIME_SECOND_THRESHOLD):
                self.__last_notification_time = now
                self.notify_subscribers(new_op)
                self.start_arbitrage(new_op)

        self.__processing_op_queue.append(new_op)

        if len(self.__processing_op_queue) >= len(self.__invest_options):
            self.mark_best_op(self.__processing_op_queue)
            helper.upload_opportunity_list_result(self.__processing_op_queue)
            self.__processing_op_queue.clear()
            return




    def start(self):
        global MAX_RUNNING_THREAD_SEM
        new_op = None
        while(self.__healthy):
            with(MAX_RUNNING_THREAD_SEM):
                time.sleep(1)
                operation_start_time = time.time()
                for invested_money in self.__invest_options:
                    try:
                        buying_money = invested_money #will be converted its exchange second currency if it's crossed
                        selling_money = buying_money
                        is_reliable = True
                        symbol = self.__buy_exchange.get_first_symbol()
                        buy_market = self.__buy_market.get_market()
                        is_cross_arbitrage = False
                        if (self.__buy_exchange.get_second_symbol() != self.__sell_exchange.get_second_symbol()):
                            is_cross_arbitrage = True
                        if (is_cross_arbitrage):
                            if (self.__buy_exchange.get_second_symbol() == "TRY"):
                                buying_money = helper.convert_usd_to_try(buying_money)
                            elif(self.__sell_exchange.get_second_symbol() == "TRY"):
                                selling_money = helper.convert_usd_to_try(selling_money)
                                
                        withdraw_fee_rate = self.__buy_market.get_withdraw_fee(symbol)
                        ask_taker_fee = self.__buy_market.get_trade_fee()
            
                        result_ask = self.__buy_market.get_avarage_ask(self.__buy_exchange.get_symbol(),buying_money)
                        if result_ask != -1:
                            is_ask_reliable = result_ask.__getitem__('reliable')
                            avg_ask_usd = result_ask.__getitem__('avg_usd')
                            best_ask_usd  = result_ask.__getitem__('best_usd')
                            currency = result_ask.__getitem__('currency')
                            avg_ask_try = result_ask.__getitem__('avg_try')
                            debug("avg ask try {:f}".format(avg_ask_try))
                            best_ask_try = result_ask.__getitem__('best_try')
                            self.__buy_exchange.set_avg_ask(avg_ask_usd)
                            self.__buy_exchange.set_last_ask(best_ask_usd)


                            total_bought_coins = invested_money / float(avg_ask_usd)
                            debug("total bought coins count without fee {:f}".format(float(total_bought_coins)))
                            buy_fee_expense = (ask_taker_fee / 100) * total_bought_coins
                            buy_fee_expense_usd = buy_fee_expense * avg_ask_usd
                            withdraw_expense_usd = withdraw_fee_rate * avg_ask_usd
                            total_expense_usd = buy_fee_expense_usd + withdraw_expense_usd
                            total_bought_coins = total_bought_coins - buy_fee_expense
                            debug("total buy with fee {:f}".format(float(total_bought_coins)))
                            total_received_coins = total_bought_coins - withdraw_fee_rate
                        else:
                            error("Couldn't fetched buy_market informations")
                    except Exception as e:
                        result_ask = -1
                        error("Error during gathering information about buy_market {:s} error: {:s}".format(str(self.__buy_market.get_name()),str(e)))

                    if result_ask != -1:
                        try:
                            bid_taker_fee = self.__sell_market.get_market().fees.__getitem__('trading').__getitem__('taker') * 100
                            result_bid = self.__sell_market.get_avarage_bid(self.__sell_exchange.get_symbol(),selling_money)
                            if result_bid != -1:
                                is_bid_reliable = result_bid.__getitem__('reliable') # if avg data can't calculated properly , it's not reliable..
                                avg_bid_usd = result_bid.__getitem__('avg_usd')
                                best_bid_usd = result_bid.__getitem__('best_usd')
                                currency = result_bid.__getitem__('currency')
                                avg_bid_try = result_bid.__getitem__('avg_try')
                                best_bid_try = result_bid.__getitem__('best_try')
                                self.__sell_exchange.set_avg_bid(avg_bid_usd) #are you using it ?
                                self.__sell_exchange.set_last_bid(best_bid_usd) #are you using it ?

                                sell_fee_expense = (bid_taker_fee / 100) * total_received_coins
                                selling_fee_expnse_usd = sell_fee_expense * avg_bid_usd
                                total_expense_usd = total_expense_usd + selling_fee_expnse_usd

                                return_money = (total_received_coins - sell_fee_expense) * avg_bid_usd

                                debug("return_money after selling fee expense {:f}".format(float(return_money)))

                                #return_money = return_money - (return_money * (bid_taker_fee / 100))

                                debug("total_sell money with fee {:f}".format(float(return_money)))
                            else:
                                error("Couldn't fetched sell market informations")
                        except Exception as e:
                            error("Error during gathering information about sell_market {:s} error: {:s}".format(str(self.__sell_market.get_name()),str(e)))



                    if (result_ask != -1 and result_bid != -1):


                        gap = return_money - invested_money
                        percent = (gap / invested_money) * 100
                        #percent = percent -(withdraw_fee + ask_taker_fee + bid_taker_fee)

                        new_op = OpportunityInfo("op_finder",self.__buy_market.get_name(),self.__sell_market.get_name(),self.__curency,self.__buy_exchange.get_second_symbol(), percent,is_ask_reliable,is_bid_reliable,new_op)
                        if is_cross_arbitrage:
                            new_op.set_cross_currency(self.__sell_exchange.get_second_symbol())

                        new_op.set_avg_ask_usd(avg_ask_usd)
                        new_op.set_avg_ask_try(avg_ask_try)
                        new_op.set_best_ask_usd(best_ask_usd)
                        new_op.set_best_ask_try(best_ask_try)

                        new_op.set_avg_bid_usd(avg_bid_usd)
                        new_op.set_avg_bid_try(avg_bid_try)
                        new_op.set_best_bid_usd(best_bid_usd)
                        new_op.set_best_bid_try(best_bid_try)

                        #Expenses for operation(buying selling fees and transaction fee)
                        new_op.set_buy_fee(buy_fee_expense_usd)
                        new_op.set_sell_fee(selling_fee_expnse_usd)
                        new_op.set_tx_fee(withdraw_expense_usd)
                        new_op.set_total_fee(total_expense_usd)
                        new_op.set_buying_money(buying_money)
                        new_op.set_spent_money(invested_money) # the money we're spending for arbitrage
                        new_op.set_buy_amount(total_bought_coins) # the coin's amount that we're buying
                        new_op.set_return_money(return_money) # the expected  return money on sell market when we sell our coins
                        simple_msg = new_op.to_simple_msg()
                        user_feedback("OP_FINDER: {:s}".format(str(simple_msg)))
                        new_op.set_avaiable_invest_options(self.__invest_options)
                        self.process_new_op(new_op)
                        #time.sleep(2)

            operation_finish_time = time.time()
            spend_time = operation_finish_time - operation_start_time
            wait_sec = self.__delay - spend_time
            if (wait_sec > 0):
                user_feedback("Wait {:d} sec before next cycle".format(int(wait_sec)))
                time.sleep(wait_sec)
            else:
                error("Operation time {:d} more than delay time {:d}".format(int(spend_time), int(self.__delay)))
