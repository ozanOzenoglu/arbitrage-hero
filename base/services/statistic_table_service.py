import json
import time
import os
import shutil
import pygal
from datetime import date
import threading
from pygal.style import Style
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from base.services.IWatchableWatcherService import IWatchableWatcherService
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


class StatisticTableService(IWatchableWatcherService):
    SubServiceStarted = False
    
    
    def __init__(self, path_to_watch: str, patterns: list):
        self.__max_point_count = symbols.MAX_TABLE_POINT_COUNT
        self.__new_table_dir = symbols.STATISTIC_TABLE_WORKING_TMP_DIR
        self.__old_table_dir = symbols.OLD_TABLE_DIR        
        self._patterns = patterns
        self._path_to_watch = path_to_watch
    
        if StatisticTableService.SubServiceStarted == False:
            OldStatisticFileRemoverSubServiceThread = threading.Thread(target=StatisticTableService.remove_too_old_tables,name="StatisticTableFileRemoverSubService")
            OldStatisticFileRemoverSubServiceThread.start()
            StatisticTableService.SubServiceStarted = True
        
        super().__init__(self._patterns, path_to_watch, action_interval=10, onModified=True, onCreated=False, folderLockRequired=True)
        
    def init(self):
        self.__init__(self._path_to_watch, self._patterns)
        return self

    def get_max_point_count(self):
        return self.__max_point_count

    def get_old_table_dir(self):
        return self.__old_table_dir
    def get_new_table_dir(self):
        return self.__new_table_dir
    

    @trycatch
    def parse_file(self, request_file_path:str):
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
        

    def determine_name(self,op_request:OpportunityInfo):
        buy_market = op_request.get_buy_market()
        sell_market = op_request.get_sell_market()
        currency = op_request.get_currency()
        name = buy_market + "_" + sell_market + "_" + currency 
        return name


    def create_statistic_table(self,file_path:str): #move the file to the old dated directory, this file is finished and can be viewed by non-paid customer now
        json_data_file = self.get_json_data_path_from_svg_file(file_path)
        old_path = symbols.STATISTIC_TABLE_WORKING_TMP_DIR
        new_path = symbols.OLD_TABLE_DIR
        new_file_path = file_path.replace(old_path,new_path)
        new_file_dir = new_file_path.split(file_path.split("/")[-1])[0]
        self.create_dir_if_not_exists(new_file_dir)
        shutil.move(file_path,new_file_path)
        os.remove(json_data_file)

    def get_json_data_path_from_svg_file(self,svg_file:str):
        return svg_file.split(".svg")[0] + ".json"

    def find_max_point_count(self,json_path:str): # find longest line point count in svg file
        data = self.load_data_file(json_path)
        keys = data.keys()
        max_point_count = 0
        for key in keys:
            val = data.__getitem__(key)
            points_count = len(val)
            if (points_count > max_point_count):
                max_point_count = points_count

        return  max_point_count

    def get_op_path_dir(self,op_request:OpportunityInfo):
        new_tables_dir = self.get_new_table_dir()
        creator = op_request.get_creator()
        path_dir = new_tables_dir + creator
        return path_dir

    def add_new_info(self,op_request:OpportunityInfo): # find which file to be added
        try:
            user_feedback("add_new_info is called")
            if op_request == None:
                error("op_request is none!")
            path_dir = self.get_op_path_dir(op_request)
            self.create_dir_if_not_exists(path_dir)
            all_svg_files = self.get_all_svg_files_in_dir(path_dir)
            if all_svg_files != None and len(all_svg_files) > 0:
                for svg_file_path in all_svg_files: #clear filled files , and mark them as old(move them under to the old files folder..
                    json_file = self.get_json_data_path_from_svg_file(svg_file_path)
                    if (os.path.exists(json_file) is not True):
                        error("Svg file {:s} does not have json file related? svg will be delted? as workaround for now".format(str(svg_file_path)))
                        os.remove(svg_file_path)
                        continue
                    max_point_count = self.find_max_point_count(json_file)
                    if (max_point_count >= self.get_max_point_count()):
                        self.create_statistic_table(svg_file_path)
            name = self.determine_name(op_request)
            left_svg_files = self.get_all_svg_files_in_dir(path_dir)
            if left_svg_files != None and len(left_svg_files)>0:
                matched_svg = [f for f in left_svg_files if f.__contains__(name)]
            else:
                matched_svg = []
            if(len(matched_svg) > 0):
                self.add_new_info_to_svg_file(matched_svg[0],op_request)
            else:
                new_svg_file = self.create_new_svg_file(op_request)[0] # returns also json_data_path in second index..
                self.add_new_info_to_svg_file(new_svg_file,op_request)
        except Exception as e:
            error("Error during add_new_info Error: {:s}".format(str(e)))

    def create_new_svg_file(self,op_request:OpportunityInfo):#Create fresh new svg file , because the old one is copleted max count number that a line can have..
        name = self.determine_name(op_request)
        now = time.strftime('%d_%m_%Y_%H:%M:%S')
        svg_file_name = name+"_"+now + ".svg"
        user_feedback("New svg file created : {:s}".format(str(svg_file_name)))
        data_file_name = self.get_json_data_path_from_svg_file(svg_file_name)
        market_pair = self.get_market_pair_name(op_request)
        path_dir = self.get_op_path_dir(op_request)
        data_file_path = os.path.join(path_dir,data_file_name)
        svg_file_path = os.path.join(path_dir,svg_file_name)
        with open(data_file_path,"w") as json_data:
            first_empty_data = json.dumps({market_pair:[]})
            json_data.write(first_empty_data)

        return [svg_file_path,data_file_path]


    def load_data_file(self,json_file_path:str):
        with open(json_file_path,"r") as data_file:
            data = json.load(data_file)
            return data

    def get_market_pair_name(self,op_info:OpportunityInfo):
        return "(" + op_info.get_currency() + ")" + op_info.get_buy_market() + "-->" + op_info.get_sell_market()

    def add_new_info_to_svg_file(self,file_path:str,op_request:OpportunityInfo):#Add new info the last fresh svg file
        json_file = self.get_json_data_path_from_svg_file(file_path)
        market_pair_name = self.get_market_pair_name(op_request)
        if(os.path.exists(json_file)):
            market_pair_datas  = self.load_data_file(json_file)
        else:
            raise Exception("{:s} Data file not exists?",str(json_file))
        percent = op_request.get_percent()
        market_pair_points = market_pair_datas.pop(market_pair_name,[])
        market_pair_points.append(percent)
        new_market_pair_data_element = {market_pair_name:market_pair_points}
        market_pair_datas.update(new_market_pair_data_element)
        with open(json_file,"w") as json_file:
            data_to_write = json.dumps(market_pair_datas)
            json_file.write(data_to_write)
        self.paint_svg(file_path)
        return



    def paint_svg(self,svg_file_path:str):
        title = svg_file_path
        debug("Arbitrage Table Drawing")
        json_file = self.get_json_data_path_from_svg_file(svg_file_path)
        json_data = self.load_data_file(json_file)
        

        dark_gray = "#212121"
        gold = "#FFD700"
        soft_green = "#009688"
        white = "#FFFFFF"
        custom_style = Style(
            background=dark_gray,
            plot_background= dark_gray,
            foreground= soft_green, # numbers on the y axis
            foreground_strong= white, #x-y axis
            foreground_subtle=soft_green, #cizgiler(lines) x axis lines..
            opacity='.6',
            label_font_size = 30,
            opacity_hover='.9',
            transition='400ms ease-in',
            colors=('#E853A0', '#E8537A', '#E95355', '#E87653', '#E89B53')
        )
   
        line_chart = pygal.Line(style=custom_style ,show_legend=False, height=460)
        #line_chart.title = title
        is_labels_created = False
        keys = json_data.keys()
        for key in keys:
            datas = json_data.__getitem__(key)
            #datas = data.split(' ')
            line_cube = []
            data_count = 0
            for each_data in datas:
                each_data = float("{:0.1f}".format(float(each_data)))
                line_cube.append(float(each_data))
                data_count += 1
            if (is_labels_created == False):
                is_labels_created = True
                line_chart.x_labels = map(str, range(0, data_count))

            line_chart.add(key, line_cube)

        svg_string = line_chart.render()

        byte_array = bytearray(svg_string)

        with open(svg_file_path, 'wb') as outputfile:
            outputfile.write(byte_array)

    @trycatch
    def create_dir_if_not_exists(self,path:str):
        if (os.path.exists(path) is not True):
            try:
                os.makedirs(path)

            except Exception as e:
                error("Error during creating file dir {:s} error: {:s}".format(str(path), str(e)))


    @trycatch
    def get_all_svg_files_in_dir(self,dir_path:str):
        svg_files = []
        files = os.listdir(dir_path)
        for file in files:
            file_path = os.path.join(dir_path,file)
            if file_path.endswith(".svg"):
                svg_files.append(file_path)
        return svg_files
    
    
    @staticmethod
    def find_old_statistics_file(dir_path:str):
        old_files = []
        today = str(date.today())
        today_array = today.split("-")
        today_power = int(today_array[0])*365 + int(today_array[1])*30 + int(today_array[2])
        statistic_directory = dir_path
        all_statistic_files  = [f for f in os.listdir(statistic_directory) if os.path.isfile(os.path.join(statistic_directory, f))]
        for file in all_statistic_files:
            file_array = file.split("_")
            year_of_file = int(file_array[5])
            month_of_file = int(file_array[4])
            day_of_file = int(file_array[3])
            file_power = year_of_file * 365 + month_of_file * 30 + day_of_file
            file_age = today_power - file_power
            #user_feedback("File age is {:d} of file: {:s}".format(int(file_age), str(file)))
            if file_age >= symbols.STATISTIC_TABLE_FILE_EXPIRED_THRESHOLD:
                old_files.append(file)
            
        return old_files
    
    


    @staticmethod
    def remove_too_old_tables():
        error("remote too old tables will be started")
        while True:
            try:            
                old_table_dir = symbols.OLD_TABLE_DIR
                creators = os.listdir(old_table_dir)
                for creator in creators:
                    creator_path = os.path.join(os.path.join(old_table_dir,creator))
                    old_tables = StatisticTableService.find_old_statistics_file(creator_path)
                    try:
                        for table in old_tables:
                            file_path = os.path.join(creator_path, table)
                            os.remove(file_path)                       
                    except Exception as e:
                        error("Error during removing file {:s}".format(str(e)))
            except Exception as e:
                error("Error during cleaning too old statistic table file Err:{:s}".format(str(e)))
            
            time.sleep(4*60*60) #wait 4 hour for next cycle.



    def action(self,request):
        self.add_new_info(request)
    