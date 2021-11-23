import time
import shutil
import os
import json
import threading
import inspect

from base.crypto_engine.request_handler.koineks_handler import KoineksRequestHandler
from base.services.i_watchable_service import IWatchableService
from base.crypto_engine.utils import helper
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine import symbols

from base.crypto_engine.setting_db.request_info import RequestType,RequestInfo
from third_party.watchdog.observers import Observer
from third_party.watchdog.events import PatternMatchingEventHandler

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
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there

        user_feedback("event type: {:s}".format(str(event.event_type)))
        if (str(event.event_type) == "modified"):

            request_folder = self.service_instance.get_request_folder_path()
            try:
                debug("folder lock granted!")
                new_requests  = FileEventHandler.service_instance.parse_requests(event.src_path)
                FileEventHandler.service_instance.add_new_requests(new_requests)

            except Exception as e:
                error("Error during parsing: {:s}".format(str(e)))
            finally:
                try:
                    os.remove(event.src_path)
                except Exception as e:
                    error("Error during removing file {:s}".format(str(e)))

    def on_modified(self, event):
        debug("ON MODIFIED!")
        self.process(event)

    def on_created(self, event):
        pass

'''
This Service is general service that handles request and pass them to request_handler
This service constructor takes only one essential argument which is request_handler_class. Request_Handler_Service
create a request_handler instance from this class and use **kwargs if constructor of request_handler needs any parameter to start up.

After creating request_handler instance , RequestHandlerService starts listening the request_folder that is created on constructor of RequestHandlerService
for any new coming request file. Then catch these new file , parse them and add to queue to pass them to the request_handler_instance.

Briefly!
RequestHandlerService is main_service that catches requests , parses them and passes them to the request_handler_instance.
Request_handler instance is the responsible to taking action. So request_handler is actually doing the requested action.
like buy,sell , withdraw coins and etc. or whatsoever. 

'''
class RequestHandlerService(IWatchableService):
    MAX_CYCLE = 1000
    MAX_FAIL_COUNT = 5
    ALL_REQUESTS_FOLDER = symbols.MAIN_REQUEST_FOLDER
    REQUEST_HANDLER_SERVICE_DIR = symbols.REQUEST_HANDLER_SERVICE_DIR


    def __init__(self,request_handler_class,**kwargs):
        self.__request_handler_class = request_handler_class
        self.__kwargs = kwargs
        self.__requests = {}
        request_type_members = inspect.getmembers(RequestType)
        for request_type in request_type_members:
            type_name = str(request_type[1])
            if(type_name.__contains__("REQUEST")):
                self.__requests.update({type_name:[]})

        healthy_fnc = getattr(request_handler_class,"is_healthy",None) # check if RequestHandler class implement is_healthy func!
        if (healthy_fnc == None  or callable(healthy_fnc) != True):
            raise Exception("Request Handler must implement is_healthy function!")

        handle_request_fnc = getattr(request_handler_class,"handle_request",None) # check if RequestHandler class implement handle_request func!
        if (handle_request_fnc == None  or callable(handle_request_fnc) != True):
            raise Exception("Request Handler must implement handle_request function!")

        try:
            handler_signature = inspect.signature(handle_request_fnc) #Check handle_request signature if valid.
            request_paramater_signature = str(handler_signature.parameters['request'])
            if request_paramater_signature.split(".")[-1] != "RequestInfo":
                raise NotImplemented("handle_request function must take a parameter in RequestInfo type!")
        except Exception as e:
            raise Exception("handle_request function should have a paramater as request in RequestInfo type!")

        self.init_handler(request_handler_class,kwargs)
        super().__init__(self._service_name,-1)

    def init(self):
        self.__init__(self.__request_handler_class,**self.__kwargs)
        return self

    def init_handler(self,handler_class,kwargs):

        try:
            self._handler_name = str(handler_class).split('.')[-1].split("RequestHandler")[0].lower()
            self._handler_main_requests_folder_path = RequestHandlerService.REQUEST_HANDLER_SERVICE_DIR + self._handler_name + symbols.REQUEST_HANDLER_TYPE_NAME + "/"
        except Exception as e:
            error("Fatal Error: Wrong Name Given to Class!. Handler Class name notain is %sRequestHandler")
            exit(-1)

        user_feedback("%s handler instance will be initialised!" % str((self._handler_name)))
        if os.path.exists(RequestHandlerService.REQUEST_HANDLER_SERVICE_DIR) is not True:
            user_feedback("{:s} folder is initialised for the first time".format(str(RequestHandlerService.ALL_REQUESTS_FOLDER)))
            os.makedirs(RequestHandlerService.REQUEST_HANDLER_SERVICE_DIR)

        if (os.path.exists(self._handler_main_requests_folder_path)) is not True:
            os.makedirs(self._handler_main_requests_folder_path)
            user_feedback("{:s} folder is initialised for the first time".format(str(self._handler_main_requests_folder_path)))

        created_folder = self.init_request_folder(self._handler_main_requests_folder_path)
        self._service_name = created_folder + "_service"
        self.__listening_request_folder_path = self._handler_main_requests_folder_path  + created_folder
        self.__handler_instance = handler_class(kwargs["username"], kwargs["password"], kwargs["driver_name"], kwargs["headless"])
        debug("Handler is initialised")

    @staticmethod
    def get_main_request_folder():
        return RequestHandlerService.ALL_REQUESTS_FOLDER

    def get_handler(self):
        return self.__handler_instance

    def get_requests(self):
        return self.__requests

    def is_handler_healthy(self):
        return self.__handler_instance.is_healthy()

    def get_request_folder_path(self):
        return self.__listening_request_folder_path

    def is_handler_busy(self):
        request_dir = self.get_request_folder_path()

        busy_file_path = request_dir + "/is_busy.info"
        try:
            with open(busy_file_path , "r") as busy_file:
                is_busy = busy_file.readline()
                if (str(is_busy).upper() == "TRUE"):
                    return True
                else:
                    return False
        except Exception as e:
            return True #? bu ne amk

    def set_handler_busy(self,state:bool):
        if (type(state) is not bool) :
            raise TypeError("set_helper_busy parameter is bool not {:s}".format(str(type(state))))
        request_dir = self.get_request_folder_path()
        busy_file_path = request_dir + "/is_busy.info"
        try:
            with open(busy_file_path , "w") as busy_file:
                if (state):
                    busy_file.write("True")
                else:
                    busy_file.write("False")
        except Exception as e:
            return True #? bu ne amk

    def update_handler_cycle(self, cycle: int):
        work_file = self.get_request_folder_path() + "/work_cycle.info"
        try:
            with open(work_file, "w+") as work_file:
                work_file.write(str(cycle))
        except Exception as e:
            error("Error during updating work cycle {:s}".format(str(e)))


    def set_handler_health_status(self,state:bool):
        if (type(state) is not bool) :
            raise TypeError("set_helper_health_status parameter is bool not {:s}".format(str(type(state))))
        self.__handler_instance.set_healthy_status(state)
        my_request_folder_path = self.get_request_folder_path()
        if (os.path.exists(my_request_folder_path) is not True):
            try:
                os.makedirs(my_request_folder_path)
            except Exception as e:
                error("Error during creating file dir {:s} error: {:s}".format(str(my_request_folder_path), str(e)))
                raise e
        with open(my_request_folder_path + "/is_healthy.info","w") as health_info:
            if (state):
                health_info.write("True")
            else:
                self.__handler_instance.de_init()
                health_info.write("False")
        if state is not True:
            pass
            #KoineksService.destructor(1,2)

    @trycatch
    def init_request_folder(self,main_request_folder): #TODO:Bu fonksiyonu tekrar  yaz. Silin request2 gibi folderlar varken boş slot olarak, gidip request7 alıyor request6 var diye..
        other_request_folders = []
        for file in os.listdir(main_request_folder):
            if os.path.isdir(main_request_folder + file):
                other_request_folders.append(file)

        index = 0
        folder_name = self._handler_name + "_" + str(index + 1) + "_handler"
        self.__request_folder_name = folder_name

        while (other_request_folders.__contains__(folder_name) is True): #if somehow old request folder forgotten to be deleted!
            index += 1
            folder_name = self._handler_name + "_" + str(index + 1) + "_handler"

        my_request_folder_path = main_request_folder + folder_name
        os.makedirs( my_request_folder_path)
        return folder_name

    @trycatch
    def add_new_requests(self, new_requests):
        all_requests = self.get_requests()
        request_index = len(new_requests) - 1
        while request_index >= 0:
            request_to_add = new_requests[request_index]
            request_type = request_to_add.get_type()
            requests_of_type = all_requests.__getitem__(request_type)
            requests_of_type.append(request_to_add)
            all_requests.update({request_type: requests_of_type})
            request_index = request_index - 1
        return 0

    @trycatch
    def parse_requests(self, request_file):
        with(open(request_file, "r")) as request_file:
            request_list = []
            data = json.load(request_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                request = RequestInfo.json_to_instance(val)
                request_list.append(request)
            return request_list


    def eliminate_duplications(self, request_list):
        debug("process_request_list_call list lenght {:d}".format(int(len(request_list))))
        current_request = request_list[0]
        if (current_request == None):
            error("Error , no current request !")
            return

        type = current_request.get_type()
        request_list_size = len(request_list)
        user_feedback("Total {:d} {:s} request we have for now ".format(request_list_size, str(type)))

        if (str(type).__contains__("FETCH")):
            debug("will be elimination in the list")
            currency_list = []
            currency = current_request.get_symbol()
            eliminated_request_list = []
            while (current_request != None):
                if (currency_list.__contains__(currency) is not True):
                    eliminated_request_list.append(current_request)
                    currency_list.append(currency)
                else:
                    debug("{:s} fetch request eliminated!".format(str(currency)))

                if (len(request_list) > 0):
                    current_request = request_list.pop()
                    currency = current_request.get_symbol()
                else:
                    break
            debug("After elimination we have {:d}".format(int(len(eliminated_request_list))))
        else:
            user_feedback("No elimination for type {:s}".format(str(type)))
            eliminated_request_list = request_list  # do not eliminate other request type

        debug("After elimination we have {:d}".format(int(len(eliminated_request_list))))
        return eliminated_request_list

    @trycatch
    def start_requests(self,eliminated_request_list:tuple):
        request_handler = self.get_handler()
        try_limit = RequestHandlerService.MAX_FAIL_COUNT

        for current_request in eliminated_request_list:
            while try_limit > 0:
                try:
                    try_limit = try_limit - 1
                    self.set_handler_busy(True)
                    request_handler.handle_request(current_request)
                    try_limit = 0 # do not try cos no exception is occured?
                except Exception as e:
                    error(str("Error{:d} in request_handler: [{:s}]".format(int(RequestHandlerService.MAX_FAIL_COUNT - try_limit),str(e))))
                    if (try_limit == 0):
                        error("Request Handler {:s} closing itself due to too much error!".format(str(request_handler.get_name())))
                        request_handler.de_init()
                        self.report_request_caused_crash(current_request)
                finally:
                    self.set_handler_busy(False)


    def report_request_caused_crash(self,request:RequestInfo):
        pass #TODO: let manager know that this request couldn't be handled and let it decide what to do.

    def process_request_type(self,request_type:str):
        all_requests = self.get_requests()
        requests = all_requests.__getitem__(request_type)
        if (len(requests) > 0):
            all_requests.update({request_type: []})
            debug("handle  {:s} request".format(str(request_type)))
            eliminated_list = self.eliminate_duplications(requests)
            if len(eliminated_list)> 0:
                self.start_requests(eliminated_list)

    def process_all_requests(self): # requests ordered in order to their priority!
        all_request_types = self.get_requests().keys() #TODO: By this we don't take care of priority of requests. So solve this!
        for type in all_request_types:
            self.process_request_type(type)

    def observer_stop(self,observer):
        try:
            while(observer.event_queue.unfinished_tasks != 0):
                time.sleep(1)
            observer.unschedule_all()
            observer.stop()
            observer.join(2)
            user_feedback("Observer is stopped")
        except Exception as e:
            error("Error during stoping observer {:s}".format(str(e)))

    def start(self):
        cycle = 0
        observer = Observer()
        file_event_handler = FileEventHandler()
        file_event_handler.save_service(self)
        request_dir = self.get_request_folder_path()
        user_feedback("HELPER STARTED ON : {:s}".format(str(request_dir)))
        observer.schedule(file_event_handler, path=request_dir)
        observer.start()
        self.set_handler_health_status(True)
        self.set_handler_busy(False)
        try:
            while self.is_handler_healthy() == True:
                cycle = cycle + 1
                self.update_handler_cycle(cycle)
                if (cycle > RequestHandlerService.MAX_CYCLE):
                    user_feedback("Helper closing itself.")
                    self.set_handler_health_status(False)
                if self.is_handler_busy() == True:
                    debug("Helper is busy!")
                    time.sleep(1)
                    continue
                else:
                    user_feedback("waiting cycle {:d}!".format(int(cycle)))
                    self.process_all_requests()
                    time.sleep(1)

        except KeyboardInterrupt:
            self.observer_stop(observer)
            shutil.rmtree(self.get_request_folder_path())

        self.observer_stop(observer)
        shutil.rmtree(self.get_request_folder_path())


'''
handler_service  = RequestHandlerService(KoineksRequestHandler,username="koineks.ozan@gmail.com",password="Ozandoruk1989",headless=True,driver_name="firefox")
handler_service.start()
'''