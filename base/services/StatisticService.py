from base.services.IWatchableWatcherService import IWatchableWatcherService
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from api.server.library.paths import *
from base.crypto_engine.MessageApi.debug import *
from base.crypto_engine.utils import helper

import json,os,math
from datetime import date,  datetime
from pathlib import Path

def trycatch(method):
    def catched(*args, **kw):
        result = None
        try:
            result = method(*args, **kw)
        except Exception as e:
            error("Error: {:s} -> {:s}".format(str(method.__name__), str(e)))
        return result
    return catched


class StatisticService(IWatchableWatcherService):

    LiveOps = {}
    FileExpiredThresholdDay = 365 # indicated the maximum age of a file in day, Older than this will be removed.
    SubServiceStarted = False

    def __init__(self, path_to_watch: str, patterns: list):
        global SubServiceStarted
        try:
            if os.path.exists(symbols.STATISTICS_DIR) is not True:
                os.mkdir(symbols.STATISTICS_DIR)
        except Exception as e:
            error("Fattal Error: Statistic dir {:s} couldn't be initialized! Exception:{:s}".format(str(e)))
            raise Exception("Fattal Error: Statistic dir {:s} couldn't be initialized! Exception: {:s}".format(str(e)))
        
        self._patterns = patterns
        self._path_to_watch = path_to_watch
        helper.create_path_if_not_exists(path_to_watch)
        helper.create_path_if_not_exists(symbols.DAILY_STATISTIC_DIR)
        helper.create_path_if_not_exists(symbols.WEEKLY_STATISTIC_DIR)
        helper.create_path_if_not_exists(symbols.MONTHLY_STATISTIC_DIR)

        
        if StatisticService.SubServiceStarted == False:
            OldStatisticFileRemoverSubServiceThread = threading.Thread(target=StatisticService.OldStatisticFileRemoverSubService,name="OldStatisticFileRemoverSubService")
            OldStatisticFileRemoverSubServiceThread.start()
            StatisticService.SubServiceStarted = True
        
        super().__init__(self._patterns, path_to_watch, action_interval=10, onModified=True, onCreated=False, folderLockRequired=True)
        

    def init(self):
        self.__init__(self._path_to_watch, self._patterns)
        return self




    @staticmethod
    def find_old_monthly_static_file():
        old_files = []
        current_month = datetime.today().month
        statistic_directory = symbols.MONTHLY_STATISTIC_DIR
        all_statistic_files  = [f for f in os.listdir(statistic_directory) if os.path.isfile(os.path.join(statistic_directory, f))]
        for file in all_statistic_files:
            file_month = file.split("-")[1]
            if int(file_month) < int(current_month):
                file_path = os.path.join(statistic_directory,file)
                old_files.append(file_path)            
        return old_files
    
    
    @staticmethod
    def find_old_weekly_static_file():
        old_files = []
        current_week = helper.find_current_week_number()
        statistic_directory = symbols.WEEKLY_STATISTIC_DIR
        all_statistic_files  = [f for f in os.listdir(statistic_directory) if os.path.isfile(os.path.join(statistic_directory, f))]
        for file in all_statistic_files:
            file_week = file.split("-")[2]
            if int(file_week) < current_week:
                file_path = os.path.join(symbols.WEEKLY_STATISTIC_DIR,file)
                old_files.append(file_path)            
        return old_files
    

    @staticmethod
    def find_old_daily_statistics_file():
        old_files = []
        today = str(date.today())
        today_array = today.split("-")
        today_power = int(today_array[0])*365 + int(today_array[1])*30 + int(today_array[2])
        statistic_directory = symbols.DAILY_STATISTIC_DIR
        all_statistic_files  = [f for f in os.listdir(statistic_directory) if os.path.isfile(os.path.join(statistic_directory, f))]
        for file in all_statistic_files:
            file_array = file.split("-")
            file_power = int(file_array[0])*365 + int(file_array[1])*30 + int(file_array[2])
            file_age = today_power - file_power
            user_feedback("File age is {:d} of file: {:s}".format(int(file_age), str(file)))
            if file_age > StatisticService.FileExpiredThresholdDay: # if we want to keep lets say  3 months old file, then fileExpiredThreshold should be 90..
                file_path = os.path.join(statistic_directory, file)
                old_files.append(file_path)
            
        return old_files
    
    @staticmethod
    def OldStatisticFileRemoverSubService():
        while True:
            old_files = []
            daily_old_files = StatisticService.find_old_daily_statistics_file()
            weekly_old_files = StatisticService.find_old_weekly_static_file()
            monthly_old_files = StatisticService.find_old_monthly_static_file()
            old_files.extend(daily_old_files)
            old_files.extend(weekly_old_files)
            old_files.extend(monthly_old_files)
            
            for file_path in old_files:
                try:
                    os.remove(file_path)
                    user_feedback("Old Statistic file {:s} is cleared".format(str(file_path)))
                except Exception as e:
                    error("Error during removing file:{:s} Exception:{:s}".format(str(file_path), str(e)))
            
            time.sleep(60*60) #Wait 1 hour..
            
            

    @trycatch
    def parse_file(self, request_file_path: str):
        request = None
        with(open(request_file_path, "r")) as request_file:
            data = json.load(request_file)
            keys = data.keys()
            for key in keys:
                val = data.__getitem__(key)
                request = OpportunityInfo.json_to_instance(val)
                break
        try:
            os.remove(request_file_path)
        except Exception as e:
            error("Error during removing file after parsing completed!{:s}".format(str(e)))
        
        return request
        

    
            
    def dump_json(self, path, payload):
        if path is None:
            return -1
        try:
            with open(path, 'w') as fp:
                json.dump(payload, fp, sort_keys=True)
                fp.close()
                return 0
        except Exception as e:
            error("Error during dumping json : {:s}".format(str(e)))
            return -1


    def get_json_content(self, path):
        if dir:
            try:
                if op.exists(path) and op.isfile(path):
                    with open(path, "r") as fr:
                        content = fr.readline()
                        '''obtain an ordered json to be able to compare it with expected data on tests'''
                        cont_dict = json.loads(content)
                        cont_json = json.dumps(cont_dict, sort_keys=True)
                        cont_json = self.convert_to_dict(cont_json)
                        return cont_json
            except Exception as e:
                error("error during reading file: {:s}: {}".format(path, str(e)))
        return None
        
        
    def convert_to_dict(self, json_str):
        dict_a = json.loads(json_str)
        while(type(dict_a) != type({})):
            dict_a = json.loads(dict_a)
        return dict_a
    
    
    
    def update_statistics_info(self,new_op:OpportunityInfo, statistic_info_path:str):
        newPercent = new_op.get_percent()
        op_name = new_op.get_simple_name()
        dirty = False
        new_op_json = new_op.to_json()
        keys = new_op_json.keys()
        for key in keys:
            data = new_op_json.__getitem__(key)
            new_op_json = data
            break
        infos = self.get_json_content(statistic_info_path)
        if infos is not None:
            if op_name in infos:
                info = infos.__getitem__(op_name)
                opInfo = OpportunityInfo.json_to_instance(info)
                maxPercent = opInfo.get_percent()
                if newPercent > maxPercent:
                    infos.update({op_name:new_op_json})
                    dirty = True
                    user_feedback("Better percent for Op Statistic:{:s} is recorded Old:{:f} New:{:f}".format(str(op_name),float(maxPercent),float(newPercent)))
            else:
                infos.update({op_name:new_op_json})
                dirty = True
                user_feedback("New Op Statistic:{:s} is recorded".format(str(op_name)))
            if dirty:
                contentStr = json.dumps(infos)
                self.dump_json(statistic_info_path, contentStr)
        else:
            new_info = {op_name:new_op_json}
            contentStr = json.dumps(new_info)
            self.dump_json(statistic_info_path, contentStr)
            user_feedback("First Record to the newly created statistic file has been done!")
                
    

    
    
    @trycatch
    def action(self,new_op:OpportunityInfo):
        today = str(date.today())
        month = today.split("-")[1] #TODO: deciding path with this method is false, make it generic(pythonic), because in apiService, generic way used(which more portable) but caused problem since here is not generic..
        year = today.split("-")[0] ## for now, we leave it here like this, because changing api service is much easier. But when you have time, change it plz.
        week =  str(helper.find_current_week_number())
        
        
        daily_statistic_info_path = symbols.DAILY_STATISTIC_DIR + today
        monthly_statistic_info_path  = symbols.MONTHLY_STATISTIC_DIR + year + "-" + month #sample 2019-12 
        weekly_statistic_info_path = symbols.WEEKLY_STATISTIC_DIR + year + "-" + month + "-" + week #Sample 2019-12-3 (third week of december.)
        paths = [daily_statistic_info_path, weekly_statistic_info_path, monthly_statistic_info_path]
        
        for statistic_info_path in paths:
            if os.path.exists(statistic_info_path) is not True:
                Path(statistic_info_path).touch()
                user_feedback("New Record file is created: {:s}".format(statistic_info_path))                
            self.update_statistics_info(new_op, statistic_info_path)
            
                
                
        



