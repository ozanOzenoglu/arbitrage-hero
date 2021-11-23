import json, os
from api.server.library import paths
from api.base.crypto_engine.utils import helper
from datetime import date, datetime


def get_monthly_statistics():
    today = str(date.today())
    current_month = today.split("-")[1]
    year = today.split("-")[0] 
    
    monthly_statistic_file = year + "-" + current_month
    monthly_statistic_files = paths.files(paths.get_monthly_statistic_dir())
    if monthly_statistic_files.__contains__(monthly_statistic_file) is not True:
        return None
    monthly_statistic_file_path = os.path.join(paths.get_monthly_statistic_dir(), monthly_statistic_file)
    monthly_dict = paths.get_json_content_as_dict_from_path(monthly_statistic_file_path)
    result = {monthly_statistic_file: monthly_dict}
    return json.dumps(result)

def get_weekly_statistics():
    today = str(date.today())
    current_month = today.split("-")[1]
    year = today.split("-")[0]
    week =  str(helper.find_current_week_number())

    weekly_statistic_file = year + "-" + current_month + "-" + week
    weekly_files = paths.files(paths.get_weekly_statistic_dir())
    if weekly_files.__contains__(weekly_statistic_file) is not True:
        return None
    weekly_statistic_file_path = os.path.join(paths.get_weekly_statistic_dir(), weekly_statistic_file)
    weekly_dict = paths.get_json_content_as_dict_from_path(weekly_statistic_file_path)
    result = {weekly_statistic_file: weekly_dict}
    return json.dumps(result)


def get_today_statistics():
    daily_files = paths.files(paths.get_daily_statistic_dir())
    today = str(date.today())
    if daily_files.__contains__(today) is not True:
        return None
    today_statistic_file_path = os.path.join(paths.get_daily_statistic_dir(), today)
    daily_dict = paths.get_json_content_as_dict_from_path(today_statistic_file_path)
    result = {today: daily_dict}
    return json.dumps(result)

def get_all_statistics():   
    
    statistics_dir = paths.get_daily_statistic_dir()
    all_statistics_ops = paths.files(statistics_dir)
    all_statistics_dict = {}
    for statistics_op in all_statistics_ops:
        if str(statistics_dir).endswith("/") is not True:
            statistics_dir = statistics_dir + "/"
        content_str = paths.get_json_content(statistics_dir, statistics_op)
        content = json.loads(content_str)
        if content is not None:
            all_statistics_dict.update({statistics_op: content})

    return json.dumps(all_statistics_dict)
    

def get_statistic(statistic_date:str):
    try:
        statistic_dir = paths.get_daily_statistic_dir() 
        files = [os.path.join(statistic_dir,f)  for f in paths.files(statistic_dir) if (str(f).__contains__(statistic_date))]
        if (len(files) > 1):
            raise Exception("There are {:d} files with name {:s}".format(int(len(files)), str(statistic_date)))
        content = paths.read_file(files[0])
        return content
    except Exception as e:
        raise Exception("Error during reading_statistic for {:s} Error:{:s}".format(str(statistic_date),str(e)))