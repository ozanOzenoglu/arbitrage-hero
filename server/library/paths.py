import glob
import os
import os.path as op
import json
from api.base.crypto_engine import symbols
from api.base.crypto_engine.MessageApi.debug import *


HOME = op.dirname(op.dirname(op.abspath(__file__)))


def dump_json(filename, payload):
    if filename is None:
        return -1
    try:
        with open(filename, 'w') as fp:
            json.dump(payload, fp, sort_keys=True)
            fp.close()
            return 0
    except Exception as e:
        error("Error during dumping json : {:s}".format(str(e)))
        return -1



def f_convert_to_dict(json_str): #(f)orce convert to dict..
    dict_a = json.loads(json_str)
    while(type(dict_a) != type({})):
        dict_a = json.loads(dict_a)
    return dict_a

def get_json_content_as_dict_from_path(path):
    if dir:
        try:
            if op.exists(path) and op.isfile(path):
                with open(path, "r") as fr:
                    content = fr.readline()
                    '''obtain an ordered json to be able to compare it with expected data on tests'''
                    cont_dict = json.loads(content)
                    cont_json = json.dumps(cont_dict, sort_keys=True)
                    cont_json = f_convert_to_dict(cont_json)
                    return cont_json
        except Exception as e:
            error("error during reading file: {:s}: {}".format(path, str(e)))
    return None

'''return sorted dict as str object'''
def get_json_content(dir, filename):
    if dir:
        filename = dir + filename
        try:
            if op.exists(filename) and op.isfile(filename):
                with open(filename, "r") as fr:
                    content = fr.readline()
                    '''obtain an ordered json to be able to compare it with expected data on tests'''
                    cont_dict = json.loads(content)
                    cont_json = json.dumps(cont_dict, sort_keys=True)
                    return cont_json
        except Exception as e:
            print("error during reading file: {:s}: {}".format(filename, str(e)))
    return None


def check_path(path):
    if not op.exists(path):
        print("[paths] {:s} doesn't exist: creating...".format(path))
        os.mkdir(path)
    return path


def path(dir_name):
    dir_name += "/"
    res = op.join(HOME, dir_name)
    if not op.exists(res):
        print("[paths] {} doesn't exist: creating...".format(res))
        os.mkdir(res)
    return res

def read_file(file_path):
    try:
        if os.path.isfile(file_path):
            with open(file_path , "rb") as file:
                content = file.read()
                return content
        else:
            return "file could not be found"
    except Exception as e:
        print("Error while reading file {:s} error:{:s}".format(str(file_path),str(e)))
        return None

def files(dir_name):
    dir = path(dir_name)
    files = [f for f in os.listdir(dir) if op.isfile(op.join(dir, f))]
    return files

def dirs(dir_name):
    dir = path(dir_name)
    directories = [f for f in os.listdir(dir) if not op.isfile(op.join(dir, f))]
    return directories

def get_tables_dir(live_requested , creator):
    if (live_requested):
        dir = os.path.join(symbols.NEW_TABLE_DIR,creator)
    else:
        dir = os.path.join(symbols.OLD_TABLE_DIR,creator)

    result = os.path.isdir(dir) #TODO: There is bug here, when api_service(server) just started , then this line executed , it returns False even directory is EXISTS! fck.
    if (result == False):
        result = os.path.isdir(dir)
    if result is not True:
        return None
    return dir

def find_table_file(name, live:bool=True):
    name = name.lower()
    result = []
    if live:
        dir = symbols.NEW_TABLE_DIR
    else:
        dir = symbols.OLD_TABLE_DIR
    files = glob.glob(dir  +   '/**/*.svg', recursive=True)
    for file in files:
        if(str(file).lower().__contains__(name)):
            result.append(file)
    #result = [f for f in files if (f.lower().__contains__(name)]
    return result

    # my_path/     the dir
    # **/       every file and dir under my_path
    # *.txt     every file that ends with '.txt'

def get_order_book_dir():
    dirname = "order_books"
    return path(dirname)


def get_sms_codes_dir():
    dirname = "sms_codes"
    return path(dirname)


def get_opportunity_dir():
    return check_path(symbols.OPPORTUNITY_DIR)


def get_best_ops_dir():
    return check_path(symbols.BEST_OPS_DIR)

def get_statistic_dir():
    return check_path(symbols.STATISTICS_DIR)

def get_daily_statistic_dir():
    return check_path(symbols.DAILY_STATISTIC_DIR)

def get_weekly_statistic_dir():
    return check_path(symbols.WEEKLY_STATISTIC_DIR)

def get_monthly_statistic_dir():
    return check_path(symbols.MONTHLY_STATISTIC_DIR)