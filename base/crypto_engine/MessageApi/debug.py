#Author Ozan Ozenoglu ozan.ozenoglu@gmail.com
#File Created at 08.11.2017



'''
Scope of Module:
This module has functions for debugging and logging purpose
'''

import threading
import inspect
import json
import sys
import traceback
from datetime import datetime
import time

import os
import api.base.crypto_engine.symbols as symbols
import collections

from base.crypto_engine.MessageApi import FcmService

ERROR_BUFFER = collections.deque(maxlen=100)
DEBUG_BUFFER = collections.deque(maxlen=50)


PERFORMANCE_ENABLED = False
INFO = "INFO"
DEBUG = "DEBUG"
SILENT = "SILENT"
ERROR = "ERROR"
TRACE = "TRACE"
WARNING = "WARNING"
USER_FEEDBACK = "USER_FEEDBACK"
MAX_MSG_LEN = 400

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    DEBUG = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

print(bcolors.FAIL + "Warning: No active frommets remain. Continue?" )


def convert_dict_to_str(val:dict):
    return json.dumps(dict)


key = "AAAAy0nKhj4:APA91bHc1RfNzVXAJnSWLZfKnIbcpOtyaJGfwLBq-YCFWK9khG0WDZoX_aXr9AaduL18yzdf-OXPtQuWKCEJ_FUmNvNNLjAHLNm5jhsReBJ4KN6_Z81yiZ3_x0RNRgsAieIyi6Cq7PzH"

DEBUG_LEVELS = [TRACE,INFO,WARNING,DEBUG,USER_FEEDBACK,ERROR,SILENT]



class Debug:
    CURRENT_DEBUG_LEVEL = None

    @staticmethod
    def log(msg,logger_id:str):
        try:
            if(os.path.exists(symbols.LOG_DIR) is not True):
                error("LOG_DIR does not exists")
                os.makedirs(symbols.LOG_DIR)
            with open(symbols.LOG_DIR + logger_id + ".log","w+") as log_file:
                log_file.write(msg)
        except Exception as e:
            error("Error in log method {:s}".format(str(e)))


    @staticmethod
    def set_debug_level_file(file_name):
        try:
            current_path = os.path.dirname(os.path.realpath(__file__))
            config_folder = str(current_path).split('src')[0] + "src/config/"
            file_path = config_folder + file_name

            print("DEBUG FILE PATH: {:s}".format(str(file_path)))
            symbols.DEBUG_LEVEL_FILE = file_path
        except Exception as e:
            print("Error during set_debug_level_file {:s}".format(str(e)))

    @staticmethod
    def set_debug_level(level:str):
        level = str(level).upper()
        symbols.DEBUG_LEVEL  = DEBUG_LEVELS[DEBUG_LEVELS.index(level)]

        last_update_time = int(round(time.time() * 1000))
        symbols.LAST_DEBUG_LEVEL_SET_TIME = last_update_time

        with open( symbols.DEBUG_LEVEL_FILE, 'wb+') as outputfile:
            byte_array = bytearray(json.dumps({'DebugState':level}),'utf8')
            outputfile.write(byte_array)
    
    @classmethod
    def get_debug_level(Debug):
        now = int(round(time.time()*1000))
        difference = now - symbols.LAST_DEBUG_LEVEL_SET_TIME
        difference = difference / 1000

        if (difference <  60): # return from memory don't try to read it from file
            return symbols.DEBUG_LEVEL
        try:
            with open( symbols.DEBUG_LEVEL_FILE, 'r') as arbitrage_pairs_file:
                data = json.load(arbitrage_pairs_file)
                debug_level =  data.__getitem__('DebugState')
                symbols.DEBUG_LEVEL = debug_level
                symbols.LAST_DEBUG_LEVEL_SET_TIME = now
                return debug_level
        except Exception as e:
            #printv2("Error in {:s} file returning last debug level: {:s}".format(str(symbols.DEBUG_LEVEL_FILE),str(e)))
            return symbols.DEBUG_LEVEL


def dump_trace():
    traceback.print_stack()


def get_curret_thread_name():
    if PERFORMANCE_ENABLED is not True:
        sys.stdout.flush()

    current_thraed_name = "ThreadNameNotFound"
    try:
        current_t = threading.currentThread()
        current_thraed_name = threading.Thread.getName(current_t)
    except Exception as e:
        print("error during getting thread name : {:s}".format(str(e)))

    return current_thraed_name


def debug(msg,by_pass:bool = False):
    try:
        t_name = get_curret_thread_name()

        index = DEBUG_LEVELS.index(Debug.get_debug_level())
        if ((index <= DEBUG_LEVELS.index(DEBUG)) or by_pass):
            time_stamp = datetime.now()

            caller_function = sys._getframe(1).f_code.co_name
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = "file_name_not_found"
            try:
                filename = module.__file__
            except Exception as e:
                printv2(e)
            splits = filename.split('/')
            caller_file = splits[len(splits) - 1]

            if (isinstance(msg,list)):
                for element in msg:
                    print(element)
            else:
                if (len(msg) > MAX_MSG_LEN):
                    msg = "TRUNCATED MSG: " + msg[:MAX_MSG_LEN] + ".."
                printv2(bcolors.DEBUG + "{:s}:DEBUG:{:s} {:s}.{:s} :{:s} ".format(str(t_name),str(time_stamp),caller_file,caller_function,msg))
        else:
            DEBUG_BUFFER.append(msg)
    except Exception as e:
        printv2("debug.py error in debug : {:s}".format(str(e)))

