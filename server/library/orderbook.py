from api.server.library import paths
from api.server.library.db import DB
import json

def update_order_book(market_name, content: dict):
    DB.set_val(market_name + "_orderbook",content)
    return 0
    # ob_dir = paths.get_order_book_dir()
    # try:
        # ob_file = ob_dir + filename + ".json"
        # paths.dump_json(ob_file, content)
    # except Exception as e:
        # print("error during writing order book file: {:s}".format(str(e)))


def get_orderbook(market):
    try:
        ret = DB.get_val(market + "_orderbook")
        if(type(ret) == type("")):
            ret = json.loads(ret)
        return ret
    except Exception as e:
       error("Error during fetching orderbook for {:s}".format(str(market)))
       return None
    # ob_dir = paths.get_order_book_dir()
    # return paths.get_json_content(ob_dir, market)
    