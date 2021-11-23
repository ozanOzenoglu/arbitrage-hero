import time
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from base.crypto_engine.symbols import *
from api.base.crypto_engine.utils.market import Market
from base.crypto_engine.MessageApi.debug import *



class Simulator():



    def __init__(self,op_info:OpportunityInfo):

        self.__op_info = op_info

    def update_arbitrage_table(self,op_info:OpportunityInfo):
        op_info.push() # push to table service

    def start_simulation(self,transfer_time:float): #after given wait time , we will simulate like we're selling on selling exchange market.
        try:
            op_info = self.__op_info
            currency = op_info.get_currency()
            second_currency = op_info.get_second_currency()
            cross_currency = op_info.get_cross_currency()
            if (cross_currency != second_currency and cross_currency != ""):
                second_currency = cross_currency
            sell_market_name = op_info.get_sell_market()
            selling_market = Market.create_market(sell_market_name)
            bid_taker_fee = selling_market.get_market().fees.__getitem__('trading').__getitem__('taker') * 100
            spent_money = op_info.get_spent_money()
            time.sleep(transfer_time)
        except Exception as e:
            error("Couldn't start simulation due to : {:s} ".format(str(e)))
            return

        simulation_finished = False
        while simulation_finished == False:
            try:
                result_bid = selling_market.get_avarage_bid(currency + "/" + second_currency, spent_money) # get selling market information
                if (result_bid == -1):
                    raise Exception("Couldn't get results from selling market")
                is_bid_reliable = result_bid.__getitem__('reliable')
                avg_bid_usd = result_bid.__getitem__('avg_usd')
                best_bid_usd = result_bid.__getitem__('best_usd')
                avg_bid_try = result_bid.__getitem__('avg_try')
                best_bid_try = result_bid.__getitem__('best_try')
                coin_to_sell = op_info.get_buy_amount()
                return_money = coin_to_sell * avg_bid_usd
                return_money = return_money - (return_money * (bid_taker_fee / 100))
                gap = return_money - spent_money
                percent = (gap / spent_money) * 100
                total_buy = op_info.get_buy_amount() #bought coins when op_info created

                op_info.set_op_info_creator("simulator")
                op_info.set_avg_bid_usd(avg_bid_usd) # use new values here
                op_info.set_avg_bid_try(avg_bid_try)
                op_info.set_best_bid_usd(best_bid_usd)
                op_info.set_best_bid_try(best_bid_try)
                op_info.set_bid_reliable(is_bid_reliable)
                op_info.set_spent_money(spent_money)  # the money we're spending for arbitrage
                op_info.set_buy_amount(total_buy)  # the coin's amount that we're buying
                op_info.set_return_money(return_money)  # the expected  return money on sell market when we sell our coins
                op_info.set_percent(percent)

                simple_msg = op_info.to_simple_msg()
                user_feedback("SIMULATOR: {:s}".format(str(simple_msg)))
                op_info.upload_result()
                self.update_arbitrage_table(op_info)
                simulation_finished = True

            except Exception as e:
                error("Error during simulation {:s}".format(str(e)))
                simulation_finished = False
                time.sleep(2)
            debug("Simulation finished in peace..")



