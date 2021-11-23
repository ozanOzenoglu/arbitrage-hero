import sys,os,threading,time,subprocess

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
sys.path.append(module_path)

from api.base.crypto_engine.utils import helper
from api.server import test
from api.server.http_server import handler, service
from api.server.library.db import DB
from api.base.services.i_watchable_service import IWatchableService
from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine.symbols import *

from api.server.library import user
PRIVATE_KEY = "osman_is_my_girl"
PORT_NUMBER = 8000
PUBLIC_PORT = 80
GIVE_UP_THRESHOLD = 10 # indicates number of try to fixing server before giving up for trying more..

class ApiService():
    FILE_PATH = os.path.abspath(__file__)
    def __init__(self,api_port,private_key):
        DB.init("localhost",6379,0)
        self._handler = handler.MyHandler
        self._private_key = private_key
        self._handler.PRIVATE_KEY = private_key
        self._api_port = api_port
        self._http_server = service.HttpServerService(self._handler,api_port)

    def init(self):
        self.__init__(self._api_port,self._private_key)
        return self
    
    def check_restart_request(self):
        if (os.path.exists(HTTP_SERVICE_SHUTDOWN_REQUEST)):
            try:
                os.remove(HTTP_SERVICE_SHUTDOWN_REQUEST)
            except Exception as e:
                error("Error during remove http server restart request {:s}".format(str(e)))
            return True
        else:
            return False

    def start(self):
        user.init_user()
        
        if (os.path.exists(HTTP_SERVICE_SHUTDOWN_REQUEST)):
            try:
                error("Found shutdown request while starting. IT must be forgotten to be deleted?")
                os.remove(HTTP_SERVICE_SHUTDOWN_REQUEST)
            except Exception as e:
                error("Error during remove http server restart request {:s}".format(str(e)))

        server_thread = threading.Thread(target=self._http_server.run_forever,name="http_server_starter_thread")
        server_thread.start()
        restarted_request = False
        while(restarted_request == False):
            time.sleep(1)
            restarted_request = self.check_restart_request()
        
        #self._http_server.run_forever()
        error("SERVICE IS CLOSING")
        self._http_server.stop()
        return

    @staticmethod
    def do_penetration():
        server_not_responded_count = 0
        server_responding = test.is_api_service_working()
        while server_responding == False:
            server_not_responded_count = server_not_responded_count + 1
            if server_not_responded_count > 5:
                return False            
            time.sleep(server_not_responded_count)# wait incremented amount of time for each try.. 1, 2 , 3 ,4 ,5 (total 15secs..)
            server_responding = test.is_api_service_working()                
        return server_not_responded_count
        


    @staticmethod
    def restart(port, pk, pid_of_server):
        ApiService.shutdown("For re-starting", pid_of_server)
        time.sleep(2)
        server_pid = ApiService.start_process(port, pk)
        return server_pid
    
    @staticmethod
    def do_fixing(port, pk, pid_of_server):
        start = time.time()
        user_feedback("Fixing HttpServer{:d}..".format(int(pid_of_server)))
        http_server_restart_try = 0
        server_responding = False
        while server_responding == False:
            http_server_restart_try = http_server_restart_try + 1
            if http_server_restart_try > GIVE_UP_THRESHOLD:
                raise Exception("We failed at fixing http server") #manager catch it, because we all completely failed now.. Manager will re-start everything..
            try:
                new_server_pid = ApiService.restart(port, pk, pid_of_server)
                phase = ApiService.do_penetration()
                if phase == False:
                    raise Exception("Server penetration test is failed!") # we catch it in do_fixing..
                server_responding = True
                end = time.time()
                diff = end - start
                user_feedback("Fixing HttpServer is succsessful in {:d} secs Penetration Passed Phase:{:d}  New Server pid:{:d}".format(int(diff), int(phase), int(new_server_pid)))         
                return new_server_pid
            except Exception as e:
                error("We couldn't fix http server at try {:d} ExceptionMsg:{:s}".format(int(http_server_restart_try),str(e) ))




    @staticmethod
    def find_pid():
        p = os.popen("ps aux |grep [n]ew_server")
        ret = p.read().split(" ")
        for result in ret:
            try:
                pid = int(result)
                return pid
            except Exception as e:
                pass
        

    @staticmethod
    def kill_server(pid:int):
        user_feedback("Killing server with pid {:d}".format(int(pid)))
        cmd = "kill -9 {:d}".format(int(pid))
        kill_cmd = os.popen(cmd)
        ret = kill_cmd.read()
        
        



    @staticmethod
    def shutdown(reason:str, pid_of_server:int):
        user_feedback("HttpServer{:d} Shutdown Request Reason: {:s}".format(int(pid_of_server), str(reason)))
        try:
            #pid = ApiService.find_pid() # Not portable solution!
            pid = pid_of_server
            with open(HTTP_SERVICE_SHUTDOWN_REQUEST,"w"):
                pass
            time.sleep(2) #let server to see the shutdown request before killing it
            ApiService.kill_server(pid)
            return True
        except Exception as e:
            error("Error during creating HttpServer Shutdown Request Creation {:s}".format(str(e)))
            return False

    @staticmethod
    def start_process(port, pk, threaded:bool=False):
        if threaded == False:
            server_process = subprocess.Popen(["python3", ApiService.FILE_PATH, str(port), pk])
            return server_process.pid
        else:
            ApiService.run(port, pk)
    
    @staticmethod
    def run(port, pk):   
        try:
            if(os.path.exists(HTTP_SERVICE_DIR)is not True):
                os.mkdir(HTTP_SERVICE_DIR)
                user_feedback("HTTP_SERVICE_DIR is created")
            if(os.path.exists(HTTP_SERVICE_REQUEST_DIR) is not True):
                os.mkdir(HTTP_SERVICE_REQUEST_DIR)
                user_feedback("HTTP_SERVICE_REQUEST_DIR is created")
        except Exception as e:
            error("Error during creating request dir {:s}".format(str(e)))
            exit(-1)
        
        service = ApiService(port,"osman_is_my_girl")
        try:
            service_starter_thread = threading.Thread(target=service.start,name="ServerStarterThread")
            service_starter_thread.start()
            user_feedback("Server is started on a thread!")
            
        except Exception as e:
            error("Error during service start: {:s}".format((str(e))))
            exit(-1)

        user_feedback("Server is closed normally.")
    
    
if __name__ == "__main__":
    helper.set_current_thread_name("HTTP_SERVER_MAINPROCESS_THREAD")
    port = 0
    pk = ""
    if(len(sys.argv) < 3):
        error("Port and Private Key should be given in order")
        exit(-1)
    try:
        port = int(sys.argv[1])
        pk = str(sys.argv[2])
    except Exception as e:
        error("Error during parsing arguments {:s}".format(str(e)))
    
    try:
        if(os.path.exists(HTTP_SERVICE_DIR)is not True):
            os.mkdir(HTTP_SERVICE_DIR)
            user_feedback("HTTP_SERVICE_DIR is created")
        if(os.path.exists(HTTP_SERVICE_REQUEST_DIR) is not True):
            os.mkdir(HTTP_SERVICE_REQUEST_DIR)
            user_feedback("HTTP_SERVICE_REQUEST_DIR is created")
    except Exception as e:
        error("Error during creating request dir {:s}".format(str(e)))
        exit(-1)
    
    user_feedback("Server is started as separeted process!")
    service = ApiService(8000,"osman_is_my_girl")
    try:
        service.start()
    except Exception as e:
        error("Error during service start: {:s}".format((str(e))))
        exit(-1)

    user_feedback("Server is closed normally.")