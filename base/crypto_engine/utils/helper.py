import math
import time
import os
import smtplib
from pathlib import Path
import json
import xml.etree.ElementTree as ET
from time import sleep
from datetime import datetime, date
from ast import literal_eval

from base.crypto_engine.MessageApi import debug
from base.crypto_engine import symbols
from modified_ccxt import Exchange
import threading


turkish_markets = ["koineks", "koinim", "btcturk"]

# Api Call Helper Methods Starts#
remote_server_address = "http://ozenoglu.com:8000/api_call"


def create_event_data(event: str, data=None):
    return {'private_key': 'osman_is_my_girl', 'event': event, 'data': data}


def send_event_custom_check(event_data: dict):
    r = requests.post(remote_server_address, data=json.dumps(event_data))
    data = r.content.decode("utf-8")
    return data


def send_event(event_data: dict, expected_data="success"):
    try:
        r = requests.post(remote_server_address, data=json.dumps(event_data))
    except Exception as e:
        raise Exception("Server Communication Problem! {:s}".format(str(e)))
    data = r.content.decode("utf-8")
    if (data != expected_data):
        event = event_data.pop('event', "None")
        raise Exception("{:s} failed return content {:s} expected_data: {:s}".format(
            str(event), str(data), str(expected_data)))


def is_server_alive():  # if server is not reachable , an exception will be occured.
    try:
        if remote_server_address.__contains__("api_call"):
            base_address = remote_server_address.split("api_call")[0]
            # if any response returns , it means server is reachable and responses our requests..
            requests.get(base_address)
        return True
    except Exception as e:
        return False

# Api Call Helper Methods Ends#


# get_sms_of can be koineks_login_code , koineks_withdraw_code , btcturk_login_code , btcturk_withdraw_code bla bla
def get_sms_code_from_server(get_sms_code_data):
    code = None
    try_count = 0
    fresh_sms = False
    fresh_sms_try_cout = 0
    while code == None:
        try:
            try_count = try_count + 1

            if (try_count > 3):
                debug.error(
                    "Error , we can't fetched sms code from server , try mail service. good luck!")
                return None
            while fresh_sms == False:
                private_key = symbols.API_PRIVATE_KEY
                data = {'event': 'get_sms_code',
                    'data': get_sms_code_data, 'private_key': private_key}
                r = requests.get(
                    "http://ozenoglu.com:8000/api_call", data=json.dumps(data))
                response = r.content.decode("utf-8").replace("\"", "")
                fresh_sms = is_sms_code_fresh(response)
                if (fresh_sms == False):
                    fresh_sms_try_cout += 1
                    if (fresh_sms_try_cout > 20):
                        debug.error("Server return old sms!")
                        return None
                        debug.error("Fetched{:d} old sms code , we will try again".format(
                            int(fresh_sms_try_cout)))
                    time.sleep(1)
                    continue
                code = response.split("kodunuz:")[1].split(" ")[0]
                return code
                debug.error("Error during fetching sms code from server at try {:d} error {:s}".format(int(try_count),
                                                                                                 str(e)))
        except Exception as e:
            debug.error(
                "Error in get_sms_code_from_server {:s}".format(str(e)))
            return None


def is_sms_code_fresh(response: str):
    try:
        update_time = response.split("update_time:")[1]
        update_time = float(update_time) / 1000
        now = time.time()
        # if older than 1 min then it's old sms_code.
        if (now - update_time) > 60:
            debug.error("{:d} sec old sms _code".format(
                int(now - update_time)))
            return False
        else:
            return True
    except Exception as e:
        raise Exception(
            "Error parsing update_time from server(sms_code) {:s}".format(str(e)))


def is_turkish(name: str):
    return turkish_markets.__contains__(name)


def convert_dict_to_str(mydict: dict):
    return json.dumps(mydict)


def release_folder_lock_if_any(folder_path):
    try:
        if (os.path.isfile(folder_path+"/.lock")):
            os.remove(folder_path+"/.lock")
            return True
    except Exception as e:
        debug.error(
            "Exception occured during release_folder_lock_if_any: {:s}".format(str(e)))
        return False


def release_folder_lock(folder_path):
    try:
        os.remove(folder_path+"/.lock")
        return True
    except Exception as e:
        debug.error(
            "Exception occured during releasing lock: {:s}".format(str(e)))
        return False


