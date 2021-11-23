import os, requests, sys, threading , multiprocessing

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
'''
selenium_driver_path = module_path + "api/selenium_drivers/"
geckod_driver_path = selenium_driver_path + "geckodriver"
phantomjs_driver_path = selenium_driver_path + "phantomjs"
drivers = {'firefox': geckod_driver_path, 'phantomjs': phantomjs_driver_path}
'''

module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
sys.path.append(module_path)

'''

selenium_driver_path = module_path + "api/selenium_drivers/"
geckod_driver_path = selenium_driver_path + "geckodriver"
phantomjs_driver_path = selenium_driver_path + "phantomjs"
print("{:s} is added to sys paths".format(str(module_path)))

sys.path.append(selenium_driver_path)
sys.path.append(geckod_driver_path)
sys.path.append(phantomjs_driver_path)

'''
from api.base.crypto_engine import symbols
from api.base.crypto_engine.MessageApi.debug import Debug as Debug
import time
import datetime
import os
import json
from sys import argv
import subprocess

from base.crypto_engine.browser.browser import MainBrowser
from base.crypto_engine.utils import helper
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils.mail import KoineksMail
from api.base.crypto_engine import symbols
from enum import Enum
from base.services.i_watchable_service import IWatchableService

import unicodedata

import signal


class LoginErrors(Enum):
    RE_LOGIN = "NEED TO RE LOGIN"
    TRY_AGAIN = "TRY AGAIN"
    NEED_TO_WAIT = "NEED TO WAIT"
    WRONG_SMS_CODE = "WRONG SMS CODE"
    WEIRD_CONDITION = "WEIRD CONDITION"


def finder(method):
    def findit(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
            if result == None or len(result) == 0:
                return None
        except Exception as e:
            error("Finder Error: {:s} -> {:s}".format(str(e)))

        return result

    return findit


def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__),str(e)))

        return result

    return catched


def timeit(method):
    def timed(*args, **kw):
        ts = time.time()

        result = method(*args, **kw)

        te = time.time()

        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            user_feedback('%r  %2.2f ms' % \
                  (method.__name__, (te - ts) * 1000))
        return result

    return timed

#service related changeable vars starts
WAIT_SIBLINGS_TIMEOUT_SEC = 60
MAX_CYCLE_COUNT = 1000
MAX_STOP_REQUEST = 4  # when stop requests reaches this limit, stop the service.
SERVICE_RELIABLE_COUNT = 3  # when service run under
MAX_ERROR_COUNT = 10  # This is limit of exceptions count that occures in get_order_book . If order_book can't complete itself without reaching this count , We're closing service.
#service related changeable vars finishes

STARTED_DRIVER_PIDS = []
STARTED_DRIVER_PID_LOCK = threading.Lock()
LAST_SERVICE_LOGGED = None
STABILITY_TEST_COUNT = 0 # how many time we had to do stability test.
PROGRAM_START_TIME = 0
DEFAULT_STABILITY_TEST_COUNT = 5 # how many time we get order books to calculate avg order_book fetch time
LIVE_SIBLINGS_COUNT = 0 # Every started KoineksServiceNG thread will increase this count by one
LIVE_SIBLINGS_COUNT_LOCK = threading.Lock()
STABILITY_BARRIER_LOCK = threading.Lock()
STAIBLITY_TEST_SEM = threading.Semaphore(1) # with 1 , it's same as Lock . but you can increase the number to run test simustanely to see how perform threads when they work at the same time
STABILITY_BARRIER = None
DO_STABILITY_TEST = False
USE_THREAD_SCORE = False
STATIC_THREAD_COUNT = 0
MAX_RUNNUNG_THREAD_LOCK = threading.Lock()
MAX_RUNNING_THREAD_NUM = 0 # Don't allow no thread start before it's set by first thread. First thread will set it when all thread are ready to start..
KOINEKS_SERVICVES_ALL_READY = False
MAX_RUNNING_THREAD_SEM = threading.Semaphore(MAX_RUNNING_THREAD_NUM)
WORST_THREAD = None
PERFORMANCE_ADJUST_COMPLETED = None
NEED_TO_WAIT_ADJUST_COMPLETE = False
SLOW_THREADS_LOCK = threading.Lock()
SLOW_THREADS = {} # In this dict , we store slow threads and decide to close only one of them at a one time.
LAST_STABILITY_TEST_TIME = 0 # Here , we store the timestamp of last stability test
EXPECTED_SIBLINGS_COUNT = 0 # how many siblings are expected to be started ?
ALL_SIBLINGS_STARTED = None
READY_TO_START = False
READY_TO_START_TEST = None # barrier..
OPTIMAL_CYCLE_TIME = 1000  #Optimum cycle time will be calculated by first thread and used as a threshold for waiting  threads to finish their tests
CPU_CORE = 0
FIRST_START = True
MIN_CYCLE_TIME = 1000 # this is the minumum cycle time before start next cycle to be passed.

