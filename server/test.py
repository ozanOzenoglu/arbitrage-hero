
'''
This file is for testing server.py functions .
Created By Ozan Özneoğlu 05.11.2018
'''

import requests
import json
import time
from api.base.crypto_engine.MessageApi.debug import *

global working_address
local_server_address = "http://localhost:8000/api_call"
remote_server_address = "http://ozenoglu.com:8000/api_call"


def test_method(method):
    def test_it(*args, **kw):
        try:
            ts = time.time() * 1000
            method(*args, **kw)
            te = time.time() * 1000
            print("{:s} finished in {:d} ms".format(str(method.__name__), int(te - ts)))
        except Exception as e:
            print("{:s} FAIL Error: {:s}".format(method.__name__,str(e)))
            raise e

    return test_it

def create_event_data(event:str,data=None):
    return {'private_key': 'osman_is_my_girl', 'event': event, 'data': data}


def send_event_custom_check(event_data: dict):
    r = requests.post(working_address, data=json.dumps(event_data))
    data = r.content.decode("utf-8")
    return data


def send_event(event_data: dict,expected_data="success"):
    try:
        r = requests.post(working_address, data=json.dumps(event_data))
    except Exception as e:
        raise Exception("Server Communication Problem! {:s}".format(str(e)))
    data = r.content.decode("utf-8")
    if (data != expected_data):
        event = event_data.pop('event',"None")
        raise Exception("{:s} failed return content {:s} expected_data: {:s}".format(str(event),str(data),str(expected_data)))


def is_server_alive(): # if server is not reachable , an exception will be occured.
    try:
        if working_address.__contains__("api_call"):
            base_address = working_address.split("api_call")[0]
            requests.get(base_address) # if any response returns , it means server is reachable and responses our requests..
        return True
    except Exception as e:
        return False
'''
@event_name:update_sms_code
@event_data:Sms Message
@event_return:success
@Explanation:In a file it stores the recevied sms_message with time stamp. 
Sample File Content:"KOINEKS.COM giris onay kodunuz:754398 B186 update_time:1541507726716.3286"
'''
@test_method
def test_send_sms_event():
    nested_data = {'sms_name': 'koineks_login_sms', 'data': 'sms code is bla bla bla'}
    send_sms_data = create_event_data('update_sms_code', nested_data)
    send_event(send_sms_data)

'''
@event_name:get_sms_code
@event_data:sms_name:str (could be koineks_login_sms , koineks_withdraw_sms , btcturk_login_sms, btcturk_withdraw_sms , vebit_login_sms ... bla bla.) so you should save data with its name 
and retrive it by checking requested sms name..
@event_return:sms_message with time_stamp
@Explanation:It returns sms_message with time stamp that is created with event update_sms_code
Sample Response:"KOINEKS.COM giris onay kodunuz:754398 B186 update_time:1541507726716.3286"
'''
@test_method
def test_get_sms_event():
    send_sms_data = create_event_data('get_sms_code', "koineks_login_sms")
    result = send_event_custom_check(send_sms_data)
    if (result.__contains__("sms code is bla bla bla") is not True):
        event = send_sms_data.pop('event',"None")
        raise Exception("{:s} failed return content {:s} expected_data: {:s}".format(str(event),str(result),str("sms code is bla bla bla")))