# maximum try time out default 1 sec , timeout for locked file
def try_lock_folder(folder_path: str, max_try_ms: int = 100, lock_file_time_out_sec: int = 2):
    locked = False
    try_count = 0
    ts = time.time()
    while locked != True:
        te = time.time()
        spent_ms = (te-ts) * 1000
        if (spent_ms < max_try_ms):  
            if (os.path.exists(folder_path + "/.lock")): #Try lock here peacufully
                locked = False
                time.sleep(0.1)
                continue
            else:
                locked = initialize_lock_file(folder_path)
        else: #We couldn't lock it is our last change if this lock file is too old , we can remove it. Probably someone forget it to remove ?

            if (os.path.exists(folder_path + "/.lock")):
                try:
                    with open(folder_path + "/.lock", "r") as lock_file:
                        locked_tmsp = float(lock_file.readline())
                        now = time.time()
                        if now - locked_tmsp > lock_file_time_out_sec:
                            release_folder_lock(folder_path)
                            debug.error("OLD LOCK FILE: lock file is too old , we take control here!")
                            locked = initialize_lock_file(folder_path)
                except Exception as e:
                    locked = False
                    debug.error("Fatal Error: it's looks like there is .lock file in {:s} but we have problem? E:{:s}".format(str(folder_path),str(e)))
            else:
                locked = initialize_lock_file(folder_path)
                break
    return locked

def initialize_lock_file(path:str):
    try:
        with open(path+ "/.lock", "w") as lock_file:
            locked_tmsp = time.time()
            lock_file.write("{:f}".format(float(locked_tmsp)))
            return True
    except Exception as e:
        debug.error("Exception occured during locking file: {:s}".format(str(e)))
        return False

def update_usd_rate():
    last_update = symbols.LAST_USD_RATE_UPDATE_SECS
    now = time.time()
    must_be_updated = False
    if(last_update != None and last_update + symbols.USD_RATE_UPDATE_INTERVAL_SECS > now and symbols.TRY_USD_RATE >= 0):
        return

    if (last_update == None or last_update + symbols.USD_RATE_UPDATE_ERROR_PRONE_LIMIT_SECS > now): #we are in error prone section , which means our date is too old , have to updated!!
        must_be_updated = True
    try:
        response = requests.get("https://free.currconv.com/api/v7/convert?q=USD_TRY&compact=ultra&apiKey=63f6b3330051e25e8b64")
        res = response.content
        strs = res.decode("UTF-8")
        rate = float(json.loads(strs).__getitem__('USD_TRY'))
        symbols.TRY_USD_RATE = rate
        symbols.LAST_USD_RATE_UPDATE_SECS = now
    except:
        try:
            try:
                response = requests.get('http://www.tcmb.gov.tr/kurlar/today.xml')
                root = ET.fromstring(response.content)

                for forex in root.iter('Currency'):
                    if (forex.getchildren()[2].text == 'US DOLLAR'):
                        try_rate = float(forex.getchildren()[4].text)
                        print("Rate from Merkez Bank {:f}".format(float(try_rate)))
                        symbols.TRY_USD_RATE = try_rate
                        symbols.LAST_USD_RATE_UPDATE_SECS = now
                        break

            except Exception as e:
                debug.error("Error{:s} during updating usd_try rate Last Rate is {:f}".format(str(e),float(symbols.TRY_USD_RATE)))

                if(must_be_updated):
                    raise Exception("Dolar Rate couldn't be updated!")

        except Exception as e:
            debug.error("wtf {:s}".format(str(e)))


def create_path_if_not_exists(path):
    try:
        if not os.path.exists(path):
            parent_folder = str(Path(path).parent)
            create_path_if_not_exists(parent_folder)
            debug.error("[paths] {:s} doesn't exist: creating...".format(path))
            os.mkdir(path)
        return path
    except Exception as e:
        debug.error("Error during checking path {:s} Error:{:s}".format(str(path),str(e)) )
        

def find_current_week_number():
    today = str(date.today())
    week =  math.ceil((int(today.split("-")[2]) / 7))
    return week

def convert_try_to_usd(amount:float):

    try:
        update_usd_rate()
        result = amount/symbols.TRY_USD_RATE
        return result
    except Exception as e:
        raise Exception("Couldn't convert try to usd due to {:s}".format(str(e)))

