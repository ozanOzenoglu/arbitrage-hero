from api.server.library import paths
from api.server.library.db import DB
import json
import time
from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine import symbols


def get_user_last_seen(user_id):
    users = json.loads(DB.get_val("online_users"))
    last_seen = users.get(user_id,None)
    return last_seen



def init_user():
    users = None
    user_list = {}
    try:
        users = DB.get_val("online_users")
        if users != None and len(users) > 0:
            return
        else:
            DB.set_val("online_users" ,user_list)
            user_feedback("Users are set in redix")
            users = DB.get_val("online_users")
            return users
    except Exception as e:
        error("Error during init users {:s}".format(str(e)))
        


def register_user(user_id):
    
    users = json.loads(DB.get_val("online_users"))
    if users == None:
        raise Exception("Users are not initialized  yeT?")
    last_seen = get_user_last_seen(user_id)
    if last_seen == None:
        DB.set_val("online_users", {user_id:time.time()})
    else: #update last seen status
        now = time.time()
        if now - float(last_seen) > 60:
            users.update({"online_users":{user_id:now}})
            DB.set_val("online_users", users)
    users = DB.get_val("online_users")
    return users
    
def get_online():
    online_users = []
    users = json.loads(DB.get_val("online_users")).get("online_users",None)
    if users == None:
        return 0
    for user in users:
        last_seen = users.get(user)
        if last_seen != None:
            if (time.time() - float(last_seen) < 60):
                online_users.append(user)
    
    onlineUserCount =  len(online_users)
    try:
        with open(symbols.ONLINE_USER_COUNT_FILE, "w") as sf:
            sf.write(str(onlineUserCount))
    except Exception as e:
        print("Error during writing sms code into the file {:s}".format(str(e)))
    finally:
        sf.close()
        return onlineUserCount

    

