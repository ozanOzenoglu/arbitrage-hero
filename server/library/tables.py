import json
import os
from api.server.library import paths
from api.base.crypto_engine.MessageApi.debug import *

def calculate_power(year,month,day,hour,min,sec):
    power = 0
    power += year * 365 * 24 * 60  * 60
    power += month * 30 * 24 * 60 * 60
    power += day * 24 * 60 * 60
    power += hour * 60 * 60
    power += min * 60
    power += sec
    return power

def calculate_power_of_searched_file(path):
    try:
        tmp = path.split("_")
        date = tmp[3]
        tmp_time = date.split("-")
        year = int(tmp_time[0])
        month = int(tmp_time[1])
        hour_tmp = tmp_time[2].split(" ")
        day = int(hour_tmp[0])
        hour_all = hour_tmp[1]
        min_tmp = hour_all.split(":")
        hour = int(min_tmp[0])
        min = int(min_tmp[1])
        sec = int(min_tmp[2])
        power =  calculate_power(year,month,day,hour,min,sec)
        return power
    except Exception as e:
        error("Error during calculate_power_of_searched_file:{:s}".format(str(e)))

def parse_file_to_its_power(path):
    try:
        tmp_path = path.split("_")
        date = tmp_path[-1]
        date_tmp = date.split(":")
        hour = int(date_tmp[0])
        min = int(date_tmp[1])
        sec = int(date_tmp[2])
        year = int(tmp_path[-2]) 
        month = int(tmp_path[-3])    
        day = int(tmp_path[-4])    
        power = calculate_power(year,month,day,hour,min,sec)
        return power
    except Exception as e:
        error("Error during parsing file to its power {:s}".format(str(e)))

def find_closest_file(date, file_list):
    try:
        previous_path = None
        date_power = calculate_power_of_searched_file(date)
        for path in file_list:
            current_power = parse_file_to_its_power(path)
            if(date_power > current_power):
                previous_path = path
            else:
                break
        if(previous_path == None):
            error("Couldn't file any closest path?")
            return "ERROR" #file_list[0] #return the oldest table #TODO: after creating a lot of tables that might help the situation but for now return None..
        return previous_path
    except Exception as e:
        error("Error during finding closest file: {:s}".format(str(e)))
def find_path(searchForPath, list):
    try:
        for path in list:
            if str(path).__contains__(searchForPath):
                return path
        return None
    except Exception as e:
        error("Error during finding table path {:s}".format(str(e)))

def get_statistic_table(table_full_name_with_date:str):#expected param should be like "cex_btcturk_XRP_10_12_2019_10:58:16"
    table_full_name_with_date = str(table_full_name_with_date).lower()
    table = None
    delimeter = "_"
    tmp = table_full_name_with_date.split(delimeter)
    just_arbitrage_name = tmp[0] + delimeter + tmp[1] + delimeter + str(tmp[2]).upper()
    related_tables = paths.find_table_file(just_arbitrage_name, live=False)
    changed_related_tables = [path.split(".")[0].split("/")[-1] for path in related_tables] # make all paths to lower case..

    if len(changed_related_tables) <= 0:
        raise Exception("There is no statistic table file yet.")
    
    if(changed_related_tables.__contains__(table_full_name_with_date)): #bingo, rare condition , you have the file directly..
        table = table_full_name_with_date
    else: # ok you don't have the file thats why , a previous one will be found.
        changed_related_tables.sort()
        try:
            table =  find_closest_file(table_full_name_with_date, changed_related_tables)
        except Exception as e:
            error("error finding closest file {:s}".format(str(e)))
            return "No Table found!"
        table_path = find_path(table, related_tables)
    if table_path == None :
        raise Exception("There is no file found for specified statistic table {:s}".format(str(table)))
        
    content = paths.read_file(table_path)
    return content

def get_table_list(live_requested, creator):
    try:
        table_dir = paths.get_tables_dir(live_requested,creator)
        if (table_dir == None):
            return []
        all_files = paths.files(table_dir)
        table_files = [f for f in all_files if str(f).endswith("svg")]
        return str(json.dumps(table_files))
    except Exception as e:
        print("ne error bu amk {:s}".format(str(e)))
        return str([])

def read_table_content(table_name, live:bool=True):
    files = paths.find_table_file(table_name, live)
    if (len(files) > 1):
        raise Exception("There are {:d} files with name {:s}".format(int(len(files)),str(table_name)))
    content = paths.read_file(files[0])
    return content