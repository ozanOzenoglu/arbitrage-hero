import os,signal
import threading
import time
import subprocess
import json
from api.third_party.watchdog.observers import Observer
from api.third_party.watchdog.events import PatternMatchingEventHandler

from api.base.crypto_engine.setting_db.request_info import RequestInfo,RequestType
from api.base.crypto_engine.MessageApi.debug import *
from api.base.services.i_watchable_service import IWatchableService
from api.base.crypto_engine import symbols

def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))
        return result
    return catched

class FileEventHandler(PatternMatchingEventHandler):
    patterns = ["*.request"]
    service_instance = None

    def save_service(self,service_instance):
       FileEventHandler.service_instance = service_instance

    def process(self, event):
        debug("event type: {:s}".format(str(event.event_type)))
        if (str(event.event_type) == "modified"):
            try:
                FileEventHandler.service_instance.save_new_request(event.src_path)
            except Exception as e:
                error("Error during load balancing: {:s}".format(str(e)))

    def on_modified(self, event):
        info("ON MODIFIED!")
        self.process(event)

    def on_created(self, event):
        pass

class HandlerInstance:
    busy_file =  "is_busy.info"

    def __init__(self,request_folder:str,busy:bool,type:str):
        self.__type = type
        self.__is_busy = busy
        self.__request_folder_name = ""
        self.set_folder(request_folder)
        self.__busy_file = request_folder + "/is_busy.info"

    def get_type(self):
        return self.__type

    def get_folder(self):
        return self.__folder

    def get_request_folder_name(self):
        return self.__request_folder_name

    def set_folder(self,folder:str):
        self.__folder = folder
        arr = folder.split('/')
        last_len = len(arr)
        name = arr[last_len-1]
        self.__request_folder_name = name

    def is_busy(self):
        try:
            with open(self.__busy_file , "r") as busy_file:
                is_busy = busy_file.readline()
                if (str(is_busy).upper() == "TRUE"):
                    return True
                else:
                    return False
        except Exception as e:
            return True #? bu ne amk

    def register_request(self,path):
        debug("Register Request for {:s}".format(str(path)))
        if os.path.isfile(path) is True:
            from_path = path
            to_path = self.get_folder()
            user_feedback("New Request REGISTERED to {:s}".format(str(self.__request_folder_name)))
            try:
                with open(path , "r") as request_file:
                    request_info = request_file.read()
                    with open(self.get_folder() + "/new.request", "w") as new_request:
                        new_request.write(request_info)

            except Exception as e:
                error("Error during registering new request!")
            finally:
                try:
                    if os.path.exists(path) is True:
                        os.remove(path)
                    else:
                        error("Error during request registration , request file is lost ? !:P ")
                except Exception as e:
                    error("Error during request registration {:s}".format(str(e)))
        else:
            error("Error {:s} is not exists".format(str(path)))