class OrderBookFetcherService(IWatchableService):
    if (symbols.GET_SMS_FROM_SERVER_ENABLED):
        user_feedback("get sms from server is enabled")
        FIRST_SMS_CODE_WAIT_TIME = 5  # this is the first amount of time we will wait before trying to fetch sms_code
    else:
        FIRST_SMS_CODE_WAIT_TIME = 10

    OB_EXPIRATION_LIMIT = 20  #
    TRY_AGAIN_WAIT_TIME = 50




    def __init__(self, username: str, password: str, driver_name,browser_class:MainBrowser,currency:str,max_restart_count:int=-1,headless_browser=False):
        global STARTED_DRIVER_PIDS
        global STARTED_DRIVER_PID_LOCK
        try:
            market_name = str(browser_class).split('.')[-1].split("Browser")[0].lower()
            self.__service_name = market_name +":" + currency + "_fetcher_service"
        except Exception as e:
            self.__service_name = currency + "_fetcher_service"

        super().__init__(self.__service_name, max_restart_count)  # Watchable Service instructor
        self.__browser_class = browser_class
        self._working_currency = currency
        self.__driver_score = 0 # This is the driver score that is re-calculated on every cycle about the driver speed and performance..
        self.__service_max_restart_count = max_restart_count
        self._driver_name = driver_name
        self._ORDER_BOOK = {}
        self.__user = username
        self.__pass = password
        self.__headles_browser = headless_browser
        self.__mail_service = KoineksMail("koineks.ozan@gmail.com", "Ozandoruk1989")
        self._browser = self.init_browser(self.__browser_class, headless_browser)
        self._driver = self._browser.get_driver()
        self.__driver_pid = self._browser.get_driver_pid()

        with STARTED_DRIVER_PID_LOCK:
            STARTED_DRIVER_PIDS.append(self.__driver_pid)

    #Get OrderBOOK RELATED FUNC START HERE
    def get_order_book(self, currency):
        return self.get_browser().fetch_order_book(currency)
    #Get OrderBOOK RELATED FUNC STOPs  HERE

    @timeit
    def login(self):
        return self.get_browser().login()

    @timeit
    def go_market(self,market:str):
        self.get_browser().go_to_market(market)

    def init_browser(self,browser_class:MainBrowser,headless_browser):
        return browser_class(self.__user,self.__pass,self._driver_name,headless_browser)

    def get_browser(self):
        return self._browser

    def get_order_book_dir(self):
        return symbols.ORDER_BOOK_DIR

    def get_orderbook_file_path(self):
        return symbols.KOINEKS_ORDER_BOOK_FILE

    def is_same(self, old: dict, new: dict):
        old_update_time = old.__getitem__('update_time')
        new_update_time = new.__getitem__('update_time')
        if (new_update_time - old_update_time > OrderBookFetcherService.OB_EXPIRATION_LIMIT * 1000):
            return False
        old_ask = old.__getitem__('asks')
        new_ask = new.__getitem__('asks')
        if (old_ask != new_ask):
            return True
        else:
            old_bid = old.__getitem__('bids')
            new_bid = new.__getitem__('bids')
            ret = (old_bid == new_bid)
            return ret

    def update_order_books_file(self):
        order_book_file_path = self.get_orderbook_file_path()
        if not os.path.exists(symbols.ORDER_BOOK_DIR):
            os.makedirs(symbols.ORDER_BOOK_DIR)
            error("ORDER_BOOK_DIR created first time? , is it new system?")

        with open(order_book_file_path, 'wb') as outputfile:
            byte_array = bytearray(json.dumps(self._ORDER_BOOK), 'utf8')
            outputfile.write(byte_array)

    def update_order_book_from_file(self):
        try:
            order_book_file_path = self.get_orderbook_file_path()
            with open(order_book_file_path, "r") as orderbook_file:
                self._ORDER_BOOK = json.loads(orderbook_file.read())
        except Exception as e:
            error("Error during updateing order book from file {:s}".format(str(e)))


    def update_order_book(self, currency: str, orderbook: dict):
        order_book_locked = helper.try_lock_folder(symbols.ORDER_BOOK_DIR, max_try_ms=500)  # try max 0.5 sec
        if (order_book_locked == True):
            try:
                self.update_order_book_from_file()
                time_stamp = int(round(time.time() * 1000))
                orderbook.update({'update_time': time_stamp})
                old_orderbook = self._ORDER_BOOK.pop(currency,
                                                     None)  # Delete the currency then update , this way ensure no duplication.
                #is_same = False if old_orderbook == None else (self.is_same(old_orderbook, orderbook))#we don't use is_same logic but in future can be used .

                self._ORDER_BOOK.update({currency: orderbook})  # on the fly
                try:
                    self.update_order_books_file()  # on the disk
                    order_book_file = self.get_orderbook_file_path()
                    helper.upload_order_book(order_book_file)
                except Exception as e:
                    error("Exception during writing to file".format((str(e))))
            except Exception as e:
                error("Error during updating order book {:s}".format(str(e)))
            finally:
                if (order_book_locked):
                    helper.release_folder_lock(symbols.ORDER_BOOK_DIR)
        else:
            error("Couldn't update to order_book , because we couldn't lock the folder")

    def kill_orphan_drivers(self):
        global STARTED_DRIVER_PID_LOCK
        global STARTED_DRIVER_PIDS
        working_drivers =  subprocess.check_output(["pidof",self._driver_name]).split()
        working_drivers = [driver.decode() for driver in working_drivers] # convert byte elements to str and create a new tuple from it. I <3 Python..

        orphan_drivers = []
        with STARTED_DRIVER_PID_LOCK:

            for driver in working_drivers:
                user_feedback("%s" % driver)
                if (STARTED_DRIVER_PIDS.__contains__(driver) is not True):
                    orphan_drivers.append(driver)

        for orphan_driver in orphan_drivers: # we assume no one else start selenium web drivers in the system , otehr wise this logic should be changes. it's just direct approach..
            user_feedback("Sent Orphan Driver SIGKILL  %s " % orphan_driver)
            try:
                os.kill(int(orphan_driver), signal.SIGKILL)
            except Exception as e:
                error("Error killing orphan driver {:s}".format(str(e)))


    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._browser.quit()
            self._driver.quit() # this is closing driver bin.. #TODO: do reserch if it works
        except Exception as e:
            error("Error exiting browser {:s}".format(str(e)))
        try:

            if (os.path.isfile("/proc/" + self.__driver_pid)):
                error("driver  {:s} is still alive , sigterm sending..".format(self.__driver_pid))
                os.kill(self.__driver_pid,signal.SIGTERM)
            if (os.path.isfile("/proc/" + self.__driver_pid)):
                error("driver  {:s} is still alive , sigkill sending..".format(self.__driver_pid))
                os.kill(self.__driver_pid, signal.SIGKILL)
            if (os.path.isfile("/proc/" + self.__driver_pid)):
                error("FATAL PERFORMANCE PROBLEM! FUCKING DRIVER IS STILL ALIVE ?")
                self.kill_orphan_drivers() #TODO: Experimantal ..
        except Exception as e:
            error("Error quiting driver {:s}".format(str(e)))
        try:
            helper.release_folder_lock_if_any(symbols.ORDER_BOOK_DIR)
        except Exception as e:
            error("Error releasing folder lock {:s}".format(str(e)))

        finally:
            user_feedback("Service is closing now ..")
            exit(0)

    def stop_service(self, reason: str = ""):
        user_feedback("Stop Service called")
        if reason != "":
            user_feedback("Reason: {:s}".format(str(reason)))
        with LIVE_SIBLINGS_COUNT_LOCK:
            global LIVE_SIBLINGS_COUNT
            LIVE_SIBLINGS_COUNT -= 1
            user_feedback("Live siblings are decreased , now {:d}".format(int(LIVE_SIBLINGS_COUNT)))
        self.__exit__(0, 0, 0)

    def get_max_cycle_time(self):  # every increased siblings will increase max_cycle_time..
        global LIVE_SIBLINGS_COUNT
        global OPTIMAL_CYCLE_TIME
        global MIN_CYCLE_TIME
        global MAX_RUNNING_THREAD_NUM
        time  = MIN_CYCLE_TIME * MAX_RUNNING_THREAD_NUM / LIVE_SIBLINGS_COUNT
        return time

    def do_performance_adjust(self):
        global SLOW_THREADS
        global LIVE_SIBLINGS_COUNT
        global WORST_THREAD
        global PERFORMANCE_ADJUST_COMPLETED
        global NEED_TO_WAIT_ADJUST_COMPLETE
        global MAX_RUNNING_THREAD_NUM
        global MAX_RUNNING_THREAD_SEM
        try:
            user_feedback("finding worst thread...")

            worst_avg_time = 0
            worst_thread = None
            for thread,thread_avg_time in SLOW_THREADS.items():
                user_feedback("{:s} avg_time:{:f}".format(str(thread),float(thread_avg_time)))
                if (thread_avg_time > worst_avg_time):
                    worst_thread = thread
                    worst_avg_time = thread_avg_time

            WORST_THREAD = worst_thread
            user_feedback("WORST THREAD IS {:s} with avg_time {:f}".format(str(WORST_THREAD), float(worst_avg_time)))
        except Exception as e:
            error("error do_performance_adjust {:s}".format(str(e)))
        finally:
            user_feedback("Worst Thread Founded released")
            PERFORMANCE_ADJUST_COMPLETED.set()
            NEED_TO_WAIT_ADJUST_COMPLETE = False
            time.sleep(1)
            PERFORMANCE_ADJUST_COMPLETED = None

    def calculate_program_stability_score(self):

        global STABILITY_TEST_COUNT
        global PROGRAM_START_TIME
        spent_time = time.time()  - PROGRAM_START_TIME
        program_score = (spent_time / STABILITY_TEST_COUNT) / 1000
        user_feedback('PROGRAM STABILITY SCORE IS {:f}'.format(float(program_score)))


    def call_siblings_for_stability_test(self,tester_count_at_once:int=1,do_performance_adjust:bool=True): #asks who the fuck make system slow..,
        global STABILITY_BARRIER
        global DO_STABILITY_TEST
        global MAX_RUNNING_THREAD_NUM
        global MAX_RUNNING_THREAD_SEM
        global NEED_TO_WAIT_ADJUST_COMPLETE
        global PERFORMANCE_ADJUST_COMPLETED
        global SLOW_THREADS
        global WORST_THREAD
        global STAIBLITY_TEST_SEM
        global READY_TO_START_TEST
        global USE_THREAD_SCORE
        global STABILITY_TEST_COUNT
        global LIVE_SIBLINGS_COUNT
        global WAIT_SIBLINGS_TIMEOUT_SEC
        user_feedback("call for stability test my siblings")
        locked_barrier = STABILITY_BARRIER_LOCK.acquire(True,1)
        locked_live_siblings = LIVE_SIBLINGS_COUNT_LOCK.acquire(True,1)
        me = self.__my_name
        try:
            STABILITY_TEST_COUNT += 1
            if STABILITY_TEST_COUNT % 5 == 0:
                self.calculate_program_stability_score()

            USE_THREAD_SCORE = False # reset flag.
            NEED_TO_WAIT_ADJUST_COMPLETE = False
            if (locked_barrier and locked_live_siblings):
                if do_performance_adjust: # if we are doing stability test for finding and killing worst thread , do performance adjust
                    NEED_TO_WAIT_ADJUST_COMPLETE = True
                    PERFORMANCE_ADJUST_COMPLETED = threading.Event()
                    USE_THREAD_SCORE = True


                STABILITY_BARRIER = threading.Barrier(LIVE_SIBLINGS_COUNT)
                READY_TO_START_TEST = threading.Barrier(LIVE_SIBLINGS_COUNT) # Wait all siblings finish their job and be ready to start the test..
                STAIBLITY_TEST_SEM = threading.Semaphore(tester_count_at_once)
                user_feedback("Wait threads to ready for test.")
                DO_STABILITY_TEST = True # this line have to be before READY_TO_START_TEST.wait()...!!
                try:
                    READY_TO_START_TEST.wait(WAIT_SIBLINGS_TIMEOUT_SEC)
                except Exception as e:
                    DO_STABILITY_TEST = False  # this line have to be before READY_TO_START_TEST.wait()...!!
                    raise Exception("DO_STABILITY_TEST = FALSE Reason : Siblings couldn't be ready to start staiblity test in time!")
                user_feedback("START STABILITY TEST WITH THREAD COUNT {:d}!!".format(int(tester_count_at_once)))
                avg_time = self.do_stability_test()
                with SLOW_THREADS_LOCK:
                    SLOW_THREADS.update({me: avg_time})
                try:
                    max_wait_time_to_test_finish = (LIVE_SIBLINGS_COUNT * DEFAULT_STABILITY_TEST_COUNT) * (
                                OPTIMAL_CYCLE_TIME * 2 ) + 1000
                    debug("Max Wait Time to other threads to finish stability tests is {:f}".format(float(max_wait_time_to_test_finish)))
                    STABILITY_BARRIER.wait(max_wait_time_to_test_finish)
                    user_feedback("All Stability Tests FINISHED")
                except Exception as e:
                    with SLOW_THREADS_LOCK:
                        error("TEST DID NOT FINISH BUT MAX WAIT TIME REACHED , FINISHED TESTS ARE:")
                        threads = SLOW_THREADS.keys()
                        index = 1
                        for thread in threads:
                            thread_score = SLOW_THREADS.__getitem__(thread)
                            error("{:d} / {:d} ->  {:s} : {:f} ".format(int(index),int(LIVE_SIBLINGS_COUNT),str(thread),float(thread_score)))
                            index += 1

                DO_STABILITY_TEST = False
                STABILITY_BARRIER = None
                if do_performance_adjust:
                    self.do_performance_adjust()
                    SLOW_THREADS.clear() # Clear slow threads for next test
                else:
                    return SLOW_THREADS
            else:
                if (locked_barrier != True):
                    error("barrier can't locked")
                if (locked_live_siblings != True):
                    error("locked_live_siblings can't locked")
                return
        except Exception as e:
            DO_STABILITY_TEST = False
            error("Error call_siblings_for_stability_test {:s} , DO_STABILITY_TEST Set as False!".format(str(e)))
        finally:
            if locked_barrier:
                STABILITY_BARRIER_LOCK.release()
                debug("barier lock relesed")
            if locked_live_siblings:
                LIVE_SIBLINGS_COUNT_LOCK.release()
                debug("live siblings count lock released")
            if (WORST_THREAD == me):
                debug("Stability-Test Caller is the Worst Thread Bye.")
                self.stop_service()  # TODO: CHECK IF stopin service cause not releasing locks??


    def handle_stability_call_request(self): # do stability test if a sibling has requested it
        global DO_STABILITY_TEST
        global SLOW_THREADS
        global WORST_THREAD
        global PERFORMANCE_ADJUST_COMPLETED
        global NEED_TO_WAIT_ADJUST_COMPLETE
        global READY_TO_START_TEST
        if DO_STABILITY_TEST == True:
            debug("Test request found , waiting other threads to be ready")
            try:
                READY_TO_START_TEST.wait()
            except threading.BrokenBarrierError as err:
                error("FATAL ERROR: READY_TO_START_TEST Barrier is broken!")
                return False #TODO: do something nicer here. Handle error , kill itelf or sth else but not this.
            me = self.__my_name
            avg_time = self.do_stability_test()
            with SLOW_THREADS_LOCK:
                SLOW_THREADS.update({me:avg_time})
            try:
                max_wait_time = (LIVE_SIBLINGS_COUNT * DEFAULT_STABILITY_TEST_COUNT )* (OPTIMAL_CYCLE_TIME * 3) # assume threads  got slower as three times than freshly started
                STABILITY_BARRIER.wait(max_wait_time) #Tell the caller I'm ready
            except Exception as e:
                error("Max Wait Time reached as a tester , just continue and wait for adjustment report.")

            if (NEED_TO_WAIT_ADJUST_COMPLETE):
                PERFORMANCE_ADJUST_COMPLETED.wait()
                debug("PERFORMANCE ADJUST IS COMPLETED")
                if (me == str(WORST_THREAD)):
                    user_feedback("I'm the worst thread bye.")
                    self.stop_service()
                debug("After PERFORMANCE_ADJUST_COMPLETED I'm in SAFE")
            else:
                debug("No need for performans adjust, just continue.")

            return True
        else:
            return False # No need


    def do_stability_test(self,sample_count:int = DEFAULT_STABILITY_TEST_COUNT): # let's find if I'm the guilty booyy that makes system sloww.
        result = None
        currency = self._working_currency
        avg_time = 0
        global OPTIMAL_CYCLE_TIME
        global USE_THREAD_SCORE
        if USE_THREAD_SCORE:
            return self.__driver_score
        with STAIBLITY_TEST_SEM: # At a one time only one thread should have cpu. This is test man , serious. Some of us will die..
            try:
                debug("stability test started")
                ts = time.time() * 1000
                test_count = 0
                while(test_count < sample_count):
                    try:
                        self.get_order_book(currency)
                    except Exception as e:
                        error("Error get_order_book in stability test -> {:s}".format(str(e)))
                    test_count += 1
                te = time.time() * 1000
                avg_time = (te-ts) / test_count
            except Exception as e:
                error("Error do_stability_test {:s}".format(str(e)))
            finally:
                debug("Stability Test Score:{:f}".format(float(avg_time)))
                return avg_time

    def find_optimum_max_thread_num(self,thread_count:int=0):
        global LIVE_SIBLINGS_COUNT
        global CPU_CORE
        global SLOW_THREADS
        global STATIC_THREAD_COUNT
        if STATIC_THREAD_COUNT != 0:
            return [STATIC_THREAD_COUNT , 1000] # TODO: calculate this 1000 later.
        if thread_count == 0:
            thread_count = CPU_CORE if CPU_CORE <= LIVE_SIBLINGS_COUNT else LIVE_SIBLINGS_COUNT
        elif thread_count > LIVE_SIBLINGS_COUNT:
            error("Thread count can't be higher than Live siblings count {:d}".format(int(LIVE_SIBLINGS_COUNT)))
            thread_count = LIVE_SIBLINGS_COUNT

        results={}
        while True:
            ts = time.time()*1000
            self.call_siblings_for_stability_test(thread_count, False)  # don't do performance adjust..
            te = time.time()*1000
            total_time = te - ts;
            results.update({thread_count:total_time})
            thread_count = thread_count -1
            if (thread_count == 0):
                break

        for thread,total_time in results.items():
            user_feedback("{:d} Thread's total time is {:f}".format(int(thread),total_time))

        optimum_thread_count = min(results,key=results.get)


        return [optimum_thread_count,results.__getitem__(optimum_thread_count) / LIVE_SIBLINGS_COUNT]


    def first_setup(self):
        global OPTIMAL_CYCLE_TIME
        global MAX_RUNNING_THREAD_SEM
        global MAX_RUNNING_THREAD_NUM
        global READY_TO_START
        global FIRST_START
        global LIVE_SIBLINGS_COUNT
        global PROGRAM_START_TIME
        global KOINEKS_SERVICVES_ALL_READY

        PROGRAM_START_TIME = time.time()

        MAX_RUNNING_THREAD_NUM , OPTIMAL_CYCLE_TIME = self.find_optimum_max_thread_num()
        max_cycle_time = self.get_max_cycle_time()
        user_feedback("With honor I'm proud to announce to all my siblings our running thread number is {:d} and   MAX CYCLE TIME is {:f}".format(int(MAX_RUNNING_THREAD_NUM),
                float(max_cycle_time)))

        MAX_RUNNING_THREAD_SEM = threading.Semaphore(MAX_RUNNING_THREAD_NUM)
        KOINEKS_SERVICVES_ALL_READY = True
        READY_TO_START = True
        FIRST_START = False

        return

    def increase_sibling_count(self):
        first_thread = False
        global LIVE_SIBLINGS_COUNT
        self.go_market(self._working_currency)
        with LIVE_SIBLINGS_COUNT_LOCK:
            LIVE_SIBLINGS_COUNT += 1
        user_feedback("{:s}: {:d} / {:d}  is ready...".format(str(datetime.now()),int(LIVE_SIBLINGS_COUNT),
                                                                  int(EXPECTED_SIBLINGS_COUNT)))


    def init(self):
        self.__init__(self.__user,self.__pass,self._driver_name,self.__browser_class,self._working_currency,self.__service_max_restart_count,self.__headles_browser)
        return self

    def start(self):
        global LIVE_SIBLINGS_COUNT
        global EXPECTED_SIBLINGS_COUNT
        global MAX_RUNNING_THREAD_NUM
        global MAX_RUNNING_THREAD_SEM
        global READY_TO_START
        global MIN_CYCLE_TIME
        global FIRST_START
        global LAST_SERVICE_LOGGED
        global MAX_CYCLE_COUNT
        global MAX_STOP_REQUEST
        global SERVICE_RELIABLE_COUNT
        global MAX_ERROR_COUNT
        self.__my_name = threading.Thread.getName(threading.currentThread())
        logged = self.login()
        if logged != True:
            error("Couldn't logged in!")
            return
        LAST_SERVICE_LOGGED.set()
        first_thread = False
        self.increase_sibling_count()

        if LIVE_SIBLINGS_COUNT == 1:
            first_thread = True
            READY_TO_START = False



        if FIRST_START:
            ALL_SIBLINGS_STARTED.wait()  # tell others I'm started..This is a barrier ;)
            if first_thread:
                self.first_setup()
            else:
                while(READY_TO_START == False):
                    debug("Not ready to start ,handle_stability_call")
                    self.handle_stability_call_request()
                    time.sleep(2)
        cycle = 0
        error_count = 0
        stop_request = 0
        service_reliable_counter = 0 # every time cycle completed under 3 sec , increase one and when it reaches RELIABLE COUNT , remove stop_request
        while True:
            done =self.handle_stability_call_request() # Before start , look if there is stability test call.
            if (done == True):
                stop_request = 0 # we already tested now , clear it.
            if (stop_request >= MAX_STOP_REQUEST):
                stop_request = 0
                self.call_siblings_for_stability_test()

            if service_reliable_counter > SERVICE_RELIABLE_COUNT and stop_request > 0: # this service is reliable man , remove stop requests..
                user_feedback("Service is proven to be reliable , {:d} stop requests are removed".format(int(stop_request)))
                stop_request = 0

            currency = self._working_currency

            try:
                with MAX_RUNNING_THREAD_SEM:
                    ts = time.time() * 1000
                    tables = self.get_order_book(currency)
                    self.update_order_book(currency, tables)
                    te = time.time() * 1000
                cycle += 1
                spent_time = te-ts
                self.__driver_score = ((self.__driver_score * (cycle-1)) + spent_time) / cycle
                wait_time = (MIN_CYCLE_TIME  - spent_time ) / 1000 # this is the time we need to wait before starting next_cycle , we don't want to rush.
                user_feedback("Cycle {:d} {:s} in {:f}ms".format(int(cycle), str(currency),float(spent_time)))
                if wait_time > 0:
                    time.sleep(wait_time)
                max_cycle_time = self.get_max_cycle_time()
                if (spent_time > max_cycle_time and LIVE_SIBLINGS_COUNT >= EXPECTED_SIBLINGS_COUNT): #ms
                    stop_request_strong = (spent_time / max_cycle_time) / 2
                    stop_request += stop_request_strong # stop service , we are slow!
                    service_reliable_counter = 0 # wow , service has to prove that it's really reliable..
                    error("Stop Request {:d}/{:d} max_cycle_time: {:f}".format(int(stop_request),int(MAX_STOP_REQUEST),float(max_cycle_time)))
                elif stop_request > 0:
                    reliable_score = max_cycle_time / spent_time
                    service_reliable_counter += reliable_score
                    user_feedback("service_reliable_counter increases {:f}".format(float(service_reliable_counter)))
                if cycle >= MAX_CYCLE_COUNT and LIVE_SIBLINGS_COUNT >= EXPECTED_SIBLINGS_COUNT:
                    self.stop_service("{:s} Service reached it's max cycle!".format(str(currency)))
                    return

            except Exception as e:
                error_count += 1
                error("Error{:d} occured getting order book of {:s} Error: {:s}".format(int(error_count), str(currency),str(e)))
                if (error_count > MAX_ERROR_COUNT): # TODO: Try to call speed-test here, I am Wondering how it will be..
                    self.stop_service("{:s} Service not working properly anymore!".format(str(currency)))
                    return

    @staticmethod
    def is_all_services_are_ready():
        global KOINEKS_SERVICVES_ALL_READY
        return KOINEKS_SERVICVES_ALL_READY

    @staticmethod
    def start_fetcher_sub_services(currency_set:tuple,browser_class:MainBrowser,browser_driver:str,headless:bool,min_cycle_time,acc:str,password:str):
        global CPU_CORE
        global LAST_SERVICE_LOGGED
        global MIN_CYCLE_TIME
        global STATIC_THREAD_COUNT

        global MIN_CYCLE_TIME
        global ALL_SIBLINGS_STARTED
        global EXPECTED_SIBLINGS_COUNT
        global FIRST_START
        MIN_CYCLE_TIME = min_cycle_time

        CPU_CORE = multiprocessing.cpu_count() * 2
        user_feedback("CPU-CORE: {:d} MIN_CYCLE_TIME : {:d}".format(int(CPU_CORE),int(MIN_CYCLE_TIME)))



        if not os.path.exists(symbols.ORDER_BOOK_DIR):
            os.makedirs(symbols.ORDER_BOOK_DIR)
            user_feedback("order_book dir is created for the first time , is it new environment?")

        if (os.path.isfile(symbols.KOINEKS_ORDER_BOOK_FILE) is not True):
            error("Order Book File will be created for the first time!")
            with open(symbols.KOINEKS_ORDER_BOOK_FILE , "w+") as order_book_file:
                print("order book file created for the first time , is it new environment?")



        FIRST_START  = True
        EXPECTED_SIBLINGS_COUNT = len(currency_set)
        ALL_SIBLINGS_STARTED = threading.Barrier(EXPECTED_SIBLINGS_COUNT)
        started_sub_services = {}
        user_feedback("{:d} siblings will run ".format(int(EXPECTED_SIBLINGS_COUNT)))
        for currency in currency_set:
            currency = str(currency).upper()
            service = OrderBookFetcherService(acc, password, browser_driver,browser_class, currency,-1,headless)
            LAST_SERVICE_LOGGED = threading.Event()
            service_thread = service.start_service()
            started_sub_services.update({service_thread.getName():service_thread})
            user_feedback("{:s} Service is started {:s}".format(str(datetime.now()),str(currency)))
            LAST_SERVICE_LOGGED.wait() #TODO: Test it before commit..
            user_feedback("Last servie is logged , wait 5 sec before start another..")
            time.sleep(5)
        return started_sub_services

