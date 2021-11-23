import time
import datetime
import os
import json
from base.crypto_engine.MessageApi.debug import *

from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message
from base.crypto_engine.utils import helper
from base.crypto_engine import symbols



class OpportunityInfo(Info):

    #Percent will increase in this situation
    BOTH_INCREASED = "BOTH_INCREASED"
    BID_INCREASED = "BID_INCREASED"
    ASK_DECREASED = "ASK_DECREASED"
    ASK_DECREASED_BID_INCREASED = "ASK_DECREASED_BID_INCREASED"
    BOTH_DECREASED = "BOTH_DECREASED"
    #Percent will decrease in this situation
    ASK_INCREASED_BID_DECREASED = "ASK_INCREASED_BID_DECREASED"
    ASK_INCREASED = "ASK_INCREASED"
    BID_DECREASED = "BID_DECREASED"
    #No change will be.
    NO_CHANGE = "NO_CHANGE"

    AVG_HISTORY_MAX_SAMPLE_COUNT = 4 #Maximum element count in the history list that should be calculated for finding avg history price


    def init_from_parent(self,parent):
        if (parent != None):
            avg_ask_history = parent.get_avg_ask_history()
            avg_bid_history = parent.get_avg_bid_history()
            previous_percent = parent.get_percent()
            previous_reason = parent.get_reason()

            if (avg_ask_history != None and avg_bid_history != None and previous_percent != None and previous_reason != None):
                self.append_avg_ask_history(avg_ask_history)
                self.append_avg_bid_history(avg_bid_history)
                self.set_previous_percent(previous_percent)
                self.set_previous_reason(previous_reason)
            else:
                raise Exception("Missing val in parent op!")


    def __init__(self,creator:str,buy_market:str,sell_market:str,
                 currency:str,second_currency:str,percent:float,
                 ask_reliable:bool,bid_reliable:bool,parent=None,
                 avg_ask_usd=0,avg_ask_try=0,best_ask_usd=0,
                 best_ask_try=0,avg_bid_usd=0,avg_bid_try=0,
                 best_bid_usd=0,best_bid_try=0 ,
                 buyable_amount:float=0,spent_money:float=0,
                 return_money:float=0, total_fee:float=0,
                 buy_fee:float=0,sell_fee:float=0,tx_fee:float=0,
                 table_candidate:bool=False, avaiable_invest_options:list=[]):
        super().__init__() # call parent constructor
        self.__avaiable_invest_options = avaiable_invest_options
        
        self.__table_candidate = table_candidate
        self.__tx_fee = tx_fee
        self.__buy_fee = buy_fee
        self.__sell_fee = sell_fee
        self.__total_fee = total_fee
        self.__reason = None # this is the reason why opportunity is occured..
        self.__buy_market = buy_market
        self.__avg_bid_usd = avg_bid_usd
        self.__avg_bid_try = avg_bid_try
        self.__best_bid_usd = best_bid_usd
        self.__best_bid_try = best_bid_try
        self.__avg_ask_usd = avg_ask_usd
        self.__avg_ask_try = avg_ask_try
        self.__best_ask_usd = best_ask_usd
        self.__best_ask_try = best_ask_try
        self.__sell_market = sell_market
        self.__currency = currency
        self.__second_currency = second_currency
        self.__cross_currency = ""
        self.__percent = percent
        self.__buying_money = 0
        self.__buyable_currency_amount = buyable_amount # buyable amount of currency with investing money (cheap tokens in other words)
        self.__spent_money = spent_money # the money that will be spending for buying
        self.__return_money = return_money # the return money that we'll have when we sell tokens on selling market.
        self.__ask_reliable = ask_reliable # if avg data can't calculated properly , it's not reliable...
        self.__bid_reliable = bid_reliable # if avg data can't calculated properly , it's not reliable...
        self.__tstmp  = int(round(time.time() * 1000))
        self.__update_date = str(datetime.now())
        self.__type = self._calculate_type(currency) # this can be (platin,bronze,gold. etc)
        self.__op_info_creator = creator
        self.__avg_ask_history = []
        self.__avg_bid_history = []
        self.__reason = None
        self.__reason_reliable = False
        self.__previous_percent = None
        self.__previous_reason = None
        self._json_message = ArbitrageResultInfoMsg(self)
        if parent != None:
            self.init_from_parent(parent)


    op_info_types_table = {
        "BRONZE": ["BTC","BCH","BTG","USDT","DOGE","DASH"],
        "GOLD": ["ETH","XLM","XEM","ETC","LTC"],
        "PLATIN" : ["XRP","TRX"]
                           }

    def is_reason_reliable(self):
        if (self.__reason == None):
            self._find_reason()
        return self.__reason_reliable

    def get_json(self):
        myJson = self._json_message._to_string()
        result = myJson.get(list(myJson.keys())[0])
        return result
    
    def get_reason(self):
        if (self.__reason == None):
            self._find_reason()
        return self.__reason

    def get_avaiable_invest_options(self):
        return self.__avaiable_invest_options
    def set_avaiable_invest_options(self, val:list):
        self.__avaiable_invest_options = val

    def _find_reason(self):
        previous_percent = self.get_previous_percent()
        if previous_percent != self.get_percent() or self.__previous_reason == None:
            user_feedback("New reason will calculate for new op_info")
            last_ask_usd = self.get_avg_ask_usd() #current avg_ask
            history_ask = self.get_history_ask() #historical avg_ask data
            last_bid_usd = self.get_avg_bid_usd() # current avg bid
            history_bid = self.get_history_bid() #historical avg_bid data
            if (last_ask_usd == None or history_ask == None or last_bid_usd == None or history_bid == None):
                raise Exception("last_ask_usd , history_ask , last_bid_uas or history_bid is null!")

            ask_change = last_ask_usd - history_ask
            bid_change = last_bid_usd - history_bid
            ask_change_rate = ask_change / history_ask
            bid_change_rate = bid_change / history_bid


            if (ask_change_rate > 0 and bid_change_rate > 0):  # 0.(+,+)(ikide artmış , source yavas kalmış %100 destination)
                self.__reason = OpportunityInfo.BOTH_INCREASED
            elif (ask_change_rate == 0 and bid_change_rate > 0):  # 1.(0,+)(source uyanamamış , piyasa artmış %100 destination)
                self.__reason = OpportunityInfo.BID_INCREASED
            elif (ask_change_rate < 0 and bid_change_rate == 0):  # 2.(-,0)(source da biri ucuza mal koymuş , %100 source)
                self.__reason = OpportunityInfo.ASK_DECREASED
            elif (ask_change_rate < 0 and bid_change_rate > 0):  # 3.(-,+)(source da biri ucuza mal koymuş ,piyasa da artmış , Hesaplanacak)
                self.__reason = OpportunityInfo.ASK_DECREASED_BID_INCREASED
            elif (ask_change_rate < 0 and bid_change_rate < 0):  # 4.(-,-)(source da piyasada düşüyor , ama source daha hızlı , %100 Source)
                self.__reason = OpportunityInfo.BOTH_DECREASED
            elif (ask_change_rate > 0 and bid_change_rate < 0): # 5. (+,-)
                self.__reason = OpportunityInfo.ASK_INCREASED_BID_DECREASED
            elif (ask_change_rate > 0 and bid_change_rate == 0): #6. (+,0)
                self.__reason = OpportunityInfo.ASK_INCREASED
            elif (ask_change_rate == 0 and bid_change_rate < 0): #7. (0,-)
                self.__reason = OpportunityInfo.BID_DECREASED #8. (0,0)
            else:
                self.__reason = OpportunityInfo.NO_CHANGE
        else:
            self.__reason = self.__previous_reason
            user_feedback("Previous Reason re-use")

        if (len(self.__avg_ask_history) >= OpportunityInfo.AVG_HISTORY_MAX_SAMPLE_COUNT):
            self.__reason_reliable = True
        else:
            self.__reason_reliable = False
    
    def set_buying_money(self, buying_money):
        self.__buying_money = buying_money
    def get_buying_money(self):
        return self.__buying_money
    
    def get_previous_percent(self):
        return self.__previous_percent

    def set_previous_percent(self,val):
        self.__previous_percent = val

    def get_previous_reason(self):
        return self.__previous_reason
    def set_previous_reason(self,val):
        self.__previous_reason = val

    def get_avg_ask_history(self):
        return self.__avg_ask_history
    def get_avg_bid_history(self):
        return self.__avg_bid_history
    def append_avg_ask_history(self,values:tuple):
        for value in values:
            self.add_avg_ask_info(value)
    def append_avg_bid_history(self,values:tuple):
        for value in values:
            self.add_avg_bid_info(value)

    def add_avg_ask_info(self,last_avg_ask):
        if len(self.__avg_ask_history) > OpportunityInfo.AVG_HISTORY_MAX_SAMPLE_COUNT:
            self.__avg_ask_history.pop(0)
        self.__avg_ask_history.append(last_avg_ask)

    def get_history_ask(self):
        total = sum(self.__avg_ask_history)
        avg = total / len(self.__avg_ask_history)
        return avg

    def add_avg_bid_info(self, last_avg_bid):
        if len(self.__avg_bid_history) > OpportunityInfo.AVG_HISTORY_MAX_SAMPLE_COUNT:
            self.__avg_bid_history.pop(0)
        self.__avg_bid_history.append(last_avg_bid)

    def get_history_bid(self):
        total = sum(self.__avg_bid_history)
        avg = total / len(self.__avg_bid_history)
        return avg



    def _calculate_type(self,currency:str):
        try:
            bronze_table = OpportunityInfo.op_info_types_table.__getitem__("BRONZE")
            gold_table = OpportunityInfo.op_info_types_table.__getitem__("GOLD")
            platin_table = OpportunityInfo.op_info_types_table.__getitem__("PLATIN")

            if (bronze_table.__contains__(currency)):
                return "bronze"
            elif (gold_table.__contains__(currency)):
                return "gold"
            elif (platin_table.__contains__(currency)):
                return "platin"
            else:
                return "unspecified"
        except Exception as e:
            error("Error during type identifiation : {:s}".format(str(e)))
            return "unspecified"

    def set_type(self,val:str):
        self.__type = val.lower()

    def get_type(self):
        return self.__type

    def get_creator(self):
        return self.__op_info_creator


    def set_op_info_creator(self,val:str):
        self.__op_info_creator = val

    def set_percent(self,val):
        self.__percent = val
    def set_bid_reliable(self,val:bool):
        self.__bid_reliable = val
    def set_ask_reliable(self,val:bool):
        self.__ask_reliable = val

    def set_cross_currency(self,val:str):
        self.__cross_currency = val
    def get_cross_currency(self):
        return self.__cross_currency

    def get_buy_market(self):
        return self.__buy_market
    def get_sell_market(self):
        return self.__sell_market
    #bid getters
    def get_avg_bid_usd(self):
        return self.__avg_bid_usd
    def get_avg_bid_try(self):
        return self.__avg_bid_try
    def get_best_bid_usd(self):
        return self.__best_bid_usd
    def get_best_bid_try(self):
        return self.__best_bid_try

    def get_update_date(self):
        return self.__update_date
    #bid setters
    def set_avg_bid_usd(self,val):
        self.__avg_bid_usd = val
        self.add_avg_bid_info(val)

    def set_avg_bid_try(self,val):
        self.__avg_bid_try= val
    def set_best_bid_usd(self,val):
        self.__best_bid_usd= val
    def set_best_bid_try(self,val):
        self.__best_bid_try= val

    @staticmethod
    def dump_op(op_json_str:str, dump_file_path:str):
        try:
            with(open (dump_file_path , "w")) as request_file:
                request_file.write(op_json_str)
                debug("Request {:s} pushed".format(str(dump_file_path)))
        except Exception as e:
            error("Error during dumping op to file {:s} Error:{:s}".format(str(dump_file_path),str(e)))
            
    def push(self):
        now = str(time.time()).split(".")[0]
        request_file_name = self.get_buy_market() + "_" + self.get_sell_market() + "_" + self.get_currency().lower() + "_table_" + now + ".request"
        try:
            request_as_str = json.dumps( self.to_json() )
            table_request_file_path = symbols.TABLE_REQUEST_DIR + request_file_name
            statistic_table_request_file_path = symbols.STATISTIC_TABLE_REQUEST_DIR + request_file_name
            statistic_request_file_path = symbols.STATISTIC_REQUEST_DIR + request_file_name
            OpportunityInfo.dump_op(request_as_str, table_request_file_path)
            OpportunityInfo.dump_op(request_as_str, statistic_request_file_path)
            OpportunityInfo.dump_op(request_as_str, statistic_table_request_file_path)
            return 0
        except Exception as e:
            error(str(e))
            return -1

    #ask getters
    def get_avg_ask_usd(self):
        return self.__avg_ask_usd
    def get_avg_ask_try(self):
        return self.__avg_ask_try
    def get_best_ask_usd(self):
        return self.__best_ask_usd
    def get_best_ask_try(self):
        return self.__best_ask_try

    #ask setters
    def set_avg_ask_usd(self,val):
        self.__avg_ask_usd = val
        self.add_avg_ask_info(val)
    def set_avg_ask_try(self,val):
        self.__avg_ask_try= val
    def set_best_ask_usd(self,val):
        self.__best_ask_usd= val
    def set_best_ask_try(self,val):
        self.__best_ask_try= val

    # buy_amount , spent_money , return money (get,set)
    def set_buy_amount(self,val:float):
        self.__buyable_currency_amount = val
    def get_buy_amount(self):
        return self.__buyable_currency_amount
    def set_spent_money(self,val:float):
        self.__spent_money = val
    def get_spent_money(self):
        return self.__spent_money
    def set_return_money(self,val:float):
        self.__return_money = val
    def get_return_money(self):
        return self.__return_money


    def get_second_currency(self):
        return self.__second_currency
    def get_currency(self):
        return self.__currency
    def get_percent(self):
        return self.__percent
    def get_ask_reliable(self):
        return self.__ask_reliable
    def get_bid_reliable(self):
        return self.__bid_reliable
    def get_tstmp(self):
        return self.__tstmp
    def get_key(self):
        return self.__buy_market + '_' + self.__sell_market + '_' + self.__currency + '_' + str(self.__spent_money)
    def get_file_name(self):
        return self.get_key()  +  "_opportunity.json"
    
    def get_simple_name(self):
        return  self.__buy_market + '_' + self.__sell_market + '_' + self.__currency 

    def get_total_fee(self):
        return self.__total_fee

    def set_total_fee(self, val):
        self.__total_fee = val

    def get_buy_fee(self):
        return self.__buy_fee

    def set_buy_fee(self, val):
        self.__buy_fee = val

    def get_sell_fee(self):
        return self.__sell_fee

    def set_sell_fee(self, val):
        self.__sell_fee = val

    def get_tx_fee(self):  # transaction
        return self.__tx_fee

    def set_tx_fee(self, val):
        self.__tx_fee = val

    def get_table_candidate(self):
        return self.__table_candidate

    def set_table_candidate(self,val):
        self.__table_candidate = val

    def upload_result(self):
        file_name = self.get_file_name()
        file_path = '/tmp/' + file_name
        with open(file_path,'wb') as result_file:
            byte_array = bytearray(json.dumps(self.to_json()), 'utf8')
            result_file.write(byte_array)

        helper.upload_opportunity_result(file_path)


    def to_very_simple_msg(self):
        total_fee = str(self.get_total_fee()) + "USD"
        avg_ask = str(self.get_avg_ask_usd()) + "USD"
        avg_bid = str(self.get_avg_bid_usd()) + "USD"
        spent_money = self.get_spent_money()
        return_money = self.get_return_money()
        is_reason_reliable = "Reliable" if self.is_reason_reliable() else "Not Reliable"
        result = "Reason:{:s}:[{:s}] %{:f} {:s} {:s}->{:s}  AvgAsk:{:s}  AvgBid:{:s}  SpentMoney:{:f} ReturnMoney:{:f} TotalFee:{:s}".\
            format(str(self.get_reason()),
                   str(is_reason_reliable),
                   self.__percent,
                   self.__currency,
                   self.__buy_market,
                   self.__sell_market,
                   avg_ask,
                   avg_bid,
                   spent_money,
                   return_money,
                   total_fee
                   )
        return result

    def to_simple_msg(self):
        total_fee = str(self.get_total_fee()) + "USD"
        buy_fee = str(self.get_buy_fee()) + "USD"
        sell_fee = str(self.get_sell_fee()) + "USD"
        tx_fee = str(self.get_tx_fee()) + "USD"

        best_bid = str(self.get_best_bid_try()) + "TRY" if helper.is_turkish(self.__sell_market) else str(self.get_best_bid_usd()) + "USD"
        best_ask = str(self.get_best_ask_try()) + "TRY" if helper.is_turkish(self.__buy_market) else str(self.get_best_ask_usd()) + "USD"
        avg_ask = str(self.get_avg_ask_try()) + "TRY" if helper.is_turkish(self.__buy_market) else str(self.get_avg_ask_usd()) + "USD"
        avg_bid = str(self.get_avg_bid_try()) + "TRY" if helper.is_turkish(self.__sell_market) else str(self.get_avg_bid_usd()) + "USD"
        avg_ask_reliable = "Reliable" if self.__ask_reliable else "Not Reliable"
        avg_bid_reliable = "Reliable" if self.__bid_reliable else "Not Reliable"
        spent_money = self.get_spent_money()
        buy_amount  = self.get_buy_amount()
        return_money = self.get_return_money()
        is_reason_reliable = "Reliable" if self.is_reason_reliable() else "Not Reliable"
        result = "\n###\n" \
                 "# Reason:{:s}:[{:s}]\n" \
                 "# %{:f} {:s} {:s}->{:s}\n" \
                 "# BestAsk:{:s}\t BestBid:{:s} {:s} \n" \
                 "# AvgAsk:{:s} {:s}\t AvgBid:{:s} \n" \
                 "# BuyAmount:{:f}\tSpentMoney:{:f}\tReturnMoney:{:f}\n" \
                 "# TotalFee:{:s}\tBuyFee:{:s}\tSellFee:{:s}\tTxFee:{:s}".\
            format(str(self.get_reason()),
                   str(is_reason_reliable),
                   self.__percent,
                   self.__currency , self.__buy_market,self.__sell_market,
                   best_ask,best_bid,avg_ask_reliable,avg_ask,
                   avg_bid_reliable,avg_bid,buy_amount,spent_money,
                   return_money, total_fee, buy_fee, sell_fee, tx_fee)
        return result

    @staticmethod
    def json_to_instance(data:dict):
        try:
            avaiable_invest_options = data.__getitem__("invest_options")
            table_candidate = data.__getitem__('table_candidate')
            total_fee = data.__getitem__('total_fee')
            buy_fee = data.__getitem__('buy_fee')
            sell_fee = data.__getitem__('sell_fee')
            tx_fee = data.__getitem__('tx_fee')
            op_info_creator = data.__getitem__('op_info_creator')
            spent_money = float(data.__getitem__('spent_money'))
            buy_amount = float(data.__getitem__('buy_amount'))
            return_money = float(data.__getitem__('return_money'))
            ask_reliable = bool(data.__getitem__('ask_reliable'))
            bid_reliable = bool(data.__getitem__('bid_reliable'))
            percent = float(data.__getitem__('percent'))
            buy_market = data.__getitem__('buy_market')
            sell_market = data.__getitem__('sell_market')
            currency = data.__getitem__('currency')
            second_currency = data.__getitem__('second_currency')
            cross_currency = data.__getitem__('cross_currency')
            avg_bid_usd = data.__getitem__('avg_bid_usd')
            avg_bid_try = data.__getitem__('avg_bid_try')
            best_bid_usd = data.__getitem__('best_bid_usd')
            best_bid_try = data.__getitem__('best_bid_try')
            avg_ask_usd = data.__getitem__('avg_ask_usd')
            avg_ask_try = data.__getitem__('avg_ask_try')
            best_ask_usd = data.__getitem__('best_ask_usd')
            best_ask_try = data.__getitem__('best_ask_try')
            instance = OpportunityInfo(creator = op_info_creator, buy_market = buy_market, sell_market = sell_market,
                                    currency = currency, second_currency = second_currency, percent = percent,
                                    ask_reliable = ask_reliable, bid_reliable = bid_reliable,
                                    parent = None, avg_ask_usd = avg_ask_usd, avg_ask_try = avg_ask_try,
                                    best_ask_usd = best_ask_usd, best_ask_try = best_ask_try, avg_bid_usd = avg_bid_usd,
                                    avg_bid_try = avg_bid_try, best_bid_usd = best_bid_usd, best_bid_try = best_bid_try,
                                    buyable_amount = buy_amount, spent_money = spent_money, return_money = return_money,
                                    total_fee=total_fee, buy_fee=buy_fee, sell_fee=sell_fee, tx_fee=tx_fee, table_candidate=table_candidate,
                                    avaiable_invest_options=avaiable_invest_options
                                    )
            instance.set_cross_currency(cross_currency)
            return instance
        except Exception as e:
            error("Error occurend creating op instance from json: Err: {:s}".format(str(e)))
            





