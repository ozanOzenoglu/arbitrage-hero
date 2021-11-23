import threading
import os
from io import open

from third_party import splinter
from api.base.crypto_engine.utils.mail import BtcTurkMail

from api.base.crypto_engine.setting_db.request_info import RequestInfo , RequestType
from api.base.crypto_engine.MessageApi.debug import *

from third_party.watchdog.observers import Observer
from third_party.watchdog.events import PatternMatchingEventHandler



class BtcTurkService:  # BtcTurkServicelinte process
    DUMP_DIR = 'data_to_send/exception_dumps/'

    REQUEST_DIR =  os.path.abspath("").split(sep='src')[0] + 'src/btcturk_service/requests/'
    SS_FOLDER = "/home/ozy/workspace/koineks/src/btcturk_service/ss/"
    ORDER_BOOK_DIR = os.path.abspath("").split(sep='src')[0] + 'src/order_books'
    ORDER_BOOK_FILE = ORDER_BOOK_DIR + "/btcturk.json"
    MAX_WAIT_TIME = 12

    is_initialised = False

    browser_lock = threading.RLock()
    BtcTurkHealthy = "BtcTurkHealthy"
    browser = None
    is_service_healthy = True
    btcturk_order_books = {BtcTurkHealthy: 'True'}

    btcturk_url = "https://www.btcturk.com"
    is_logged = False
    your_account = {'username': 'btcturk.ozan@gmail.com', 'password': 'Ozandoruk1989!'}



    @staticmethod
    def is_service_healthy():
        with open(BtcTurkService.ORDER_BOOK_FILE,"r") as btcturk_order_book:
            data = json.load(btcturk_order_book)
            is_healthy = data.__getitem__(BtcTurkService.BtcTurkHealthy)
            if str(is_healthy).upper() != "TRUE" :
                return False
            else :
                return True



    btcturk_order_books = {BtcTurkHealthy: 'True'}

    def __init__(self,working_path):
        debug("BtcTurkService  initalised is started")
        self.__config_path = working_path


        self.__new_requests = []

        user_feedback("BtcTurk Service is initialised!")

        self.init()


    @staticmethod
    def update_order_books_file():

        if not os.path.exists(BtcTurkService.ORDER_BOOK_DIR):
            os.makedirs(BtcTurkService.ORDER_BOOK_DIR)

        with open(BtcTurkService.ORDER_BOOK_FILE, 'wb') as outputfile:
            byte_array = bytearray(json.dumps(BtcTurkService.btcturk_order_books),'utf8')
            outputfile.write(byte_array)

    @staticmethod
    def update_healtyh_state(state: str):

        BtcTurkService.btcturk_order_books.update({BtcTurkService.BtcTurkHealthy: state})
        BtcTurkService.is_healthy = True if str(state).upper() == "TRUE" else False
        BtcTurkService.update_order_books_file()
        if BtcTurkService.is_healthy is not True:
            android_alarm("BtcTurkService is closed")
            exit(-1)






    def add_new_requests(self,new_requests):

        size = len(new_requests) -1
        while size >= 0:
            self.__new_requests.append(new_requests[size])
            size = size -1
        return 0


    def parse_requests(self,request_file):

        with(open(request_file,"r")) as request_file:
            request_list = []
            data = json.load(request_file)
            user_feedback("Raw Request is : {:s}".format(str(data)))
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                request = RequestInfo.json_to_instance(val)
                if (request.get_type() != RequestType.WITHDRAW):
                    raise Exception("Parse error , request type is not withdraw it's {:s}".format(request.get_type()))

                request_list.append( request)

            return request_list


    @staticmethod
    def update_healtyh_state(state:str):

        BtcTurkService.btcturk_order_books.update({BtcTurkService.BtcTurkHealthy:state})
        BtcTurkService.is_service_healthy = True if str(state).upper() == "TRUE" else False
        BtcTurkService.update_order_books_file()
        if BtcTurkService.is_service_healthy is not True:

            android_alarm("KoinekksService is closed")
            exit(-1)

    @staticmethod
    def push_request(request:RequestInfo):
        if(BtcTurkService.is_service_healthy() is not True):
            return -1

        request_file_name = request.get_log_file_name() + ".request"
        try:
            file_path = BtcTurkService.REQUEST_DIR + request_file_name
            with(open (file_path , "w")) as request_file:
                request_as_str = str({request.get_log_file_name() : request.to_json() })
                request_as_str = request_as_str.replace('\'','"')

                request_file.write(request_as_str)
            return 0
        except Exception as e:
            error(str(e))
            return -1




    def start_request(self,request:RequestInfo):
        request_date = str(datetime.now())
        request_date = request_date.replace(' ', '_').split('.')[0]

        if request.get_type() == RequestType.WITHDRAW:
            log_file_name = request.get_log_file_name()
            destination = request.get_destination()
            symbol = request.get_symbol()
            amount = request.get_amount()
            if str(symbol).upper() == "XRP":
                tag = request.get_tag()

            BtcTurkService.withdraw(symbol,destination,amount,tag)
            mail_helper = BtcTurkMail(BtcTurkService.your_account['username'],BtcTurkService.your_account['password'])
            link = ""
            while (link.__contains__("btcturk") is not True):
                time.sleep(5)
                try:
                    link = mail_helper.get_btcturk_confirmation_link()

                    BtcTurkService.browser.visit(link)
                    time.sleep(2)

                except Exception as e:
                    error("Exception during e-mail confirmation step: {:s}".format(str(e)))
                    BtcTurkService.save_screen_shot_at(BtcTurkService.SS_FOLDER+log_file_name+"_error_"+request_date+".png")

            BtcTurkService.save_screen_shot_at(BtcTurkService.SS_FOLDER+log_file_name+"_result_"+request_date+".png")
            msg = "Withdraw request completed {:s} {:s} {:d} {:s}".format(str(request.get_buy_exchange().related_market().get_name()),
                                                                                  str(request.get_sell_exchange().related_market().get_name()),
                                                                                  float(request.get_amount()),
                                                                                  str(request.get_symbol()))
            user_feedback(msg)

        elif request.get_type() == RequestType.GET_BALANCE:
            raise Exception("not implemented yet")











    def process_request(self):

        if (len(self.__new_requests) > 0 ): #if we have new request process them and remove from the list.

            current_request = self.__new_requests.pop()


            while (current_request != None):
                try:
                    self.start_request(current_request)
                except Exception as e:
                    error(str(e))
                try:
                    if ( len(self.__new_requests) > 0):
                        current_request = self.__new_requests.pop()
                    else:
                        current_request = None
                except Exception as e :
                    error(str(e))







    def start_service(self):
        user_feedback("simulator service is started")
        observer = Observer()
        handler = MyHandler()
        handler.save_service(self)
        observer.schedule(MyHandler(), path= BtcTurkService.REQUEST_DIR)
        observer.start()

        try:
            while True:
                self.process_request()
                time.sleep(1)

        except KeyboardInterrupt:
            observer.stop()

        observer.join()

    @staticmethod
    def login_with_your_account():
        if BtcTurkService.is_logged:
            return
        try:
            BtcTurkService.browser_lock.acquire()
            url = 'https://www.btcturk.com/Account/Login'
            BtcTurkService.browser.visit(url)
            BtcTurkService.browser.find_by_name('Email')._set_value(BtcTurkService.your_account['username'])
            BtcTurkService.browser.find_by_name('Password')._set_value(BtcTurkService.your_account['password'])
            button = BtcTurkService.browser.find_by_text('GİRİŞ YAP')[1];
            time.sleep(4) #wait for user click on captcha! #TODO auto click captcha , #TODO2 auto resolve captcha if you can :)
            BtcTurkService.is_logged = True
            # Interact with elements
            button.click()

        except Exception as e:
            print(str(e))
        finally:
            BtcTurkService.browser_lock.release()



    @staticmethod
    def go_to_withdraw_page(symbol:str):
        if symbol == "XRP":
            ending = "Ripple"
        elif symbol == "BTC":
            ending = "Bitcoin"
        elif symbol == "ETH":
            ending = "Ethereum"
        BtcTurkService.browser.visit("https://www.btcturk.com/Withdrawal/"+ending)






    @staticmethod
    def withdraw(symbol:str,destination:str,amount:float,tag:str=""):

        BtcTurkService.go_to_withdraw_page(symbol)

        amount_precision = amount-int(amount)
        amount = int(amount)# round it

        if amount == 0:
            amount = "0"
        if amount_precision == 0:
            amount_precision = "0"
        else:
            amount_precision = str(amount_precision).split('.')[1]


        destination_element = BtcTurkService.browser.find_by_name("RecieverAddress")
        if symbol.upper() == "XRP" :
            button = BtcTurkService.browser.find_by_css('div[class="withDrawalBtcContainer"] input')[6]
            tag_element = BtcTurkService.browser.find_by_name("DestinationTag")
            tag_element._set_value(tag)
        else:
            button = BtcTurkService.browser.find_by_css('div[class="withDrawalBtcContainer"] input')[5]

        amount_element = BtcTurkService.browser.find_by_name("Amount")
        precision_element = BtcTurkService.browser.find_by_name("AmountPrecision")

        destination_element._set_value(destination)
        amount_element._set_value(str(amount))
        precision_element._set_value(str(amount_precision))


        button.click()




    def init(self):
        if BtcTurkService.is_initialised == True:
            return
        with BtcTurkService.browser_lock:
            BtcTurkService.browser = splinter.Browser()
            BtcTurkService.login_with_your_account()
            user_feedback("BtcTurk Service init finished")
            BtcTurkService.is_initialised = True
            BtcTurkService.update_healtyh_state("True")


    @staticmethod
    def dump_log_with_ss(log_msg: str):
        now = datetime.now()
        time_stamp = str(now.year) + ':' + str(now.month) + ':' + \
                     str(now.day) + ':' + str(now.hour) + ':' + str(now.minute) + ':' + str(now.second)
        if os.path.exists(BtcTurkService.DUMP_DIR) is not True:
            try:
                os.makedirs(BtcTurkService.DUMP_DIR)
            except Exception as e:
                raise e

        try:
            log_dir = BtcTurkService.DUMP_DIR + time_stamp
            os.makedirs(log_dir)

            BtcTurkService.save_screen_shot_at(log_dir + '/ss.png')

            with (open(log_dir + '/log_msg.log', 'w')) as log_file:
                log_file.write(log_msg)
        except Exception as e:
            raise e

    @staticmethod
    def get_ss():
        try:

            driver = BtcTurkService.browser.driver
            image_binary = driver.get_screenshot_as_png()
            return image_binary
        except Exception as e:

            raise e

    @staticmethod
    def save_screen_shot_at(location: str):
        image_binary = BtcTurkService.get_ss()
        debug(location + 'is saved')
        with(open(location, 'wb')) as out_file:
            out_file.write(image_binary)
        return

    def wait_before_try(self, wait_time, exception):

        if (str(exception) == "Tried to run command without establishing a connection"):
            error("Tried to run command came , healthy state set as False")
            self.update_healtyh_state("false")

        error("wait time is {:d} ".format(int(wait_time)) + "for " + str(exception))
        if (wait_time >= 8):
            try:
                BtcTurkService.dump_log_with_ss(str(exception))
            except Exception as e:
                error("Error during dump_log_with_ss : {:s}".format(str(e)))
        if (wait_time >= BtcTurkService.MAX_WAIT_TIME):
            error("wait time is higher than max wait time , is set to max wait time ")
            wait_time = BtcTurkService.MAX_WAIT_TIME
        time.sleep(wait_time)














class MyHandler(PatternMatchingEventHandler):
    patterns = ["*.request"]



    service_instance = None

    def save_service(self,service_instance):
       MyHandler.service_instance = service_instance

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print( event.src_path, event.event_type ) # print now only for degug
        if (str(event.event_type) == "modified"):
            try:
                new_requests  = MyHandler.service_instance.parse_requests(event.src_path)
                os.remove(event.src_path)
                MyHandler.service_instance.add_new_requests(new_requests)

            except Exception as e:
                error("Error during parsing: {:s}".format(str(e)))

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)






