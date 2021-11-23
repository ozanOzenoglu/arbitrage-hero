import json
import time
import os
import shutil
import pygal
from pygal.style import Style
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from base.crypto_engine.MessageApi.debug import *
from base.services.table_service import TableService

class LiveTableService(TableService):
    
    def __init__(self, path_to_watch: str, patterns: list):
        super().__init__(path_to_watch, patterns)
        self.__max_point_count = symbols.MAX_TABLE_POINT_COUNT
        self.__new_table_dir = symbols.LIVE_TABLES
        self.__old_table_dir = symbols.OLD_TABLE_DIR #TODO:Remove and check if sth goes wrong
        
        
    def remove_first_element(self, file_path:str, op_request:OpportunityInfo):
        json_file = self.get_json_data_path_from_svg_file(file_path)
        market_pair_name = self.get_market_pair_name(op_request)
        if(os.path.exists(json_file)):
            market_pair_datas  = self.load_data_file(json_file)
        else:
            raise Exception("{:s} Data file not exists?",str(json_file))
        
        market_pair_points = market_pair_datas.pop(market_pair_name,[])
        market_pair_points = market_pair_points[1:]
        new_market_pair_data_element = {market_pair_name:market_pair_points}
        market_pair_datas.update(new_market_pair_data_element)
        with open(json_file,"w") as json_file:
            data_to_write = json.dumps(market_pair_datas)
            json_file.write(data_to_write)
        return
    
    
    
    def determine_name(self,op_request:OpportunityInfo):
        buy_market = op_request.get_buy_market()
        sell_market = op_request.get_sell_market()
        currency = op_request.get_currency()
        name = buy_market + "_" + sell_market + "_" + currency 
        return name
    

    def get_max_point_count(self):
        return self.__max_point_count

    def get_old_table_dir(self):
        return self.__old_table_dir
    def get_new_table_dir(self):
        return self.__new_table_dir


    def get_op_path_dir(self,op_request:OpportunityInfo):
        new_tables_dir = self.get_new_table_dir()
        creator = op_request.get_creator()
        path_dir = new_tables_dir + creator
        return path_dir
    
    def add_new_info(self,op_request:OpportunityInfo): # find which file to be added
        path_dir = self.get_op_path_dir(op_request)
        self.create_dir_if_not_exists(path_dir)
        make_trim = False
        all_svg_files = self.get_all_svg_files_in_dir(path_dir)
        if all_svg_files != None and len(all_svg_files) > 0:
            for file in all_svg_files: #clear filled files , and mark them as old(move them under to the old files folder..
                json_file = self.get_json_data_path_from_svg_file(file)
                max_point_count = self.find_max_point_count(json_file)
                if (max_point_count >= self.get_max_point_count()):
                    self.remove_first_element(file, op_request)
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

        
        
