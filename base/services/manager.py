import firebase_admin
from firebase_admin import credentials
import os,sys,shutil,signal,time
import threading,subprocess
print("init_services of services module")

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
print("{:s} is added to sys paths".format(str(module_path)))
sys.path.append(module_path)

from api.server import test
from api.server.new_server import ApiService
from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine import symbols
from api.base.services.load_balancer import LoadBalancer
from base.crypto_engine.utils.market import Markets
from api.base.crypto_engine.utils.fcm import FCM

#from api.base.services.ob_service import OrderBookService

from api.base.crypto_engine.utils.config_manager import Config

ApiServiceCheckedTmsp = None
ManagerHealth = False
class Manager():

    started_service = {}
    MANAGER_FILE_PATH = os.path.abspath(__file__)

    @staticmethod
    def destructor(a,b):
        services = Manager.started_service.keys()
        for service in services:
            user_feedback("TODO: {:s} service should be closed!".format(str(service)))
        exit(0)

    def __init__(self, health_monitor_path:str, debug_mode_enabled:bool=False):
        try:
            self._debug_mode_enabled = debug_mode_enabled
            self._health_monitor_path = health_monitor_path
            current_t = threading.currentThread()
            threading.Thread.setName(current_t, "Manager")
        except Exception as e:
            print("error during setting thread name : {:s}".format(str(e)))

        user_feedback("Manager started with health path {:s}".format(str(self._health_monitor_path)))
        signal.signal(signal.SIGTERM, self.destructor)
        signal.signal(signal.SIGINT, self.destructor)
        self.app_info = Config.get_manager_config()
        log_to_file = self.app_info.get_log_to_file_enabled()
        symbols.LOG_TO_FILE_ENABLED = log_to_file
        Debug.set_debug_level_file("manager.config")
        debug_level = self.app_info.get_manager_debug_level()
        try:
            Debug.set_debug_level(debug_level)
        except Exception as e:
            error("Wrong debug level given error is {:s}".format(str(e)))
            Debug.set_debug_level("user_feedback") #default


        Manager.started_service = {}
        Config.set_config_folder(symbols.MARKET_AND_EXCHANGE_CONFIG_DIR)

    def init(self):
        self.__init__()
        return self


    @staticmethod
    def start_process(port,pk):
        server_process = subprocess.Popen(["python3", Manager.MANAGER_FILE_PATH, str(port), pk])
        user_feedback("New Server is started with pid {:d}".format(int(server_process.pid)))
        return server_process


    def write_health_info(self,info:str):
        try:
            with open(self._health_monitor_path,"w") as manager_health_file:
                manager_health_file.write(info)
        except Exception as e:
            error("Exception during writing manager health info {:s}".format(str(e)))

    def check_api_monitor_health(self):
        global ApiServiceCheckedTmsp
        global ManagerHealth
        healthy = True
        while True:
            debug("checking manager health status..")
            time.sleep(5)
            now = time.time()
            if ManagerHealth == False :
                error("ManagerHealth is set to False. Re-starting")
                healthy = False                             
            if ManagerHealth == False or (ApiServiceCheckedTmsp != None and now - ApiServiceCheckedTmsp > 300): #more than 60 sec
                error("Manager is not responding.. Manager should be re-started....")
                healthy = False                 
            if healthy is not True:
                self.write_health_info("death")
                Manager.destructor(None,None)
            else:
                print("Manager is  alive")



    def clear_folder(self,path:str):
        try:
            if (os.path.exists(path) is True):
                shutil.rmtree(path)
            os.makedirs(path)
            user_feedback("{:s} is cleared".format(str(path)))
        except Exception as e:
            error("Error during clearing folder {:s}".format(str(e)))

    def clear_garbages(self):
        self.clear_folder(symbols.MAIN_REQUEST_FOLDER)
        self.clear_folder(symbols.SIMULATOR_REQUEST_DIR)
        self.clear_folder(symbols.TABLE_REQUEST_DIR)
        self.clear_folder(symbols.REQUEST_HANDLER_SERVICE_DIR)
        self.clear_folder(symbols.NEW_TABLE_DIR)
        self.clear_folder(symbols.MAIN_REQUEST_FOLDER)
        self.clear_folder(symbols.OPPORTUNITY_DIR)
        self.clear_folder(symbols.HTTP_SERVICE_REQUEST_DIR)
        user_feedback("ALL GARBAGES ARE CLEARED")

    def find_activated_markets(self, arbitrage_file_names):
        try:
            activated_markets = []
            for enabled_arbitrage_name in arbitrage_file_names:
                active_arbitrage = Config.get_arbitrage_from_file(enabled_arbitrage_name)
                arbitrage_keys = active_arbitrage.keys()
                for key in arbitrage_keys:
                    first_market = str(key).split("/")[0]
                    second_market = str(key).split("/")[1]
                    if(activated_markets.__contains__(first_market) != True):
                        activated_markets.append(first_market)
                    if (activated_markets.__contains__(second_market) != True):
                        activated_markets.append(second_market)
            return activated_markets
        except Exception as e:
            error("Error during finding activated markets {:s}".format(str(e)))
            raise e
        
    def init_fcm(self):
        try:
            cred = credentials.Certificate(symbols.FCM_KEY_PATH)
            firebase_admin.initialize_app(cred)
        except Exception as e:
            error("Error during init fcm: {:s} ".format(str(e)))
        

    def start(self):
        global ApiServiceCheckedTmsp
        global ManagerHealth
        ManagerHealth = True
        app_info = self.app_info
        self.clear_garbages()
        self.write_health_info("alive")
        self.init_fcm()
        
        markets = Config.get_markets_from_config()
        exchanges = Config.get_exchange_from_config()
        statistic_service_enabled = app_info.get_statistis_service_enabled()
        api_service_enabled = app_info.get_api_service_enabled()
        op_finder_enabled = app_info.get_op_finder_enabled()
        #ob_service_enabled = app_info.get_ob_service_enabled() #TODO: implement ittrue
        arbitrage_file_count = app_info.get_arbitrage_file_count()
        koineks_handler_count = app_info.get_koineks_handler_count()
        btcturk_handler_count = app_info.get_btcturk_handler_count()
        if (arbitrage_file_count <= 0 and op_finder_enabled):
            raise Exception("No given Arbitrage Config file name")
        arbitrage_file_names = app_info.get_arbitrage_files() if op_finder_enabled else []
        koineks_cryptos_to_watch = []
        atleast_one_arbitrage = False
        for arbitrage_file in arbitrage_file_names:
            arbitrages = Config.get_arbitrage_from_file(arbitrage_file)
            arbitrage_keys = arbitrages.keys()
            for arbitrage_name in arbitrage_keys:
                arbitrage = arbitrages.__getitem__(arbitrage_name)
                if arbitrage.get_active() == False:
                    debug("Arbitrage {:s} is disabled".format(str(arbitrage_name)))
                    continue  # skip if the arbitrage is not activated
                atleast_one_arbitrage = True
                buy_market = arbitrage.get_market_low().get_name()
                sell_market = arbitrage.get_market_high().get_name()
                symbol = str(arbitrage.get_symbol()).lower()
                if (str(buy_market).lower() == "koineks" or str(sell_market).lower() == "koineks"):
                    if (koineks_cryptos_to_watch.__contains__(symbol) is not True):
                        koineks_cryptos_to_watch.append(symbol)  # add these symbols for koineks_ob handler!

        if (atleast_one_arbitrage is not True and op_finder_enabled):
            raise Exception(
                "No arbitrage is enabled in given arbitrage(s) file{:s}, why I'm supposed to run then for op_finder?".format(
                    str(arbitrage_file_names)))

        koineks_acc = app_info.get_koineks_acc()
        koineks_pass = app_info.get_koineks_password()
        simulator_enabled = app_info.get_simulator_enabled()
        table_service_enabled = app_info.get_table_service_enabled()
        koineks_ob_service_enabled = app_info.get_koineks_ob_enabled()
        ob_fresh_guy_enabled = app_info.get_ob_fresh_guy_enabled()
        arbitrage_enabled = app_info.get_arbitrage_enabled()
        if (op_finder_enabled is not True):
            if arbitrage_enabled:
                raise Exception("I can't do arbitrage without op_finder enabled!")
            if simulator_enabled:
                raise Exception("Why I need to run simulator without op_finder ?")

        if (koineks_ob_service_enabled is False):
            symbols.LOCAL_ORDERBOOK_SUPPORT = False
        else:
            symbols.LOCAL_ORDERBOOK_SUPPORT = True


        #START API_SERVICE
        if api_service_enabled:
            threaded_mode_open = True if self._debug_mode_enabled else False            
            port = app_info.get_api_service_port()
            pk = app_info.get_api_service_pk()
            current_server_pid = ApiService.start_process(port, pk, threaded_mode_open)
            #server_process = subprocess.Popen(["python3.6",api_service_path,str(port),pk])
            #api_service = ApiService(port, pk) #TODO: fetch limited time data from config
            #service_thread = api_service.start_service()
            #Manager.started_service.update({service_thread.getName():service_thread})
            
        #START ORDER BOOK FETCHER SERVICES
        
        time.sleep(3) # wait for api service get up!
        
        if op_finder_enabled: #if op_finder_enabled we will need order book fetcher services..

            from api.base.services.ob_service import OrderBookService
            activated_markets = self.find_activated_markets(arbitrage_file_names)            
            for market in activated_markets:
                ob_service = OrderBookService(market,8)
                ob_service_thread = ob_service.start_service()
                Manager.started_service.update({ob_service_thread.getName():ob_service_thread})

        #START LoadBalaner Service
        if koineks_handler_count + btcturk_handler_count > 0:
            load_balancer = LoadBalancer()
            service_thread = load_balancer.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})

            
        if (simulator_enabled):
            # START SIMULATOR_SERVICE
            import api.base.services.simulator_service
            simulator_service = api.base.services.simulator_service.SimulatorService()
            service_thread = simulator_service.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})

        if (table_service_enabled):
            # START TABLE_SERVICE        
            import api.base.services.table_service
            table_service = api.base.services.table_service.TableService(symbols.TABLE_REQUEST_DIR, ["*.request"])
            service_thread = table_service.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})

        if (table_service_enabled):#TODO: Make it statistic_table_service_enabled..(ofc with needed changes)
            # START STATISTIC_TABLE_SERVICE
            import api.base.services.statistic_table_service
            statistic_table_service = api.base.services.statistic_table_service.StatisticTableService(symbols.STATISTIC_TABLE_REQUEST_DIR, ["*.request"])
            service_thread = statistic_table_service.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})

        if (koineks_ob_service_enabled):
            # START KOINEKS OB FETCHER
            is_ob_headless = app_info.get_koineks_ob_headless()
            ob_driver_name = app_info.get_koineks_ob_driver_name()
            min_cycle_time = app_info.get_koineks_ob_min_cycle_time()
            import api.base.services.order_book_fetcher_service
            from api.base.crypto_engine.browser.koineks_browser import KoineksBrowser
            started_services = api.base.services.order_book_fetcher_service.OrderBookFetcherService.start_fetcher_sub_services(
                koineks_cryptos_to_watch,
                KoineksBrowser, browser_driver=ob_driver_name, headless= is_ob_headless,
                # firefox,driver in headless mode(true) ,
                min_cycle_time=min_cycle_time, acc=koineks_acc, password=koineks_pass)
            Manager.started_service.update(started_services)
            services_ready = api.base.services.order_book_fetcher_service.OrderBookFetcherService.is_all_services_are_ready()
            while (services_ready is not True):
                user_feedback("ob_fetcher_services are not read yet!")
                time.sleep(10)
                services_ready = api.base.services.order_book_fetcher_service.OrderBookFetcherService.is_all_services_are_ready()


        if (koineks_handler_count > 0):# which means koineks_handler is enabled 
            # START KOINEKS HANDLER
            from api.base.services.request_handler_service import RequestHandlerService
            from api.base.crypto_engine.request_handler.koineks_handler import KoineksRequestHandler
            started_handler_count = 0
            driver_name = app_info.get_koineks_handler_driver_name()
            is_headless = app_info.get_koineks_handler_headless()
            while (started_handler_count < koineks_handler_count):
                handler_service = RequestHandlerService(KoineksRequestHandler, username=koineks_acc,
                                                        password=koineks_pass, headless=is_headless,
                                                        driver_name=driver_name)
                service_thread = handler_service.start_service()  # Starts I_watchable_service with infinitve loop
                Manager.started_service.update({service_thread.getName():service_thread})
                started_handler_count += 1

        # START OB(KOINEKS) FRESHER GUARDIAN
        if (ob_fresh_guy_enabled):  # if there is no handler , fresh guarding can't do anything
            if (started_handler_count < 1 ):
                raise Exception("So ob_fresh_guy will just find old values but not be able to update them cos no handler is avaiable to handle request from fresh guy?")

            import api.base.services.ob_fresh_guard_service
            fresh_guard_service = api.base.services.ob_fresh_guard_service.OB_Fresh_Guard_Service("koineks",
                                                                                                  koineks_cryptos_to_watch)
            service_thread = fresh_guard_service.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})
        
        if op_finder_enabled:
        # START OP_FINDER_SERVICE                      
            import api.base.services.op_finder_service
            for name in arbitrage_file_names:
                op_finder_service = api.base.services.op_finder_service.OPFinderService(name, markets, exchanges)
                service_thread = op_finder_service.start_service()
                Manager.started_service.update({service_thread.getName(): service_thread})
        #START STATISTIC SERVICE
        if statistic_service_enabled is True:
            import api.base.services.StatisticService
            time.sleep(20) ## ALOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO #TODO KALDIR AMK BUNU BİR ŞEKİLDE ?:
            StatisticService = api.base.services.StatisticService.StatisticService(symbols.STATISTIC_REQUEST_DIR, ["*.request"])
            service_thread = StatisticService.start_service()
            Manager.started_service.update({service_thread.getName():service_thread})
        started_services = Manager.started_service.keys()
        #START MANAGER HEALTH MONITOR SERVICE
        service_thread = threading.Thread(target = self.check_api_monitor_health, name = "ManagerMonitor")
        service_thread.start()
        Manager.started_service.update({service_thread.getName():service_thread})
        
        for service in started_services:
            user_feedback("{:s}  is started".format(str(service)))
            print("{:s}  is started".format(str(service)))
        if (self._debug_mode_enabled):
            user_feedback("###  Manager is started in debug mode!! ##")
        else:
            user_feedback("### Manager is started normally !! ###")

            

        
        if api_service_enabled:
            restarted_count = 0
            first_api_start_time = time.time()
            last_api_restart_time = first_api_start_time
            while True:
                time.sleep(30)
                penetration_result = ApiService.do_penetration() #returns False in case of fail or passed count in case of success as return val.
                ApiServiceCheckedTmsp = time.time()
                last_api_age = (time.time() - last_api_restart_time) / 3600  #3600 converts secs to hour
                if (penetration_result is False):
                    user_feedback("Http Server{:d} is not responding,re-start it.".format(int(current_server_pid)),False,True)
                    try:
                        current_server_pid = ApiService.do_fixing(port, pk, current_server_pid)
                        last_api_restart_time = time.time()
                        restarted_count += 1
                        now = time.time()
                        avg = ((now - first_api_start_time) / restarted_count) / 3600 # 360 converts secs to hour.                        
                        user_feedback("Api Stability Info: Avg:{:0.2f} Hour Restarted Count:{:d} Last Api Age {:0.2f} Hour"
                                      .format(float(avg), restarted_count, last_api_age))
                    except Exception as e:
                        error("Manager handled exception during Server Fixing. Lets start from BEGIN?")
                        ManagerHealth = False
                else:
                    user_feedback("Api is working for {:0.2f} hour and has passed penetration test at phase {:d}".
                                  format(float(last_api_age),int(penetration_result)),truncated_free=False, print_time=False)





