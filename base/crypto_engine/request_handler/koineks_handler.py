import time
import datetime
import os
import json
import threading

from api.base.crypto_engine import symbols
from api.base.crypto_engine.browser.koineks_browser import KoineksBrowser
from api.base.crypto_engine.request_handler.handler import Handler
from base.crypto_engine.MessageApi.debug import *


def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))

        return result

    return catched


ONE_THREAD_LOCK = threading.Lock()


def only_one_thread(method):
    def syncronized(*args, **kw):
        with ONE_THREAD_LOCK:
            try:
                method(*args, **kw)
            except Exception as e:
                error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))

    return syncronized


def timeit(method):
    def handle(*args, **kw):
        try:
            ts = time.time() * 1000
            method(*args, **kw)
            te = time.time() * 1000
            user_feedback("{:s} finished in {:d}".format(str(method.__name__), int(te - ts)))
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))

    return handle


class KoineksRequestHandler(Handler):
    MAX_CYCLE = 1000
    MAIN_LOG_FOLDER = symbols.LOG_DIR

    def start(self):
        pass

    def __init__(self, username: str, password: str, driver_name="firefox", headless=True):
        self.__browser = KoineksBrowser(username, password, driver_name, headless)
        super().__init__(username)
        logged = self.__browser.login()
        if (logged is False):
            error("Koineks Handler couldn't be logged")
            self.de_init()
            return
        self.fetch_all_balance()
        self.__is_healthy = True

    def is_healthy(self):
        return self.__is_healthy

    def get_browser(self):
        return self.__browser

    def set_healthy_status(self, status: bool):
        self.__is_healthy = status

    def get_log_folder_path(self):
        return KoineksRequestHandler.MAIN_LOG_FOLDER

    def init(self):
        return self.__init__(self.__username, self.__password, self.__driver_name)

    def get_name(self):
        return "koineks"

    def de_init(self):
        self.set_healthy_status(False)
        self.__browser.quit()