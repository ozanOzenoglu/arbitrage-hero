import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
import os
import sys
module_path = os.path.dirname(os.path.abspath(__file__))
module_path = module_path.split('api')[0]
print("{:s} is added to sys paths".format(str(module_path)))
sys.path.append(module_path)
from api.base.crypto_engine import symbols
from api.base.crypto_engine.MessageApi.debug import *



                  
                  
if __name__ == "__main__": 
     
    if(len(sys.argv) < 3):
        message = "Deneme"
        topic = "new_opportunity"

    try:
        cred = credentials.Certificate(symbols.FCM_KEY_PATH)
        firebase_admin.initialize_app(cred)
    except Exception as e:
        error("Error during init fcm: {:s} ".format(str(e)))
    try:
        message =messaging.Message( data={"payload":message},
                                    topic=topic,
                                    )
        response = messaging.send(message)
        user_feedback("Fcm Msg Sent: {:s}".format(str(response)))
    except Exception as e:
        error("Error sending fcm msg: {:s}".format(str(e)))