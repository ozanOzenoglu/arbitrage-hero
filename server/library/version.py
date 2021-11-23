
from api.server.library import paths
import os.path as path
from api.base.crypto_engine import symbols

def get_app_version():
        try:
            with open(symbols.VERSION_FILE, "r") as sf:
                latest_version = sf.readline()
                return latest_version
        except Exception as e:
            print("error during returning sms code {:s}".format(str(e)))
            return "error"