class ArbitrageResultInfoMsg(Message):
    def __init__(self, setting:OpportunityInfo):
        self.__relevent_setting = setting

    def _to_string(self):
        key = self.__relevent_setting.get_key()

        result = {'buy_market':self.__relevent_setting.get_buy_market(),
                  'sell_market':self.__relevent_setting.get_sell_market(),
                  'currency':self.__relevent_setting.get_currency(),
                  'second_currency':self.__relevent_setting.get_second_currency(),
                  'cross_currency':self.__relevent_setting.get_cross_currency(),
                  'percent':self.__relevent_setting.get_percent(),
                  'buy_amount':self.__relevent_setting.get_buy_amount(),
                  'spent_money':self.__relevent_setting.get_spent_money(),
                  'return_money':self.__relevent_setting.get_return_money(),
                  'ask_reliable':self.__relevent_setting.get_ask_reliable(),
                  'bid_reliable':self.__relevent_setting.get_bid_reliable(),
                  'avg_ask_usd':self.__relevent_setting.get_avg_ask_usd(),
                  'avg_ask_try':self.__relevent_setting.get_avg_ask_try(),
                  'best_ask_usd':self.__relevent_setting.get_best_ask_usd(),
                  'best_ask_try':self.__relevent_setting.get_best_ask_try(),
                  'avg_bid_usd': self.__relevent_setting.get_avg_bid_usd(),
                  'avg_bid_try': self.__relevent_setting.get_avg_bid_try(),
                  'best_bid_usd': self.__relevent_setting.get_best_bid_usd(),
                  'best_bid_try': self.__relevent_setting.get_best_bid_try(),
                  'tstmp' : self.__relevent_setting.get_tstmp(),
                  'op_info_creator' : self.__relevent_setting.get_creator(),
                  'op_info_type' : self.__relevent_setting.get_type(),
                  'update_time' : self.__relevent_setting.get_update_date(),
                  'total_fee' : self.__relevent_setting.get_total_fee(),
                  'buy_fee' : self.__relevent_setting.get_buy_fee(),
                  'sell_fee' : self.__relevent_setting.get_sell_fee(),
                  'tx_fee' : self.__relevent_setting.get_tx_fee(),
                  'table_candidate' : self.__relevent_setting.get_table_candidate(),
                  'invest_options' : self.__relevent_setting.get_avaiable_invest_options()
                  }
        return {key:result}
