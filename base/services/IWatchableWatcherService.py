from third_party.watchdog.observers import Observer
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from base.services.i_watchable_service import IWatchableService
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils import helper
from base.crypto_engine import symbols

from pathlib import Path
import time


from api.third_party.watchdog.events import PatternMatchingEventHandler


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
    
    '''
    def _ignore_directories(self,arg):
        print("noluyor amk")
    '''
    
    def __init__(self,patterns,onModified:bool , onCreated:bool,threadName: str):
        patterns = patterns
        self._onModifiedEnabled = onModified
        self._onCreatedEnabled = onCreated
        self.thread_name = threadName + "_FileEventHandler"
        self.__related_service_instance = None
        super().__init__(patterns,ignore_directories=False,case_sensitive=False)

    def save_service(self,service_instance):
        self.__related_service_instance  = service_instance
        self.lock_required = service_instance.get_lock_required()
        if self.lock_required:
            debug("Observer service instance required locking folder!")
        else:
            debug("Observer service instance  NOT required locking folder!")

    def get_service_instance(self):
        return self.__related_service_instance
    
    def process(self, event):
        helper.set_current_thread_name(self.thread_name)
        debug("FileEventHandler processing for {:s} started ".format(str(event.src_path)))
        try:          
            file_name = event.src_path.split("/")[-1]
            file_folder = event.src_path.split(file_name)[0]
            folder_locked = None
            if self.lock_required:
                folder_locked = helper.try_lock_folder(file_folder)
                if folder_locked:
                    debug("{:s} is locked ".format(str(file_folder)))
            else:
                folder_locked = True
            if (folder_locked):
                debug("Folder{:s} locked for parsing {:s}".format(str(file_folder),str(event.src_path)))
                service_instance = self.get_service_instance()
                new_requests = service_instance.parser(event.src_path)
                if new_requests is not None:
                    service_instance = self.get_service_instance()
                    service_instance.add_new_requests(new_requests)
                else:
                    error("Parse Error no new request is parsed? ")

                #os.remove(event.src_path)
                #user_feedback("{:s} proessed and  removed".format(str(event.src_path)))
            else:
                raise Exception("Could not lock folder {:s}".format(str(file_folder)))
        except Exception as e:
            error("Table Service : File Event Handler: Error during parsing: {:s}".format(str(e)))
        finally:
            try:
                if self.lock_required and folder_locked:
                    ret = helper.release_folder_lock_if_any(file_folder)
                    if ret:
                        debug("We release folder lock of {:s}".format(str(file_folder)))
            except Exception as e:
                error("Error during releasing lock for folder {:s} Error:{:s}".format(str(file_folder),str(e)))

    def on_modified(self, event):
        if self._onModifiedEnabled and event.is_directory is not True and event.src_path.endswith(".lock") is not True:
            self.process(event)

    def on_created(self, event):
        if self._onCreatedEnabled and event.is_directory is not True and event.src_path.endswith(".lock") is not True:
            self.process(event)



class IWatchableWatcherService(IWatchableService):

    def __init__(self, patterns:list, path_to_watch:str, action_interval:int=1, onModified:bool = True, onCreated:bool = True,folderLockRequired:bool=False):
        if (patterns == None or len(patterns) == 0):
            raise Exception("File Extensions of file must be given")
        if (path_to_watch == None or len(path_to_watch) == 0):
            raise Exception("PATH must be given that will be watched")


        self.parser = getattr(self, "parse_file", None)
        if self.parser == None or callable(self.parser) != True:
            raise NotImplemented("Watcher  must implement parse function!")

        self.__action = getattr(self, "action",None)
        if self.__action == None or callable(self.__action) != True:
            raise NotImplemented("Action func must be implemented that process requests!")

        self._class_name =  self.__class__.__name__
        self.action_interval = action_interval
        self.__requests = []
        self.__requests.append(self._class_name)
        self.patterns = patterns
        self.folder_lock_required = folderLockRequired
        self.path_to_watch = path_to_watch
        self._onModifiedEnabled = onModified
        self._onCreatedEnabled = onCreated
        super().__init__(self._class_name ,-1)

    def get_lock_required(self):
        return self.folder_lock_required

    def init(self):
        self.__init__(self.patterns, self.path_to_watch)
        return self

    def get_requests(self):
        return self.__requests

    def get_target_path(self):
        return self.path_to_watch


    @trycatch
    def add_new_requests(self, new_requests):       
        all_requests = self.get_requests()
        all_requests.append(new_requests)

    
    def process_all_requests(self): # requests ordered in order to their priority!
        all_request = self.get_requests()
        if(len(all_request) < 1):
            raise Exception("There must be the name of the service as a mark for request list")
        try:
            debug("{:d} request are ready to be processed".format(int(len(all_request))))
            for request in all_request:
                if ( type(request) == type("string")):
                    continue
                if (request == None):
                    error("WTF? request can't be NONE?")
                else:
                    try:
                        self.__action(request)
                    except Exception as e:
                        error("Unhandled Exception caught during execution __action function.. ErrMsg: {:s}".format(str(e)))
                        
                    all_request.remove(request)
            #all_request.clear() #TODO: Be sure remove func is worked..
            debug("Request are cleared")
        except Exception as e:
            error("Error during processing requests E: {:s}".format(str(e)))


    def check_path(self, path):
        try:
            if not os.path.exists(path):
                parent_folder = str(Path(path).parent)
                self.check_path(parent_folder)
                error("[paths] {:s} doesn't exist: creating...".format(path))
                os.mkdir(path)
            return path
        except Exception as e:
            error("Error during checking path {:s} Error:{:s}".format(str(path),str(e)) )

    def start(self):
        observer = Observer()
        file_event_handler = FileEventHandler(self.patterns, onModified=self._onModifiedEnabled, onCreated=self._onCreatedEnabled, threadName=self._class_name)
        file_event_handler.save_service(self)
        target_path = self.get_target_path()
        self.check_path(target_path)
        observer.schedule(file_event_handler, path=target_path)
        observer.start()
        try:
            while True:
                self.process_all_requests()
                time.sleep(self.action_interval)

        except KeyboardInterrupt:
            error("Table Service Observer stopped by KeyboardInterrupt ")
            observer.stop()
        except Exception as e:
            error("something you could not catch is fired dude err: {:s}".format(str(e)))
        observer.stop()
        error("Table Service Observer is stopped")