def check_ops_names_valid( valid_name: str, names_dict):
    try:
        ret = True
        names = iter(names_dict)
        name = next(names)
        if name is not "best" and str(name).startswith(valid_name) is not True:
            error("Name {:s} is not Valid".format(str(name)))
            ret = False
        return ret
    except Exception as e:
        error("Error during validating names E:{:s}".format(str(e)))
        return False

def convert_usd_to_try(amount:float):
    try:
        update_usd_rate()
        result = amount * symbols.TRY_USD_RATE
        return result
    except Exception as e:
        raise Exception("Couldn't convert try to usd due to {:s}".format(str(e)))



def set_current_thread_name(name:str):
    try:
        current_t = threading.currentThread()
        threading.Thread.setName(current_t,name)
    except Exception as e:
        print("error during setting thread name : {:s}".format(str(e)))

'''Usage of find_*** functions:
bittrex = bittrex({'apiKey': 'xxx','secret': 'xxx'})

result = bittrex.fetch_balance()
print(find_symbol_address(result,'SYS'))
print(find_pending_balance(result,'BTCD'))

 '''
def find_symbol_address(fetch_balance_result,symbol:str):
    for info in fetch_balance_result.__getitem__('info'):
        if info.__getitem__('Currency') == symbol:
            return info.__getitem__('CryptoAddress')

def find_free_balance(fetch_balance_result):
    try:
        if (type(fetch_balance_result) == type(())):  # tuple
            dic_result = fetch_balance_result[0]
        elif type(fetch_balance_result) == type({}):  # dict
            dic_result = fetch_balance_result
        else:
            assert  Exception("Unknowon type ")

        free_balance = dic_result.__getitem__('free')

    except Exception as e:
        debug.error("Unknown result type for fetching balance is {:s}".str(format(type(fetch_balance_result))))
        debug.dump_trace()
        free_balance = 0
    finally:
        return free_balance

def get_avarage_price(orders:tuple,sampling_count:int=10):
    i = 0
    total = 0
    total_order_count = 0
    while (total_order_count < sampling_count):
        order = orders[i]
        order_price = order[0]
        order_count = order[1]
        total +=  order_price * order_count
        total_order_count += order_count
        i = i+1
    return total / total_order_count

def get_avarage_price_for_money(orders:tuple,total_money:int=5000): #5000TRY
    i = 0
    spent_money = 0
    bought_coins = 0
    left_money = total_money
    while (left_money > 0 ):
        if (i >= len(orders)):
            raise Exception("There is not enough orders to calculate for given money {:f}".format(float(total_money)))

        order = orders[i]
        i += 1
        order_price = order[0]
        order_count = order[1]
        current_order_price = order_price * order_count
        if (spent_money  + current_order_price < total_money): # Consume all Order
            spent_money += current_order_price
            bought_coins += order_count
        # Last Buy (Partial Buy of a order)
        else:
            left_money = total_money - spent_money
            affordable_coins_count = float(left_money / order_price)
            bought_coins += affordable_coins_count
            spent_money = total_money

            left_money = 0
    return spent_money / bought_coins





def avarage_price_for_first_ncrypto(orders:tuple,ncrypto:int):
    i = 0
    total = 0
    total_order_count = 0


    while (total_order_count < ncrypto):
        try:
            order = orders[i]
            order_price = order[0]
            order_count = order[1]
            if ( order_count + total_order_count > ncrypto):
                order_count = ncrypto - total_order_count

            total +=  order_price * order_count
            total_order_count += order_count
            i += 1
        except Exception as e:
            debug("Error during avarage_price_for_First_ncrypto :{:s}".format(str(e)))
            raise e
    return total / total_order_count


def avarage_price_for_first_n(orders:tuple,n:int=1):
    i = 0
    total = 0
    order_price = 0
    order_count = 0
    total_order_count = 0
    order = None
    try:

        if (len(orders) == 0):
            debug.error("There is not any order , price  will be return as 0")
            return 0
        if (len(orders) < n ):
            debug.error("There is not enough order in the order list all order will be calculated though")
            n = len(orders)
    except Exception as e:
        debug.error("Given orders is problematic")
        return 0

    while (i < n):
        try:
            order = orders[i]
            order_price = order[0]
            order_count = order[1]
            total +=  order_price * order_count
            total_order_count += order_count
            i += 1
        except Exception as e:
            debug.error("There is no ")
    return total / total_order_count