'''
@event_name:new_opportunity_info
@event_data:dictionary(json formatted string) sample: https://ozenoglu.com/opportunities/cex_koineks_XLM_opportunity.json
@event_return:success
@Explanation:It stores given single opportunity_info item into catogerized opportunities(like ../all_ops/bronze_ops.json) info dictionary and saves it in a file.
For example there should be bronze_opportunities.json and in this file there are dictionary items like "koineks_cex_xrp": {....}, "koineks_cex_btc": {....},
you may find a sample file in remote server /var/http/www/opportunities/ folder.(or ozenoglu.com/opportunuties/all_opportunuties.json) all_opportunities.json file,
 stores all infos in a single file in json(dictionary) format. you may get an idea from it.
 
 ### IMPORTANT UPDATE TO THIS EVENT###
 
 From now on this event is also charge of creating tables! . 
 
 Tables how will be created is described below!*
  
 A possible Data Structure for storing table can be like this.
 
 /tables/bronze/cex-btcturk_{date}.svg
 /tables/silver/koineks-btcturk_{date}.svg
 /tables/{type}/cex-btcturk_{date}.svg
 
 *Every table will have related two market. In same table there won't be more than two market. (so btcturk,koineks,cex tables are wrong)
 *Every table will have a type.{bronze,silver,golder...}
 *Every table will have saved under /tables/{type}/ folder.
 *Every table name will end {date}.svg naming notaion.
 *A table can have more than one Arbitrage Line(Every currency means a line, so cex-btcturk(xrp,btc,eth..) can have multiple line inside of it.
 *For good looking a table must have excatly 20 dots(arbitrage rate info) per line.
 *After 20 dot is completed , a new table must be created with new {date}
 *Maximum 2 days old data should be kept , in other words older than two days tables should be removed from the system.
 
 @Description
 So let's assume new_opportunity_info event gets a data says that BTCTURK_CEX_XRP with type Bronze.
 so you should use this data to create a new dot in table /tables/bronze/btcturk_cex_{date}.svg in XRP LINE.
 That's it.
 
'''
@test_method
def test_new_opportunity_info_event(sample_url): # this op info should be saved into bronze_op_infos.json! if bronze is given as op_info type
    # r = requests.get("https://ozenoglu.com/opportunities/cex_koineks_XLM_opportunity.json")
    # sample_op_info = json.loads(r.content.decode("UTF-8"))
    # nested_data = {'type':'bronze','data':sample_op_info}
    # data = create_event_data("new_opportunity_info",nested_data)
    # send_event(data)

    r = requests.get(sample_url)
    sample_op_info = json.loads(r.content.decode("UTF-8"))
    op_name = next(iter(sample_op_info.keys()))
    op_data = sample_op_info.get(op_name)
    op_info_type = op_data.get("op_info_type")
    nested_data = {'data':sample_op_info}
    data = create_event_data("new_opportunity_info",nested_data)
    send_event(data)



    check_event = create_event_data("get_all_opportunity_info",op_info_type)
    result  = send_event_custom_check(check_event)
    list = json.loads(result)
    ops = list.keys()
    for op in ops:
        if op == op_name:
            data = list.get(op)
            sample_op_info_data_tstmp = sample_op_info.get(op_name).get("tstmp")
            data_as_dict = json.loads(data)
            sample_data_tstmp = data_as_dict.get(op_name).get("tstmp")
            if (sample_data_tstmp != sample_op_info_data_tstmp):
                raise Exception("Not same data :/")





'''
@event_name:get_all_opportunity_info
@event_data:type:string
@event_return:opportunity_info_list:json_string(dictionary)
@Explanation:This event should return a list of all oppportunities info in json format(dictionary) that belongs to given type
so just return bronze_ops.json if bronze ops are  asked..
'''
@test_method
def test_get_all_opportunity_info_event():

    #Since we check data integrity in send op info event , we just check here length of returned list..

    data = [
     create_event_data("get_all_opportunity_info","gold")
    ]

    for event in data:
        result = send_event_custom_check(event)
        try :
            list = json.loads(result)
        except Exception as e:
            raise Exception("Error during converting result into dictionary(all_list)")

        try:
            if (list == None or len(list) == 0):
                raise Exception("list is None!")

        except Exception as e:
            print("Unexpected Error in test_get_all_opportunity_info_event test case")
            raise e



@test_method
def test_get_opportunity():
    data = create_event_data("get_opportunity_info",{"buy_market":"cex","sell_market":"btcturk" , "currency":"btc"})
    result = send_event_custom_check(data)

    list = json.loads(result)
    for table_name in list:
        if str(table_name).__contains__("cex_btcturk"):
            return 0 #this line is success line :)
    #we shouldn't came here to pass this event. Because we send cex_koineks new opp info in new_op_info event test.
    raise Exception("Table api failed {:s}".format(str(result)))

