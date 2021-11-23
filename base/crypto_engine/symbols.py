import os

WORKING_FOLDER = os.path.abspath("").split(sep='src')[0]
if WORKING_FOLDER.endswith("/") is not True:
    WORKING_FOLDER = WORKING_FOLDER + "/"

SRC_FOLDER = WORKING_FOLDER + "src/"
DATA_DIR = SRC_FOLDER + "datas/"
FCM_KEY_PATH = DATA_DIR + "fcm_key.json"
LOG_DIR = DATA_DIR + "logs/"
ARBITRAGE_LOG_FILE = LOG_DIR + "arbitrage.log"
TABLE_DIR = DATA_DIR + "tables/"
OPPORTUNITY_DIR = DATA_DIR + "opportunities/"
STATISTICS_DIR = DATA_DIR + "statistics/"
DAILY_STATISTIC_DIR = STATISTICS_DIR + "daily/"
MONTHLY_STATISTIC_DIR = STATISTICS_DIR + "monthly/"
WEEKLY_STATISTIC_DIR = STATISTICS_DIR + "weekly/"
ONLINE_USER_COUNT_FILE = STATISTICS_DIR + "online.txt"
BEST_OPS_DIR = OPPORTUNITY_DIR + "bests/"
NEW_TABLE_DIR = DATA_DIR + "tables/live/"
OLD_TABLE_DIR = DATA_DIR + "tables/old/"
STATISTIC_TABLE_WORKING_TMP_DIR = TABLE_DIR + "tmp/"
NOTIFICATION_TIME_SECOND_THRESHOLD = 300 # 5 mins
STATISTIC_TABLE_FILE_EXPIRED_THRESHOLD = 31 #how many days a table statistic table want to be store. Older than this will be deleted
MAIN_REQUEST_FOLDER = DATA_DIR +"requests/" #

ORDER_BOOK_DIR = DATA_DIR + 'order_books/'
CONFIG_DIR = DATA_DIR + "configs/"
VERSION_FILE = DATA_DIR + "configs/version.txt"
ARBITRAGE_CONFIG_DIR = CONFIG_DIR + "arbitrage_configs/"
MARKET_AND_EXCHANGE_CONFIG_DIR = CONFIG_DIR + "market_exchanges_configs/"

SERVICE_DIR = SRC_FOLDER + "services/"
TABLE_SERVICE_DIR = SERVICE_DIR + "table_service/"
TABLE_REQUEST_DIR = TABLE_SERVICE_DIR + "requests/"
STATISTICS_TABLE_SERVICE_DIR = SERVICE_DIR + "statistics_table_service/"
STATISTIC_TABLE_REQUEST_DIR = STATISTICS_TABLE_SERVICE_DIR + "requests/"
STATISTIC_SERVICE_DIR = SERVICE_DIR + "statistic_service/"
STATISTIC_REQUEST_DIR = STATISTIC_SERVICE_DIR + "requests/"
SIMULATOR_SERVICE_DIR = SERVICE_DIR + "simulator_service/"
SIMULATOR_REQUEST_DIR = SIMULATOR_SERVICE_DIR + "requests/"
SIMULATOR_LOG_DIR = SIMULATOR_SERVICE_DIR + "logs/"
SIMULATOR_SERVICE_NAME = "simulator"
HTTP_SERVICE_DIR = SERVICE_DIR + "http_service/"
HTTP_SERVICE_REQUEST_DIR = HTTP_SERVICE_DIR + "requests/"
HTTP_SERVICE_SHUTDOWN_REQUEST = HTTP_SERVICE_REQUEST_DIR + "shutdown"
ORDER_BOOK_SERVICE_DIR = SERVICE_DIR + "order_book_fetchers/"
REQUEST_HANDLER_SERVICE_DIR = SERVICE_DIR + "request_handlers/"
REQUEST_HANDLER_TYPE_NAME = "_request_handlers"
HANDLER_HEALTHY_FILE_NAME = "is_healthy.info"

KOINEKS_ORDER_BOOK_FILE = ORDER_BOOK_DIR + "/koineks.json"
KOINEKS_BALANCE_FILE = ORDER_BOOK_DIR + "/koineks_balance.json"

WEIRD_BUG_PATH = LOG_DIR + "weird_bug.log"
OP_FINDER_SERVICE_WATCH_DOG_LOG = LOG_DIR + "op_finder_service_watchdog.log" #todo give better names


