import threading
from api.base.crypto_engine.MessageApi.debug import *
'''
#This is a Interface-Abstraction class hybrid class.
#Service classes should inherit from this class and must implement start and init functions
int start function , service class Must implement it's routine function.
in init function service class Must implement it's constructor that Must return it self.
So with IWatchAbleService you may implement your servce without taking care of the situations that your service has stopped. Watchable service will re-start your service

'''
class IWatchableService:
    INFINITE = -1 # every time when thread deads , re-start it.

    def __init__(self,name:str,max_restart_count:int = -1):
        self.__instance_obj = self
        self.__start_op = getattr(self,"start",None)
        self.__instance_constructor = getattr(self,"init",None)
        if self.__instance_constructor == None or callable(self.__instance_constructor) != True:
            raise NotImplemented("Child of WatchableServiec must implement init function! And implement necesarry setup there cause we will have to create a new instance with new thread!")

        if self.__start_op == None or callable(self.__start_op) != True:
            raise NotImplemented("Child of WatchableServiec must implement start function!")
        self.__name = name
        self.__restarted_count  = 0
        self.__max_restart_count = max_restart_count

    def _run(self): # if -1 , re-start dead thread for forever.

        while self.__restarted_count < self.__max_restart_count or self.__max_restart_count < 0:
            if (self.__restarted_count != 0):
                new_obj = self.__instance_constructor()
                self.__instance_obj = new_obj
            self.__current_thread = threading.Thread(target = self.__instance_obj.start , name = self.__name)
            self.__restarted_count += 1
            self.__current_thread.start()
            self.__current_thread.join()


    def start_service(self):
        service_starter_thread_name = self.__name + "_starter_thread"
        run_thread = threading.Thread(target=self._run, name = service_starter_thread_name)
        run_thread.start()
        user_feedback("{:s} is started".format(str(self.__name)),False,True)
        return run_thread