'''
@event_name:get_table_list
@event_data:type:string (type points that which type of table are asked for)
@event_return:list of ARBITRAGE TABLE(svg files )names that server has /***/ ORANLARI GOSTEREN TABLOLAR /***/ 
@Explanation:In this event , you must return a list that shows names of tables that is created by new_arbitrage_table event. For example something like this.
but in json format..
stable_2018-11-05_03:46:06.svg
stable_2018-11-05_04:06:06.svg
stable_2018-11-05_04:26:06.svg
stable_2018-11-05_04:46:07.svg
stable_2018-11-05_05:06:07.svg
stable_2018-11-05_05:26:07.svg
stable_2018-11-05_05:46:07.svg
stable_2018-11-05_06:06:07.svg
stable_2018-11-05_06:26:07.svg
stable_2018-11-05_06:46:07.svg
stable_2018-11-05_07:06:07.svg 
'''
@test_method
def test_get_table_list_event():
    data = create_event_data("get_table_list",{"live_requested":True , "creator":"op_finder"})
    print("data is %s" % data)
    result = send_event_custom_check(data)

    list = json.loads(result)
    for table_name in list:
        if str(table_name).__contains__("btcturk_cex"):
            return 0 #this line is success line :)
    #we shouldn't came here to pass this event. Because we send cex_koineks new opp info in new_op_info event test.
    raise Exception("Table api failed {:s}".format(str(result)))

'''
@event_name:get_table
@event_data:table_name:string
@event_return:Table File . like stable_12.21.21.svg 
@Explanation:In this event , you must return a file which extension is .svg.
This file should be created in new_arbitrage_table_event.
'''

@test_method
def test_get_table_event(): #in this test , we are expecting and .svg file that is created by server.py on new_table_info event.

    data = create_event_data("get_table_list",{"live_requested":True , "creator":"op_finder"})
    result = send_event_custom_check(data)
    table_name = ""
    list = json.loads(result)
    for table_name in list:
        if str(table_name).__contains__("btcturk_cex"):
            break
    #we shouldn't came here to pass this event. Because we send cex_koineks new opp info in new_op_info event test.
    if table_name == "":
        raise Exception("No table found!")

    data = create_event_data("get_table",{"table_name":table_name})
    r = requests.get(working_address, data=json.dumps(data))
    if (r.content.decode().__contains__("un-supoorted event get_table")):
        raise Exception("Un supported event {:s} get_table".format(str("get_table")))
    if str(r.content).upper().__contains__("ERROR"):
        raise Exception("Error during fetching table {:s}".format(str(table_name)))    
    with open('file.data', 'wb') as file:
        file.write(r.content)
        return True

'''
@event_name:new_orderbook
@event_data:type:nested_dictionary  (order_book_name:"sample_order_book" , "data": order_book_data:dictionary(json) )
@event_return:success
@Explanation:This event stores order book information into a single json file like koineks.json. 
Especially this event will be used by koineks_service that collects data from koineks.com and post it to the server.
So this data will be served to op_finder instances.
So just store the given data into the json file whose name is order_book_name.
sample file can be found at ozenoglu.com/order_books/koineks.json
'''
@test_method
def test_new_orderbook_event():
    r = requests.get("https://ozenoglu.com/order_books/test_order_book.json")
    sample_orderbook_data = json.loads(r.content.decode("UTF-8"))
    nested_data = {'orderbook_name':'test_order_book','data':sample_orderbook_data}
    data = create_event_data("new_orderbook", nested_data)
    send_event(data)


