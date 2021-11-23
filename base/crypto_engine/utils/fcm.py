import firebase_admin
from firebase_admin import credentials as cretentials
from firebase_admin import messaging as messaging
import os
from base.crypto_engine import symbols
from api.base.crypto_engine.MessageApi.debug import *


class FCM:

    @staticmethod
    def send_topic_message(title,body,message, topic):
        try:
            message =messaging.Message( notification = messaging.Notification( title=title, body=body ),
                                       android=messaging.AndroidConfig( priority='high', notification=messaging.AndroidNotification( sound='default' ), ),
                                       apns=messaging.APNSConfig( payload=messaging.APNSPayload( aps=messaging.Aps( sound='default' ), ), ),
                                       data={"payload":message},
                                       topic=topic,
                                       )
            response = messaging.send(message)
            user_feedback("Fcm Msg Sent: {:s}".format(str(response)))
        except Exception as e:
            error("Error sending fcm msg: {:s}".format(str(e)))     