def find_first_ten_order_avarage(orders:tuple):
    i = 0
    total = 0
    n = 10
    order_price = 0
    order_count = 0
    total_order_count = 0
    order = None

    if (len(orders) == 0):
        debug.error("There is not any order , price  will be return as 0")
        return 0
    if (len(order) < n ):
        debug.error("There is not enough order in the order list first {:d} order will be considered".format(len(order)))
        n = len(orders)

    while (i < n):
        order = orders[i]
        order_price = order[0]
        order_count = order[1]
        total +=  order_price * order_count
        total_order_count += order_count
        i += 1

    return total / total_order_count

def get_best_price(orders:tuple):

        order = orders[0]
        order_price = order[0]
        return order_price

def is_host_alive(host_address:str):
    return True #TODO: implement if given host such as google.com is alive or not.


def upload_svg(svg_path:str):
    uploader_thread = threading.Thread(target = __upload_svg,args=[svg_path],name="Svg-Uploader")
    uploader_thread.start()
def upload_order_book(order_book_path:str):
    uploader_thread = threading.Thread(target = __upload_order_book,args=[order_book_path],name="Order-Book-Uploader")
    uploader_thread.start()
def upload_opportunity_result(op_result_path:str):
    uploader_thread = threading.Thread(target = __upload_opportunity_result,args=[op_result_path],name="OpInfo-Uploader")
    uploader_thread.start()
def upload_opportunity_list_result(op_results:list):
    uploader_thread = threading.Thread(target = __upload_opportunity_list_result,args=tuple(op_results) ,name="OpInfo-Uploader")
    uploader_thread.start()


def __upload_svg(svg_path: str):
    if symbols.UPDATE_SERVER_ENABLED == False:
        debug.debug("Update Server Enabled False , don't upload anything.")
        return
    try_count = 0
    while True:
        try_count += 1
        try:
            files = {'file': open(svg_path, 'rb')}
            r = requests.post("http://ozenoglu.com:8000/upload_svg/", files=files)
            debug.debug("svg file uploaded")
            return r
        except Exception as e:
            if try_count > 5:
                debug.error("Error during  uploading svg! {:s}".format(str(e)))
                return False
            else:
                time.sleep(1)

def __upload_order_book(order_book_path: str):
    if symbols.UPDATE_SERVER_ENABLED == False:
        debug.debug("Update Server Enabled False , don't upload anything.")
        return
    try_count = 0
    while True:
        try_count += 1
        try:
            files = {'file': open(order_book_path, 'rb')}
            r = requests.post("http://ozenoglu.com:8000/upload_order_books/", files=files)
            # debug.debug("order_book file uploaded")
            return r
        except Exception as e:
            if try_count > 5:
                debug.error("Error during  uploading order_book! {:s}".format(str(e)))
                return False
            else:
                time.sleep(1)

def send_mail(to:str,msg:str):

    try:
        app_info  = Config.get_manager_config()
        mail_settings = app_info.get_mail_settings()
        user_name = mail_settings.__getitem__("username")
        password = mail_settings.__getitem__("password")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(user_name, password)
        msg = msg.replace(":"," ")
        server.sendmail("btcturk.ozan@gmail.com",  to, msg)
    except Exception as e:
        debug.error("Error during sending mail {:s}".format(str(e)))

def __upload_opportunity_list_result(*list):
    if symbols.UPDATE_SERVER_ENABLED == False:
        debug.debug("Update Server Enabled False , don't upload anything.")
        return

    op_results = list
    first_op = op_results[0]
    best_op_name = op_results[-1] #best op name appended to list at the end..

    op_file_name = first_op.get_file_name()
    try_count = 0
    while True:
        try_count += 1
        try:
            ops_in_json = {}
            for op in op_results:
                if type(op) is not str:
                    ops_in_json.update(op.to_json())
            ops_in_json.update({"best": best_op_name})
            nested_data = {'data': ops_in_json}
            data = create_event_data("new_opportunity_info", nested_data)
            send_event(data)
            debug.debug("opportunity_info file uploaded")
            return True
        except Exception as e:
            if try_count > 5:
                debug.error("Error during  uploading op_result! {:s}".format(str(e)))
                return False
            else:
                time.sleep(1)