if __name__ == "__main__":    
    try:
        current_t = threading.currentThread()
        threading.Thread.setName(current_t, "Manager")
    except Exception as e:
        print("error during setting thread name : {:s}".format(str(e)))
    
    if(len(sys.argv) < 3):
        error("Only %d parameter is given expected is 3(self, manager_health_path, debug_mode_is_enabled)" % len(sys.argv))
        exit(-1)
    try:
        debug_mode = False
        if str(sys.argv[2]) == "True":
            debug_mode = True
            error("##### Debug Mode Enabled! ####")
        else:
            error("#### Debug Mode is Disabled ####")
        health_file_path = str(sys.argv[1])
        print("ManagerMonitorHealth Path is {:s}".format(str(health_file_path)))
        manager = Manager(health_file_path, debug_mode)
        manager.start()
    except Exception as e:
        error("WTF on Manager Main Start: {:s}".format(str(e)))
        print("WTF on Manager Main Start: {:s}".format(str(e)))
        
        
   
#Starter bash script..     
'''
#!/bin/sh
PID=$$
home=$(pwd)
script=$home"/start.sh"
direct=""
started=0
manager_file=$home"/api/base/services/manager.py"
while true;
do
	log_file=$home"/log.txt"
	manager_health=$home"/manager_health.txt"
	direct=">> "$log_file" 2>&1"
	command="python3.5 "$manager_file" "$manager_health" "$direct
	echo $command
	echo "before start wait 5 sec"
	sleep 5
	eval "($command) &"
	started=$((started + 1))
	manager_pid=$!
	echo "manager pid is "$manager_pid
	ps aux|grep python3.5
	while true;
	do
		echo "Reading Manager Health"
		sleep 5
		line=$(cat $manager_health)
		echo "Fucking Line is "$line
		if [ "death" = "$line" ]; then
				echo "String are death"
				./kill_debug.sh
				sleep 2
				break
		else
				echo "Strings are alive"
		fi
	done

done


'''