TRY_USD_RATE = 0 # will be changed every time by convert_try_to_usd(helper.py) method when new rate gathered .
LAST_USD_RATE_UPDATE_SECS = None
USD_RATE_UPDATE_INTERVAL_SECS = 10368 # due to restriction free api we have only 250 request in one month
USD_RATE_UPDATE_ERROR_PRONE_LIMIT_SECS = 600 # After 10 mins values can't be truested..
MAX_TABLE_POINT_COUNT = 25 # maximum point count than a line can have in svg table
WEIRD_PERCENT_THRESHOLD = 50
BTC_USD = 'BTC/USD'
BTC_TRY = 'BTC/TRY'
BTC_LTC = 'BTC/LTC'
BTC_ETH = 'BTC/ETH'
BTC_USDT = 'BTC/USDT'
ETH_USDT = 'ETH/USDT'
ETH_TRY = 'ETH/TRY'
BTC = 'BTC'
TRY = 'TRY'
USD = 'USD'
USDT = 'USDT'
DASH = 'DASH'
XRP = "XRP"
XLM = 'XLM'
ETH = "ETH"
LTC = "LTC"
BCH = "BCH"
BTG = "BTG"

LOG_TO_FILE_ENABLED = True
DEBUG_LEVEL_FILE = "" # set on runtime
DEBUG_LEVEL="ERROR" #Default error level when no error level can not find..
LAST_DEBUG_LEVEL_SET_TIME=0

MIN_ORDERBOOK_LEN = 5 # we accept market is not avaiable if the count of order in the market is under this count
FETCH_ORDERBOOK_ONLINE = False # İf this is false , then market will try the fetch order book from directly from markets instead of our order book database

'''
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
'''
DEFAULT_DEBUG_LEVEL = DEBUG_LEVEL


ETH_FEE = 0.005
DASH_FEE = 0.005
LTC_FEE = 0.001
XRP_FEE = 0.02
USDT_FEE = 5
UPDATE_SERVER_ENABLED = True
DEFAULT_TITLE = "ArbitOzan"
ARBITRAGE_TABLE_MIN_PERCENT = -2 # highter than this percent's wont be reported to table.
INTELLIGENT_FIRST_N = 10 # shows how many first orders will be considred to calculate avarage price
INTELLIGENT_AVARAGE_MONEY_TRY = 10000

Milisecond = 0.01 # in second
Sec = 100 * Milisecond
Min = 60 * Sec
Hour = 60 * Min
Day = 24 * Hour
Week = 7 * Day
Month = 4 * Week
Year = 12 * Month

SMS_FLOOD_TIME = 120
KOINEKS_MARKETS = ["BTC","ETH","LTC","XRP","XLM","DASH","BCH","BTG","DOGE","USDT"]
#KOINEKS_MARKETS = ["BTC"]
IMPORTANT_KOINEKS_MARKET = ["XRP","XLM","ETH","BTC","USDT"]
UNIMPORTANT_KOINEKS_MARKET = ["BTC","LTC","DASH","BCH","BTG","DOGE"]

API_PRIVATE_KEY = "osman_is_my_girl"
GET_SMS_FROM_SERVER_ENABLED = True # if it's enabled , fetch sms codes from server..

LOCAL_ORDERBOOK_SUPPORT = True # if koineks.py runs on local place where koineks service try fetch ob from file system.
USDT_TIME = 45 * Min

BTC_TIME = 30 * Min
ETH_TIME =  4 * Min
DASH_TIME  = 60 * Min
LTC_TIME = 10 * Min
XRP_TIME = 5 * Min
XLM_TIME = 4 * Min
BTG_TIME = 20 * Min
BCH_TIME = 10 * Min


#MIM = MIN INVEST MONEY
BTC_MIM = 10000
ETH_MIM =  1000
DASH_MIM =  5000
LTC_MIM = 1000
XRP_MIM = 250
XLM_MIM = 250
BTG_MIM=1000
BCH_MIM = 5000

mim_list = {
    BCH:BCH_MIM,
    ETH:ETH_MIM,
    DASH:DASH_MIM,
    LTC:LTC_MIM,
    XRP:XRP_MIM,
    XLM:XLM_MIM,
    BTC:BTC_MIM,
    BTG:BTG_MIM
}

transfer_time_list ={ # in seconds
     ETH:ETH_TIME,
     DASH:DASH_TIME,
     LTC:LTC_TIME,
     XRP:XRP_TIME,
     XLM:XLM_TIME,
     USDT:USDT_TIME,
     BTC:BTC_TIME,
     BTG:BTG_TIME,
     BCH:BCH_TIME
}

fee_list = {ETH:ETH_FEE,
            DASH:DASH_FEE,
            LTC:LTC_FEE,
            XRP:XRP_FEE,
            USDT:USDT_FEE}