def __upload_opportunity_result(opportunity_result_path: str):
    if symbols.UPDATE_SERVER_ENABLED == False:
        debug.debug("Update Server Enabled False , don't upload anything.")
        return

    try_count = 0
    while True:
        try_count += 1
        try:
            with open(opportunity_result_path,'r') as new_op_file:
                sample_op_info = json.load(new_op_file)
                op_name = next(iter(sample_op_info.keys()))
                op_data = sample_op_info.get(op_name)
                op_info_type = op_data.get("op_info_type")
                nested_data = {'data':sample_op_info}
                data = create_event_data("new_opportunity_info",nested_data)
                send_event(data)
                debug.debug("opportunity_info file uploaded")
                os.remove(opportunity_result_path)
                return True
        except Exception as e:
            if try_count > 5:
                debug.error("Error during  uploading op_result! {:s}".format(str(e)))
                return False
            else:
                time.sleep(1)

def find_symbol_fbalance(fetch_balance_result, symbol:str):
    try:
        if (type(fetch_balance_result) == type(())):  # tuple
            dic_result = fetch_balance_result[0]
            free_balance = dic_result.__getitem__('free')
            balance = free_balance.__getitem__(symbol)

            return balance
    except Exception as e:
        debug.error("Exception at find_symol _fblance ->:{:s}".format(str(e)))
        return 0
    try:

        if type(fetch_balance_result) == type({}):  # dict
            dic_result = fetch_balance_result
            free_balance = dic_result.__getitem__('free')
            balance = free_balance.__getitem__(symbol)

            return balance
        else:
            debug.error("Unknown result type for fetching balance is {:s}".str(format(type(fetch_balance_result))))
    except Exception as e:
        debug.error("Exception at find_symol _fblance ->:{:s}".format(str(e)))
        return 0



def find_available_balance(fetch_balance_result,symbol:str):
    for info in fetch_balance_result.__getitem__('info'):
        if info.__getitem__('Currency') == symbol:
            return info.__getitem__('Available')

def find_pending_balance(fetch_balance_result,symbol:str):
    for info in fetch_balance_result.__getitem__('info'):
        if info.__getitem__('Currency') == symbol:
            return info.__getitem__('Pending')

def is_limit_buy_order_succeed(limit_buy_order_result):
    return limit_buy_order_result.__getitem__('info').__getitem__('success')


# sample_result = {'id': '5ab4dc52-113a-4dcb-b2f7-6499cc0de524', 'info': {'success': True, 'result': {'uuid': '5ab4dc52-113a-4dcb-b2f7-6499cc0de524'}, 'message': ''}}
def is_limit_sell_executed(result):
    return result.__getitem__('info').__getitem__('success')

'''

print(get_ask_price('ETH/BTC',bittrex))
print(get_bid_price('ETH/BTC',bittrex))
print(result)
'''
def get_ask_price(symbol:str,market_Ex:Exchange):
    result = fetch_price = market_Ex.fetch_ticker(symbol)
    return result.__getitem__('info').__getitem__('Ask')

def get_bid_price(symbol:str,market_Ex:Exchange):
    result = fetch_price = market_Ex.fetch_ticker(symbol)
    return result.__getitem__('info').__getitem__('Bid')

'''
returns 1/1000 lower than actual price 
'''
def get_tenthousandth_lower_price(price:float):
    return price-(price*0.0001)

def get_thousandth_lower_price(price:float):
    return price-(price*0.001)
'''
returns 1/1000 higher than actual price 
'''
def get_thousandth_higher_price(price:float):
    return price+(price*0.001)

def get_twothousandth_higher_price(price:float):
    return price+(price*0.002)

def get_two_hundert_lower_price(price:float):
    return price-(price*0.02)
def get_five_hundert_lower_price(price:float):
    return price-(price*0.05)

class Message:
    def __init__(self,low_market_data:str,high_market_data:str,gap:float,percent:float):
        self.__low_market_data = low_market_data
        self.__high_market_data = high_market_data
        self.__gap = gap
        self.__percent = percent

    def to_string(self):
        result = {'low_market_data':self.__low_market_data,
                  'high_market_data': self.__high_market_data,
                  'gap' : self.__gap,
                  'percent': self.__percent}
        return result



import requests

xmldata = '''<?xml version="1.0"?>
<doc>
    <branch name="testing" hash="1cdf045c">
        text,source
    </branch>
    <branch name="release01" hash="f200013e">
        <sub-branch name="subrelease01">
            xml,sgml
        </sub-branch>
    </branch>
    <branch name="invalid">
    </branch>
</doc>
'''


url = 'http://www.tcmb.gov.tr/kurlar/today.xml'