'''
@event_name:get_orderbook
@event_data:wanted_order_book_name:string
@event_return:order_book info in json format(dictionary)
@Explanation:This event should return stored order book data in new_order_book_event
sample file can be found at ozenoglu.com/order_books/koineks.json
Note that , Expected_order_book_data is "https://ozenoglu.com/order_books/test_order_book.json" , because we posted it in new_order_book_event.
So it should return the order_book that is wanted and specified by the name of the order_book. like koineks. like btcturk.
if btcturk is given then you should return btcturk order book data..
'''
@test_method
def test_get_orderbook_event():
    r = requests.get("https://ozenoglu.com/order_books/test_order_book.json")
    expected_order_book_data = json.loads(r.content.decode("UTF-8"))
    expected_order_book_data = json.dumps(expected_order_book_data, sort_keys=True)
    data = create_event_data("get_orderbook","test_order_book") #test_order_book is name of order book which is wanted to get..
    result = send_event_custom_check(data)
    if (result == expected_order_book_data) is not True:
        raise Exception("result is not as expected!")


'''
@event_name:get_all_statistics
@event_data:None
@event_return:all statistic info in json format(dictionary)
@Explanation:This event should return statistics info related opportunities
Basically it shows best percentage of an opportunity in that day.
'''
@test_method
def test_get_all_statistics_event():
    data = create_event_data("get_all_statistics")
    result = send_event_custom_check(data)
    


'''
@event_name:get_statistics
@event_data:Date:str date of the desired statistics information
@event_return: statistics info in json format(dictionary)
@Explanation:This event should return statistics info related opportunities
Basically it shows best percentage of an opportunity of given date
'''
@test_method
def test_get_statistics_event():
    date = "2019-10-25"
    data = create_event_data("get_statistics", date)
    result = send_event_custom_check(data)

'''
@event_name:get_user_type
@event_data:username:string
@event_return:type of given user in plain text.(string)
@Explanation:In this event , you must return type of the given user.
'''
@test_method
def test_get_user_type_event():
    data = create_event_data("get_user_type","account_name")
    type = send_event_custom_check(data)
    if (type == "bronze" or type == "gold" or type == "platin" or type == "silver") is not True:
        raise Exception("Unexpected user type {:s}".format(str(type)))

'''
@event_name:login
@event_data:dictionary : {"username":"ozan","password":"2321"}
@event_return:success or fail in plain text
@Explanation:In this event , you must connect wordpress database and check if given informations are valid.
If yes , return success if not , return fail.
'''
@test_method
def test_login_event():
    login_data = {"username":"bronze_user","password":"12345"}
    data = create_event_data("login",login_data)
    send_event(data)


'''
Here we start testing phase1.
'''
def start_test_phase1(server_address:str):
    global working_address
    working_address = server_address
    is_server_running = is_server_alive()
    if is_server_running != True:
        print("First Start Server.")
        raise Exception("Server is not reachable!")

    test_send_sms_event()
    test_get_sms_event()
    test_new_orderbook_event()
    test_get_orderbook_event()


'''
Here we start testing phase2.
'''

def start_test_phase2(server_address:str):
    global working_address
    working_address = server_address
    is_server_running = is_server_alive()
    if is_server_running != True:
        print("First Start Server.")
        raise Exception("Server is not working exception")

    #test_new_opportunity_info_event("https://ozenoglu.com/opportunities/sample_opportunity.json")
    test_get_all_opportunity_info_event()
    test_get_opportunity()
    test_get_table_list_event()
    test_get_table_event()
    #test_get_all_statistics_event()
    #test_get_statistics_event()

'''
Here we start testing phase2.
'''
def start_test_phase3(server_address:str):
    test_get_user_type_event()
    test_login_event()


def is_api_service_working():
    test_server_address = remote_server_address #you can change it , to test remote server use remote_server_address variable.
    try:
        #start_test_phase1(test_server_address)
        start_test_phase2(test_server_address)
        debug("HttpServer is working {:s}".format(str(test_server_address)))
        #start_test_phase3(test_server_address)
        return True
    except Exception as e:
        return False

if __name__ == "__main__":

    test_server_address = remote_server_address #you can change it , to test remote server use remote_server_address variable.
    try:
        user_feedback("We're gonna test server where serves at {:s}".format(str(test_server_address)))
        start_test_phase1(test_server_address)
        start_test_phase2(test_server_address)
        #start_test_phase3(test_server_address)
    except Exception as e:
        error("There is problem with api service!")
        