def printv2(msg):
    if (symbols.LOG_TO_FILE_ENABLED):
        msg = msg + "\n"
        file_name = get_curret_thread_name() + ".log"
        if (os.path.exists(symbols.LOG_DIR) is not True):
            os.makedirs(symbols.LOG_DIR)
        file_path = symbols.LOG_DIR + file_name
        with open(file_path,"a+") as log_file:
            log_file.write(msg)
    else:
        print(msg)


def dump_debugs():
    for msg in DEBUG_BUFFER:
        print
def error(msg):
    try:
        t_name = get_curret_thread_name()
        index = DEBUG_LEVELS.index(Debug.get_debug_level())
        if (index <= DEBUG_LEVELS.index(ERROR)):
            caller_function = sys._getframe(1).f_code.co_name
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = "file_name_not_found"
            try:
                filename = module.__file__
            except Exception as e:
                print(e)
            splits = filename.split('/')
            caller_file = splits[len(splits) - 1]
            if (len(msg) > MAX_MSG_LEN):
                msg = "TRUNCATED MSG: " + msg[:MAX_MSG_LEN] + ".."

            printv2(bcolors.FAIL + "{:s}:ERROR: {:s}.{:s} :{:s} ".format(str(t_name),caller_file, caller_function, msg))
        else:
            ERROR_BUFFER.append(msg)
    except Exception as e:
        printv2("debug.py  error : {:s}".format(str(e)))

def info(msg):
    try:
        index = DEBUG_LEVELS.index(Debug.get_debug_level())
        if (index <= DEBUG_LEVELS.index(INFO)):
            caller_function = sys._getframe(1).f_code.co_name
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = "file_name_not_found"
            try:
                filename = module.__file__
            except Exception as e:
                print(e)
            splits = filename.split('/')
            caller_file = splits[len(splits) - 1]
            if (len(msg) > MAX_MSG_LEN):
                msg = "TRUNCATED MSG: " + msg[:MAX_MSG_LEN] + ".."
            printv2(bcolors.OKGREEN + "INFO: {:s}.{:s} :{:s} ".format(caller_file, caller_function, msg))
    except Exception as e:
        printv2("debug.py error in info : {:s}".format(str(e)))

def user_feedback(msg:str,truncated_free:bool=False,print_time:bool=False):
    try:
        t_name = get_curret_thread_name()
        index = DEBUG_LEVELS.index(Debug.get_debug_level())
        if (index <= DEBUG_LEVELS.index(USER_FEEDBACK)):
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = "file_name_not_found"
            try:
                filename = module.__file__
            except Exception as e:
                printv2(e)
            splits = filename.split('/')
            if (truncated_free is False and len(msg) > MAX_MSG_LEN):
                msg = "TRUNCATED MSG: " + msg[:MAX_MSG_LEN] + ".."
            if (print_time):
                now = datetime.now().strftime("%d:%m:%Y %H:%M:%S")
                msg = "{:s}: ".format(str(now)) + msg               
            printv2(bcolors.OKGREEN + "{:s}:{:s} ".format(str(t_name),msg))
    except Exception as e:
        printv2("debug.py error in user_feedback {:s}".format(str(e)))


def warn(msg):
    try:
        index = DEBUG_LEVELS.index(Debug.get_debug_level())
        if (index <= DEBUG_LEVELS.index(WARNING)):
            caller_function = sys._getframe(1).f_code.co_name
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            filename = module.__file__
            splits = filename.split('/')
            caller_file = splits[len(splits) - 1]
            if (len(msg) > MAX_MSG_LEN):
                msg = "TRUNCATED MSG: " + msg[:MAX_MSG_LEN] + ".."
            printv2(bcolors.OKBLUE + "Warning: {:s}.{:s} :{:s} ".format(caller_file, caller_function, msg))
    except Exception as e:
        printv2("debug.py error in wanr {:s}".format((str(e))))
def notify(msg):
    try:
        str_msg = None
        if (type(msg) == type({})):
            str_msg = convert_dict_to_str(msg)
        else:
            error("Unrecgonized type of data")
            return

        sender = FcmService.FcmService()
        # sender.send_notification('DARPHANE',str_msg)
    except Exception as e:
        printv2("debug.py error in notify {:s}".format(str(e)))

def android_alarm(msg):
    try:
        #index = DEBUG_LEVELS.index(Debug.get_debug_level())
        #if (index == DEBUG_LEVELS.index(SILENT)):
            #return
        sender = FcmService.FcmService()
        sender.send_notification('alarm',msg)
    except Exception as e:
        printv2("debug.py error in android_alarm {:s}".format((str(e))))

def send_data(msg):
    try:
        str_msg = None
        if (type(msg) == type({})):
            str_msg = convert_dict_to_str(msg)
        else:
            error("Unrecgonized type of data")
            return

        sender = FcmService.FcmService()
        #sender.send_data(str_msg)
    except Exception as e:
        printv2("debug.py error in send_data {:s}".format(str(e)))
