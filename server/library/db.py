from api.third_party import redis
import json
class DB:
    r = None

    @staticmethod
    def init(hostname,port,db):
        DB.r = redis.Redis(host=hostname,
        port=port,
        db=db)


    @staticmethod
    def get_val(key):

        if(DB.r == None):
            raise Exception("Connection not created")
        ret = DB.r.get(key)
        if (ret == None):
            return None
        if type(ret) == bytes:
            ret = ret.decode("UTF-8")
        ret = json.loads(ret)
        ret = json.dumps(ret,sort_keys=True)
        return ret

    @staticmethod
    def set_val(key,val):
        if type(val) == type({}):
            val = str(json.dumps(val))
        if(DB.r == None):
            raise Exception("Connection not created")
        return DB.r.set(key,val)
