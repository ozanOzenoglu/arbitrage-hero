from http.server import BaseHTTPRequestHandler

import json
import time
from io import BytesIO

from api.server.library import orderbook, sms, opportunity , tables, statistic, version, user
from api.base.crypto_engine.MessageApi.debug import *


class MyHandler(BaseHTTPRequestHandler):
    PRIVATE_KEY = ""
    def _set_headers(self, type):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def is_pk_valid(self, private_key: str):
        if str(private_key) == self.PRIVATE_KEY:
            return True
        else:
            error("Invalid private key!")
            return False

    def read_payload(self):
        len = self.headers.get('Content-Length')
        post_body = self.rfile.read(int(len))
        payload = post_body.decode()
        return payload

    def return_text_message(self, message: str):
        self._set_headers("application/json")
        if type(message) != type(""):
            message = json.dumps(message) #TODO: here we were using str(message) instead of json.dumps( check vanidity control for other api services..)

        self.wfile.write(message.encode("UTF-8"))

    def return_binary_data(self,content):
        f = BytesIO()
        f.write(content)
        length = f.tell()
        self.send_response(200)
        self.send_header("Content-type", "application/octet-stream")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        self.wfile.write(content)

    def return_error_message(self, message: str , error_code:int = 401):
        self.send_error(error_code, message)

    def handle_event(self, event: str, data: dict):
        debug("Starting process event %s " % event)

        if event == 'new_opportunity_info':
            debug("[handle_event] 'new_opportunity_info' event is received")
            data =  data.get("data",{})
            try:
                opportunity.create_new_ops(data)
                self.return_text_message("success")
            except Exception as e:
                self.return_error_message("Error during creating opportunities: {:s}".format(str(e)))
        
        elif event == "update_sms_code":
            ts = time.time() * 1000 #ms
            sms_content = data.get('data', {})
            sms_content += " update_time:"  + str(ts)
            sms_file = data.get("sms_name", {})
            sms.create_sms_file(sms_file, sms_content)
            self.return_text_message("success")

        elif event == "get_sms_code":
            sms_type = data
            sms_code = sms.get_code(sms_type)
            if sms_code:
                self.return_text_message(sms_code)
            else:
                error("No sms code found.")

        elif event == "new_orderbook":
            debug("new_orderbook event handling.")
            '''here orderbook_name is actually market_name'''
            market_name = data.get("orderbook_name", "")
            ob_data = data.get("data", {})
            orderbook.create_new_orderbook(market_name, ob_data)
            self.return_text_message("success")

        elif event == "get_orderbook":
            if data:
                market = data
            debug("get_orderbook event handling.")
            ob = orderbook.get_orderbook(market)
            self.return_text_message(ob)
        elif event == "get_all_opportunity_info":
            op_type = data
            payload = opportunity.get_all_best_ops()
            if len(payload) == 0:
                self.return_error_message("No opportunies is listed for type {:s}".format(str(op_type)))
            else:
                self.return_text_message(payload)
        elif event == "get_opportunity_info":
            op_type = data
            payload = opportunity.get_opportunity(data)
            if len(payload) == 0:
                self.return_error_message("No opportunies is listed for type {:s}".format(str(op_type)))
            else:
                self.return_text_message(payload)
        elif event == "get_table_list":
            try:
                creator = data.get("creator")
                live_requested = data.get("live_requested")
                table_list = tables.get_table_list(live_requested,creator)
                self.return_text_message(table_list)
            except Exception as e:
                error("viy amk")

        elif event == "get_table": #This will get from live tables..
            table_name = data.get("table_name")
            content = tables.read_table_content(table_name, live=True)
            self.return_binary_data(content)
        
        elif event == "get_old_table": #TODO: NOT IMPLEMENTED YET! ### get_statistic_table is implemented instead of this function
            table_name = data.get("table_name")
            content = tables.read_table_content(table_name, live = False)
            self.return_binary_data(content)
        elif event == "get_statistic_table": 
            table_name = data.get("table_name")
            content = tables.get_statistic_table(table_name)
            self.return_binary_data(content)
        elif event == "get_version":
            currentVersion = version.get_app_version()
            self.return_text_message(currentVersion)  
        
        #STATISTIC EVENTS
        elif event == "get_daily_statistic":                     
            user_feedback("get_daily_statistic event handler..")
            content = statistic.get_today_statistics()
            if len(content) == 0:
                self.return_error_message("No Statistics File Found!")        
            user_feedback("{:d} files are found in statistic folder".format(int(len(content))))
            self.return_text_message(content)
        elif event == "get_weekly_statistic":                     
            user_feedback("get_weekly_statistic event handler..")
            content = statistic.get_weekly_statistics()
            if len(content) == 0:
                self.return_error_message("No Statistics File Found!")        
            user_feedback("{:d} files are found in statistic folder".format(int(len(content))))
            self.return_text_message(content)
        elif event == "get_monthly_statistic":                     
            user_feedback("get_monthly_statistic event handler..")
            content = statistic.get_monthly_statistics()
            if len(content) == 0:
                self.return_error_message("No Statistics File Found!")        
            user_feedback("{:d} files are found in statistic folder".format(int(len(content))))
            self.return_text_message(content)
        
        
        elif event == "get_all_statistics":#For backward compability..
            time_interval = data          
            user_feedback("get_all_statistic event handler..") 
            if str(time_interval).upper() == "DAILY":
                content = statistic.get_today_statistics()
            elif str(time_interval).upper() == "MONTHLY":
                content = statistic.get_monthly_statistics()
            elif str(time_interval).upper() == "WEEKLY":
                content = statistic.get_weekly_statistics()
            elif str(time_interval).upper() == "ALL_STATISTICS":
                daily = statistic.get_today_statistics()
                weekly = statistic.get_weekly_statistics()
                monthly = statistic.get_monthly_statistics()
                content = {"daily":daily, "weekly":weekly, "monthly":monthly}
            else:                
                content = statistic.get_today_statistics()
            
            if len(content) == 0:
                self.return_error_message("No Statistics File Found!")        
            user_feedback("{:d} files are found in statistic folder".format(int(len(content))))
            self.return_text_message(content)
        elif event == "get_statistics":
            date = data
            content = statistic.get_statistic(date)            
            self.return_text_message(content)
        elif event == "upload_order_book":
            data_type = type(data)
            str_type = type("str")
            if data_type == str_type:
                try:
                    data = json.loads(data)
                except Exception as e:
                    error("Error in upload_order_book event converting data[type:{:s}] converting to dict Error:{:s}".format(str(type(data)),str(e)) )
            market_name = data.pop("market_name",None)
            if market_name == None:
                self.return_error_message("No market name is provided for upload_order_book event!")
                return
            order_book_info = data
            result = orderbook.update_order_book(market_name, order_book_info)
            self.return_text_message("Ok")
        elif event == "get_order_book":
            if type(data) == type(""):
                data = json.loads(data) #convert to dict.
            market_name = data.get("market_name")
            symbol_pair = data.get("symbol_pair")
            ret = orderbook.get_orderbook(market_name)
            ret = ret.get(symbol_pair)
            self.return_text_message(ret)
        elif event == "get_online":
            online_user_count = user.get_online()
            self.return_text_message(online_user_count)
        elif event == "register_user":
            try:
                user_id = data
                user.register_user(user_id)
                self.return_text_message("user id {:s} is registered".format(str(user_id)))
            except Exception as e:
                error("Error during updating_user last sean time: {:s}".format(str(e)))
                self.return_error_message("Error during registering user {:s}".format(str(e)))
            
        else:
            error("unsupported event {:s}".format(str(event)))
            self.return_error_message("unsupported event {:s}".format(str(event)))
            return -1

    def handle_request(self, request: str, payload: str):
        private_key = ""
        event = ""
        data = ""

        # handle only api_calls for now
        if not payload:
            error("payload can't be None")
            return
        payload = json.loads(payload)

        try:
            private_key = payload.__getitem__('private_key')
            event = payload.__getitem__('event')
            data = payload.__getitem__('data')
        except Exception as e:
            error("Exception during [handle_request] {:s}".format(str(e)))

        if private_key != "":
            valid_key = self.is_pk_valid(private_key)
            if valid_key:
                if event != "" and data != "":
                    try:
                        ret = self.handle_event(event, data)
                        #TODO: give error message according to ret
                    except Exception as e:
                        error("Exception at [handle_event] {:s}".format(str(e)))
                        self.send_error(201, "fail")
                else:
                    self.send_error(401, "[handle_request] empty event or data")
            else:
                self.send_error(31,"")
        else:
            error("[handle_request] No private key found in the payload ")

    def _do_GET(self):
        try:
            payload = self.read_payload()
            if (payload.__contains__("'")):
                debug("payload sent in wrong format for json.loads ' will be changed as \" ")
                payload = payload.replace("'", "\"")
            if (payload.__contains__('\n')):
                payload = payload.replace("\n", " ");
            self.handle_request(self.path, payload)
        except Exception as e:
            error("error during do_Get {:s}".format(str(e)))

    def do_GET(self):
        try:
            if self.path.__contains__("api_call"):
                return self._do_GET()
            debug("Get request by: {:s}".format(str(self.client_address)))
        except Exception as e:
            error("Error during handling get request {:s}".format(str(e)))

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("Connecting to Server..".encode())
        return

    def do_POST(self):
        try:
            if (self.path.__contains__("api_call")):
                return self._do_GET()
        except Exception as e:
            error("Error during handing post request {:s}".format(str(e)))