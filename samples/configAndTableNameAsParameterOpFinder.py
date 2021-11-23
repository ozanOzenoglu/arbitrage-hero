#Author Ozan Ozenoglu ozan.ozenoglu@gmail.com
#File Created at 08.11.2017


'''
Scope of Module:
This module is command line interface module which take commands from command line and parse them and execute them
'''

from threading import Thread
from time import sleep
from sys import argv
import os,sys


try:
    import base
except Exception as e:
    sys.path.append('..')
    print("Parent directory is added to sys path")
    
from base.crypto_engine.utils.config_manager import Config
from base.crypto_engine.utils.opportunity_finder import OpportunityFinder
from base.crypto_engine.setting_db.exchange_info import ExchangeInfo
from base.crypto_engine.setting_db.application_info import Mode
from base.crypto_engine.symbols import *
import base.crypto_engine.MessageApi.debug as debug

if (len(argv) < 3):
    print("Table Title and config Path should be given in given order [configAndTableNameAsParameterOpFinder.py TableTitle ConfigPath");
    exit(-1)
else:
    table_title = argv[1]
    config_name = argv[2]

if (len(argv) > 3):
    debug_level = str.upper((argv[3]))
else:
    debug_level = DEFAULT_DEBUG_LEVEL # constant value in symbols.py

try:
    debug.CURRENT_DEBUG_LEVEL = debug.DEBUG_LEVELS[debug.DEBUG_LEVELS.index(debug_level)]
except Exception as e:
    debug.error("Wrong debug level given error is {:s}".format(str(e)))
    exit(-1)


current_path  = os.path.dirname(os.path.realpath(__file__))
config_path = current_path + "/" + config_name
Config.set_config_folder(config_path)


markets =  Config.get_markets_from_config()
arbitrages = Config.get_arbitrages_from_config()
exchanges = Config.get_exchange_from_config()



arbitrage_keys = arbitrages.keys()
for arbitrage_name in arbitrage_keys:
    arbitrage = arbitrages.__getitem__(arbitrage_name)
    if arbitrage.get_active() == False:
        continue # skip if the arbitrage is not activated
    low_market = arbitrage.get_market_low()
    high_market = arbitrage.get_market_high()
    desired_percent = arbitrage.get_percent()

    is_notify_active = arbitrage.get_notify()
    symbol = arbitrage.get_symbol()
    symbol = str.lower(symbol)
    delay = arbitrage.get_delay()
    try:
        low_market_exchange = exchanges.__getitem__(low_market.get_name() + '/' + symbol)
    except Exception as e:
        low_market_exchange = ExchangeInfo.create_dummy_usd_exchange(low_market.get_name(),symbol)
    try:
        high_market_exchange = exchanges.__getitem__(high_market.get_name() + '/' + symbol)
    except Exception as e:
        high_market_exchange = ExchangeInfo.create_dummy_usd_exchange(high_market.get_name(),symbol)

    op_finder = OpportunityFinder(delay,Mode.AGGRESSIVE,table_title,ARBITRAGE_TABLE_MIN_PERCENT)

    op_finder.add_markets_to_watch(high_market_exchange,low_market_exchange,desired_percent,is_notify_active,arbitrage.get_only_notify())
    op_finder_start_thread = Thread(target=op_finder.start)

    op_finder_start_thread.start()
    sleep(2)