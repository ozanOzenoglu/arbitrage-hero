import json
import time
import os
import shutil
import pygal
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


class TableService(IWatchableWatcherService):

    def __init__(self, path_to_watch: str, patterns: list):
        self.__max_point_count = symbols.MAX_TABLE_POINT_COUNT
        self.__new_table_dir = symbols.NEW_TABLE_DIR
        self.__old_table_dir = symbols.OLD_TABLE_DIR
        self._patterns = patterns
        self._path_to_watch = path_to_watch
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
        path_dir = self.get_op_path_dir(op_request)
        self.create_dir_if_not_exists(path_dir)
        all_svg_files = self.get_all_svg_files_in_dir(path_dir)
        if all_svg_files != None and len(all_svg_files) > 0:
            for file in all_svg_files: #clear filled files , and mark them as old(move them under to the old files folder..
                json_file_path = self.get_json_data_path_from_svg_file(file)
                max_point_count = self.find_max_point_count(json_file_path)
                if (max_point_count >= self.get_max_point_count()): #TODO:Make more moduler with seperated func..
                    data = self.load_data_file(json_file_path)
                    keys = data.keys()
                    for key in keys:
                        val = data.__getitem__(key)
                        val = val[1:]
                        data.update({key:val})
                        with open(json_file_path,"w") as json_file:
                            data_to_write = json.dumps(data)
                            json_file.write(data_to_write)
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


    def action(self,request):
        self.add_new_info(request)
    