class LoadBalancer(IWatchableService):
    REQUEST_DIR = symbols.MAIN_REQUEST_FOLDER
    REQUEST_HANDLER_SERVICE_DIR = symbols.REQUEST_HANDLER_SERVICE_DIR
    HANDLERS_STATUS_FILE = REQUEST_DIR + "open_handlers.info"
    requests = [] #path:str #MUST
    requests_lock = threading.RLock()
    handlers = {} # {path:handler_instance} #MUST
    handler_lock = threading.RLock() # any process related to handlers
    def __init__(self):
        super().__init__("LoadBalancer",-1)
        self.request_handlers = {}
        self.__is_service_healthy = True

    def init(self):
        self.__init__()
        return self

    #MUST
    @staticmethod
    def is_any_handler_healthy(handler_name:str):
        avaiable_handler_count = LoadBalancer.get_avaiable_handler_count(handler_name)
        if (avaiable_handler_count > 0) :
            return True
        else:
            return False


    #MUST
    def update_handler_count_file(self,ie:dict): #open handlers count
        try:
            with open(LoadBalancer.HANDLERS_STATUS_FILE ,"w") as handler_info_file:
                handler_info_file.write(str(json.dumps(ie)))
        except Exception as e:
            error("Error during updating handler count {:s}".format(str(e)))

    #MUST
    @staticmethod
    def get_avaiable_handler_count(looking_handler_name:str): #open handlers count
        try:
            with open(LoadBalancer.HANDLERS_STATUS_FILE ,"r") as handler_info_file:
                de = json.load(handler_info_file)
                handler_names = de.keys()
                for handler_name in handler_names:
                    if str(handler_name).__contains__(looking_handler_name):
                        looking_handler_name = handler_name
                handler_entity_count = de.pop(handler_name,None)
                if (handler_entity_count) == None:
                    return 0
                else:
                    return int(handler_entity_count)
        except Exception as e:
            error("Error during getting handler count {:s}".format(str(e)))
            return 0

    #MUST
    def save_new_request(self,path:str): #this is called from another thread , so you should rlcok for shared requets lock!
        with self.requests_lock:
            self.requests.append(path)
            self.process_new_requests()
    #MUST
    def parse_requests(self,request_file):

        with(open(request_file,"r")) as request_file:
            request_list = []
            data = json.load(request_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                request = RequestInfo.json_to_instance(val)
                request_list.append( request)
            return request_list
    #MUST
    def destroy_request(self,request_path:str):
        if (os.path.isfile(request_path)):
            debug("{:s} is eliminated which is already listed".format(str(request_path)))
        else:
            error("Request {:s} does not exists".format(str(request_path)))

    #MUST
    def process_new_requests(self): #This function eliminates same request and order them in order to their priority!
        urgent_fetch_requests = {}
        fetch_requests = {}
        get_all_balance = []
        important_request = []
        if (len(self.requests) == 0):
            debug("No Requests to balance yet..")
            return

        try:
            current_request_file = self.requests.pop()
            while(current_request_file != None):
                requests = self.parse_requests(current_request_file)
                if (len(requests) > 0):
                    request = requests[0]
                type  = request.get_type()
                if type == RequestType.FETCH_FOR_HELP_URGENT:
                    symbol = request.get_symbol()
                    if urgent_fetch_requests.keys().__contains__(symbol) is not True:
                        urgent_fetch_requests.update({symbol:current_request_file})
                        #debug("Urgent {:s} Fetch Added First Time".format(str(symbol)))
                    else:
                        self.destroy_request(current_request_file)
                elif type== RequestType.FETCH_FOR_HELP:
                    symbol  = request.get_symbol()
                    if (urgent_fetch_requests.keys().__contains__(symbol) is not True and fetch_requests.keys().__contains__(symbol) is not True):
                        fetch_requests.update({symbol:current_request_file})
                        #debug("Normal {:s} Fetch Added First Time".format(str(symbol)))
                    else:
                        self.destroy_request(current_request_file)
                elif type == RequestType.GET_ALL_BALANCE:#TODO: investigate this block , seems to me buggy.
                    if (len(get_all_balance) > 0):
                        self.destroy_request(current_request_file)
                    else:
                        get_all_balance.append(current_request_file)
                        #debug("Get All Balance Added First Time")
                else: # don't eliminate these request , they must already be a unique calls. like buy,sell,withdraw!
                    user_feedback("{:s} request will not be processed and eliminated!".format(str(type)))
                    important_request.append(current_request_file)
                if (len(self.requests) > 0):
                    current_request_file = self.requests.pop()
                else:
                    current_request_file = None
            if (fetch_requests.__len__() > 0): # lowest priority request
                symbols = fetch_requests.keys()
                for symbol in symbols:
                    request_path = fetch_requests.__getitem__(symbol)
                    self.requests.append(request_path)

            if (urgent_fetch_requests.__len__() > 0): # higher priority requests
                symbols = urgent_fetch_requests.keys()
                for symbol in symbols:
                    request_path = urgent_fetch_requests.__getitem__(symbol)
                    self.requests.append(request_path)
            if len(get_all_balance) > 0: # higher priority than urgent_fetchs
                self.requests.append(get_all_balance[0])

            if (len(important_request) > 0): # these requests has to be balanced immediately! These will be probably for arbitrage operations like buy,sell,withdraw!
                self.requests.extend(important_request)

        except Exception as e:
            error("Error during processing requests! {:s}".format(str(e)))

    #MUST
    @trycatch
    def delete_existing_handler(self,path):
        dead_handler = self.handlers.pop(path)
        request_folder_name = dead_handler.get_request_folder_name()
        user_feedback("{:s} is a dead handler and deleted !".format(str(request_folder_name)))

    #MUST
    def save_new_handler(self,path:str,type:str):
        handler_instance = HandlerInstance(path, False, type)
        self.handlers.update({path:handler_instance})

    #MUST
    def check_if_healthy(self,handler_path):
        try:
            handler_path = handler_path + "/" if str(handler_path).endswith("/") is not True else handler_path
            healthy_file_path = handler_path + symbols.HANDLER_HEALTHY_FILE_NAME
            if os.path.isfile(healthy_file_path) is True:
                with open(healthy_file_path , "r") as healthy_file:
                    status = healthy_file.readline()
                    if status.lower() == "true":
                        return True
            else:
                return False
        except Exception as e:
            error("Error during checking health status of handler {:s}".format(str(handler_path)))
            return  False

    #MUST
    def is_any_new_handler_avaiable(self):
        with LoadBalancer.handler_lock:
            for file in os.listdir(LoadBalancer.REQUEST_HANDLER_SERVICE_DIR): # Main Handler Directory , Koineks,Btcturk Main Dirs are here.

                path = LoadBalancer.REQUEST_HANDLER_SERVICE_DIR + file #Sub Handler Directory , could be one of Btcturk,Koineks,Vebit etc..
                if os.path.isdir(path):
                    type = file
                    handlers_of_type = self.request_handlers.pop(type,None)
                    handlers_of_type = handlers_of_type if handlers_of_type != None else []

                    for handler_dirs in os.listdir(path):
                        handler_path = path + "/" + handler_dirs
                        is_healthy = self.check_if_healthy(handler_path)
                        if is_healthy: # if handler is working
                            if handlers_of_type.__contains__(handler_path) is not True: #check if we added it before
                                handlers_of_type.append(handler_path)
                                self.save_new_handler(handler_path,type)
                        else: #if not working
                            if handlers_of_type.__contains__(handler_path) is True: #check if a health working handler died? if so , delete it from working hnadler list.
                                handlers_of_type.remove(handler_path)
                                self.delete_existing_handler(handler_path)

                    self.request_handlers.update({type:handlers_of_type})
                    avaiable_handlers_count = len(handlers_of_type) if handlers_of_type != None  else 0
                    information_element = {type: avaiable_handlers_count}
                    self.update_handler_count_file(information_element)

    #MUST
    def find_request_handler_type(self,request_file):
        with(open(request_file, "r")) as request_file:
            content = json.load(request_file)
            request = RequestInfo.json_to_instance(content)
            handler_name = request.get_handler_name()
            return handler_name

    #MUST
    def balance_load(self):
        if len(self.requests) > 0:
            user_feedback("Request Count {:d}".format(int(len(self.requests))))
        with LoadBalancer.handler_lock:
            handlers = self.handlers.keys()

        current_requests = self.requests.copy()
        self.requests.clear() #clear saved

        while(len(current_requests) != 0): #while we have request in request queue.
            request_path = current_requests.pop()
            request_handler_type = self.find_request_handler_type(request_path)

            handler_found = False
            #we don't use  handler lock here because we want to let other thread be able to update for newly closed handler , so we can avoid from trying to use them ;)
            for handler_path in handlers: #iterate over all handlers and share requests among avaiable handlers
                try:
                    handler = self.handlers.__getitem__(handler_path)
                except Exception as e:
                    error("Error getting handler , handler may be closed! {:s}".format(str(e)))
                    return # let service to call balance_load again so we can work with updated handlers information..
                if (handler.get_type().__contains__(request_handler_type) is not True):
                    continue
                if (handler.is_busy() == False):
                    try:
                        handler_found = True
                        handler.register_request(request_path)
                        user_feedback("Reamining Request Count {:d}".format(int(len(current_requests))))
                        time.sleep(2) # wait for handler fot setting itself as Busy #TODO find a better way instead of wait 2 secs MAL
                        break
                    except Exception as e:
                        error("Error during register_request {:s}".format(str(e)))
                else:
                     debug("{:s} is busy".format(str(handler.get_request_folder_name())))
            if (handler_found == False):
                debug("No Free handler found!  Remaining Request: {:d}".format(int(len(current_requests))))
                time.sleep(2) # let handlers done their work!

    def set_service_healthy(self,state:bool):
        self.__is_service_healthy = state

    def is_service_healthy(self):
        return self.__is_service_healthy

    def start(self):
        observer = Observer()
        handler = FileEventHandler()
        handler.save_service(self)
        observer.schedule(FileEventHandler(), path = LoadBalancer.REQUEST_DIR)
        observer.start()
        try:
            while True :
                try:
                    #self.process_new_requests() it's caled when new request is saved automatically now.
                    self.is_any_new_handler_avaiable()
                    self.balance_load()
                    time.sleep(1)
                    if (self.is_service_healthy() != True):
                        user_feedback("destructor initialized , Good bye from load balancer")
                        observer.stop()
                        observer.join()
                        break
                except Exception as e:
                    error("FATAL ERROR during loader_service {:s}".format(str(e)))

        except KeyboardInterrupt:
            observer.stop()

        return


