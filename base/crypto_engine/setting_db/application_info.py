from base.crypto_engine.setting_db.info import Info
from base.crypto_engine.setting_db.setting_message import Message


class ApplicationInfo(Info):
    def __init__(self,arbitrage_options:dict,simulator_enabled:bool,table_service_enabled:bool,koineks_handler_options:dict,
                 btcturk_handler_options:dict,koineks_acc_info:dict,btcturk_acc_info:dict,koineks_ob_fetcher_op:dict,
                 ob_fresh_guy_enabled:bool,manager_options,api_service_options, statistic_service_enabled:bool):
        self.__arbitrage_options = arbitrage_options
        self.__simulator_enabled = simulator_enabled
        self.__table_service_enabled = table_service_enabled
        self.__koineks_handler_options = koineks_handler_options
        self.__btcturk_handler_options = btcturk_handler_options
        self.__koineks_acc_info = koineks_acc_info
        self.__btcturk_acc_info = btcturk_acc_info
        self.__koineks_ob_ops = koineks_ob_fetcher_op
        self.__ob_fresh_guy_enabled = ob_fresh_guy_enabled
        self.__manager_options = manager_options
        self.__api_service_options = api_service_options
        self.__statistic_service_enabled = statistic_service_enabled
        self._json_message = ApplicationInfoMsg(self)


    def get_ob_fresh_guy_enabled(self):
        return self.__ob_fresh_guy_enabled
    def get_arbitrage_files(self):
        enabled_files = []
        arbitrage_files_d = self.__arbitrage_options.__getitem__("arbitrage_files")
        arbitrage_files = arbitrage_files_d.keys()
        for file in arbitrage_files:
            if (arbitrage_files_d.__getitem__(file) == True):
                enabled_files.append(file)
        return enabled_files

    def get_op_finder_enabled(self):
        op_finder_enabled = self.__arbitrage_options.__getitem__("op_finder_enabled")
        return op_finder_enabled
    def get_statistis_service_enabled(self):
        return self.__statistic_service_enabled

    def get_api_service_options(self):
        return self.__api_service_options
    def get_api_service_port(self):
        return self.__api_service_options.__getitem__("port")
    def get_api_service_pk(self):
        return self.__api_service_options.__getitem__("private_key")
    def get_api_service_enabled(self):
        return self.__api_service_options.__getitem__("enabled")

    def get_arbitrage_options(self):
        return self.__arbitrage_options
    def get_simulator_enabled(self):
        return self.__simulator_enabled
    def get_table_service_enabled(self):
        return self.__table_service_enabled
    def get_koineks_handler_options(self):
        return self.__koineks_handler_options
    def get_btcturk_handler_options(self):
        return self.__btcturk_handler_options
    def get_koineks_acc_info(self):
        return self.__koineks_acc_info
    def get_btcturk_acc_info(self):
        return self.__btcturk_acc_info

    def get_koineks_ob_fetcher_ops(self):
        return self.__koineks_ob_ops

    def get_log_to_file_enabled(self):
        return self.__manager_options.__getitem__("log_to_file")

    def get_manager_options(self):
        return self.__manager_options
    def get_manager_debug_level(self):
        return self.__manager_options.__getitem__("debug_level")

    def get_koineks_ob_headless(self):
        return self.__koineks_ob_ops.__getitem__("headless")
    def get_koineks_ob_min_cycle_time(self):
        return self.__koineks_ob_ops.__getitem__("min_cycle_time")
    def get_koineks_ob_driver_name(self):
        return self.__koineks_ob_ops.__getitem__("driver_name")
    def get_koineks_ob_enabled(self):
        return self.__koineks_ob_ops.__getitem__("enabled")

    def get_koineks_acc(self):
        return self.__koineks_acc_info.__getitem__("acc")
    def get_koineks_password(self):
        return self.__koineks_acc_info.__getitem__("password")

    def get_btcturk_acc(self):
        return self.__btcturk_acc_info.__getitem__("acc")
    def get_btcturk_password(self):
        return self.__btcturk_acc_info.__getitem__("password")

    def get_arbitrage_file_count(self):
        return len(self.get_arbitrage_files())
    def get_arbitrage_spend_money(self):
        return self.__arbitrage_options.__getitem__("spend_money")
    def get_arbitrage_spend_money_currency(self):
        return self.__arbitrage_options.__getitem__("spend_money_currency")
    def get_arbitrage_mode(self):
        return self.__arbitrage_options.__getitem__("arbitrage_mode")
    def get_arbitrage_enabled(self):
        return self.__arbitrage_options.__getitem__("enabled")
    def get_koineks_handler_count(self):
        return self.__koineks_handler_options.__getitem__("count")

    def get_koineks_handler_driver_name(self):
        return self.__koineks_handler_options.__getitem__("driver_name")

    def get_koineks_handler_headless(self):
        return self.__koineks_handler_options.__getitem__("headless")

    def get_btcturk_handler_count(self):
        return self.__btcturk_handler_options.__getitem__("count")

    def get_btcturk_handler_driver_name(self):
        return self.__btcturk_handler_options.__getitem__("driver_name")

    def get_btcturk_handler_headless(self):
        return self.__btcturk_handler_options.__getitem__("headless")

    def set_arbitrage_options(self,val):
        self.__arbitrage_options = val
    def set_simulator_enabled(self,val):
        self.__simulator_enabled = val
    def set_table_service_enabled(self,val):
        self.__table_service_enabled = val
    def set_koineks_handler_options(self,val):
        self.__koineks_handler_options = val
    def set_btcturk_handler_options(self,val):
        self.__btcturk_handler_options = val
    def set_koineks_acc_info(self,val):
        self.__koineks_acc_info = val
    def set_btcturk_acc_info(self,val):
        self.__btcturk_acc_info = val



    @staticmethod
    def json_to_instance(data:dict):
        statistic_service_enabled = data.__getitem__("statistic_service_enabled")
        api_service_options = data.__getitem__("api_service_options")
        manager_options = data.__getitem__("manager_options")
        ob_fresh_guy_enabled = data.__getitem__("ob_fresh_guy_enabled")
        arbitrage_options = data.__getitem__("arbitrage_options")
        simulator_enabled = data.__getitem__("simulator_enabled")
        table_service_enabled = data.__getitem__("table_service_enabled")
        koineks_handler_options = data.__getitem__("koineks_handler_options")
        btcturk_handler_options = data.__getitem__("btcturk_handler_options")
        koineks_acc_info = data.__getitem__("koineks_acc_info")
        btcturk_acc_info = data.__getitem__("btcturk_acc_info")
        koineks_ob_ops = data.__getitem__("koineks_ob_fetcher_options")
        return ApplicationInfo(arbitrage_options,simulator_enabled,table_service_enabled,
                               koineks_handler_options,btcturk_handler_options,koineks_acc_info,btcturk_acc_info,koineks_ob_ops,
                               ob_fresh_guy_enabled,manager_options,api_service_options,statistic_service_enabled)





class ApplicationInfoMsg(Message):
    def __init__(self,setting:ApplicationInfo):
        self.__relevent_setting = setting


    def _to_string(self):
        ins = self.__relevent_setting
        result  = {
                   "ob_fresh_guy_enabled":ins.get_ob_fresh_guy_enabled(),
                   "arbitrage_options":ins.get_arbitrage_options(),
                   "simulator_enabled":ins.get_simulator_enabled(),
                   "table_service_enabled":ins.get_table_service_enabled(),
                   "koineks_handler_options":ins.get_koineks_handler_options(),
                   "btcturk_handler_options":ins.get_btcturk_handler_options(),
                   "manager_options":ins.get_manager_options(),
                   "koineks_acc_info":ins.get_koineks_acc_info(),
                   "koineks_ob_fetcher_options":ins.get_koineks_ob_fetcher_ops(),
                   "btcturk_acc_info":ins.get_btcturk_acc_info(),
                   "api_service_options": ins.get_api_service_options()

        }
        return result


