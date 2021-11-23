from api.server.library import paths
from api.base.crypto_engine.setting_db.opportunity_info import OpportunityInfo
from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine.utils import helper
import json


def mark_the_best(ops: dict):
    op_names = ops.keys()
    table_candidate_found = False
    max_percent = -999
    table_candidate_name = None

    for op_name in op_names:
        op = ops.__getitem__(op_name)
        percent = op.__getitem__("percent")
        if (max_percent < percent):
            max_percent = percent
            table_candidate_name = op_name
    op = ops.__getitem__(table_candidate_name)
    op.update({"table_candidate": True})
    user_feedback("{:s} marked as table candidate".format(
            str(table_candidate_name)))


def create_new_ops(content: dict):
    op_dir = paths.get_opportunity_dir()
    try:
        best_op_name = content.pop("best",None)
        if best_op_name == None:
            raise Exception("Best Op is not marked?")
        folder_locked = helper.try_lock_folder(op_dir)
        if folder_locked:
            ops_info = next(iter(content.keys())).split("_")
            op_name = ops_info[0] + "_" + ops_info[1] + "_" + ops_info[2]
            
            op_file = op_dir + "/" + op_name + ".json"
            ret = paths.dump_json(op_file, content)
            best_op = content.__getitem__(best_op_name)
            best_op_instance = OpportunityInfo.json_to_instance(best_op)
            best_op_instance.push() # push to table service
            best_op_dir = paths.get_best_ops_dir()
            best_op_file = best_op_dir + "/" + op_name 
            
            ret = paths.dump_json(best_op_file, best_op)
            if ret != 0:
                raise Exception("Error during saving op into json file")
            user_feedback("Opportunity.py  {:s} create new ops SUCCESS".format(op_name))    
        else:
            raise Exception("Couldn't lock folder {:s}".format(str(op_dir)))

    except Exception as e:
        error("Error ocurred during createing new ops {:s}".format(str(e)))

    finally:
        if folder_locked:
            ret = helper.release_folder_lock_if_any(op_dir)
            if ret:
                user_feedback("Lock released for {:s}".format(str(op_dir)))
            else:
                error("Lock could not release for {:s}".format(str(op_dir)))
    '''
    mark_the_best(data)
    op_names = data.keys()
    for op_name in op_names:
        op = data.__getitem__(op_name)
        type = op.__getitem__("op_info_type")
        table_candidate = op.__getitem__("table_candidate")

        if(table_candidate == True):
            create_new_opportunity(type, {op_name: op}, table_candidate)
        else:
            create_new_opportunity(type, {op_name: op}, table_candidate)
    '''

def create_new_opportunity(type, content: dict, best_marked: bool = False):

    op_name = next(iter(content.keys()))
    if best_marked:
        op_dir = paths.get_best_ops_dir() + type
        op_file = op_dir + "/" + \
            op_name.rstrip("_0123456789") + "_best.json"
    else:
        op_dir = paths.get_opportunity_dir() + type
        op_file = op_dir + "/" + op_name + ".json"

    try:
        paths.path(op_dir)
        op_name = next(iter(content.keys()))
        ret = paths.dump_json(op_file, content)
        if ret != 0:
            error("Error during saving op into json file")
            return
        op_data = content.get(op_name)
        op_info = OpportunityInfo.json_to_instance(op_data)
        is_table_candidate = op_info.get_table_candidate()
        # Double check, about going crayz about this fucking best candidate finding bug!
        if is_table_candidate:
            if(best_marked != True):
                raise Exception(
                    "handler marked it table_candidate but json is missing this info?")
            op_info.push()  # to table service.
    except Exception as e:
        error("error during writing all {} opportunity file: {:s}".format(type, str(e)))


def get_all_best_ops():  # This name should be changed as get_best_ops..
    op_dir = paths.get_best_ops_dir()
    all_ops = paths.files(op_dir)
    all_ops_dict = {}
    for op in all_ops:
        if str(op_dir).endswith("/") is not True:
            op_dir = op_dir + "/"
        content_str = paths.get_json_content(op_dir, op)
        content = json.loads(content_str)
        if content is not None:
            all_ops_dict.update({op: content})

    return json.dumps(all_ops_dict)

def get_opportunity(info: dict):
    buy_market = info.__getitem__("buy_market")
    sell_market = info.__getitem__("sell_market")
    currency = info.__getitem__("currency")
    all_ops_dict = {}

    target_op = "{:s}_{:s}_{:s}".format(
        str(buy_market), str(sell_market), str(currency).upper())
    op_dir = paths.get_opportunity_dir()

    all_ops = paths.files(op_dir)
    for op in all_ops:
        op_file_name = op
        if (str(op_file_name).upper().startswith(str(target_op).upper())):
            content_str = paths.get_json_content(op_dir, op_file_name)
            content = json.loads(content_str)
            if (content is not None):
                all_ops_dict.update({op_file_name: content})
                break

    return json.dumps(all_ops_dict)
