

import imaplib
import smtplib
import email
import cgi

from api.base.crypto_engine.MessageApi.debug import *


# note that if you want to get text content (body) and the email contains
# multiple payloads (plaintext/ html), you must parse each message separately.
# use something like the following: (taken from a stackoverflow post)
#from uno import Any


class DecodeError(Exception):
    pass


class AnyMail():


    def __init__(self,username:str,password:str):
        self.__username = username
        self.__password = password



    def decode_string(string):
        for charset in ("utf-8", 'latin-1', 'iso-8859-1', 'us-ascii', 'windows-1252', 'us-ascii'):
            try:
                return cgi.escape(unicode(string, charset)).encode('ascii', 'xmlcharrefreplace')
            except Exception:
                continue
        raise DecodeError("Could not decode string")

    def __get_first_text_block(self, email_message_instance):
        mail = email_message_instance

        content_of_mail = {}
        content_of_mail['text'] = ""
        content_of_mail['html'] = ""

        for part in mail.walk():
            part_content_type = part.get_content_type()
            part_charset = part.get_charsets()
            if part_content_type == 'text/plain':
                part_decoded_contents = part.get_payload(decode=True)
                try:
                    if part_charset[0]:
                        content_of_mail['text'] += cgi.escape(
                            (str(part_decoded_contents), part_charset[0])).encode(
                            'ascii', 'xmlcharrefreplace')
                    else:
                        content_of_mail['text'] += cgi.escape(str(part_decoded_contents)).encode('ascii',
                                                                                                 'xmlcharrefreplace')
                except Exception:
                    try:
                        content_of_mail['text'] += self.decode_string(part_decoded_contents)
                    except DecodeError:
                        content_of_mail['text'] += "Error decoding mail contents."
                        print("Error decoding mail contents")
                continue
            elif part_content_type == 'text/html':
                part_decoded_contents = part.get_payload(decode=True)

                part_decoded_contents = str(part_decoded_contents).replace('\n','').replace('\r','')

                continue
        return part_decoded_contents

    def __get_latest_mail(self):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.__username, self.__password)
        mail.select()
        mail.list()

        result, data = mail.uid('search', None, "ALL")  # search and return uids instead #TODO: replace ALL with UnSeen!


        uids = data[0].split()
        last_index = len(uids) -1

        email_message = None
        while last_index >= 0 :
            latest_email_uid = uids[last_index]
            last_index -= 1
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]

            email_message = email.message_from_bytes(raw_email)
            break

        if email_message is not None:
            return email_message

        else:
            raise Exception("Last Btcturk Mail couldn't retrived")


    def print_last_mail_payload(self):
        try:
            mail = self.__get_latest_mail()
        except Exception as e :
            raise e

        try:
            payload = self.__get_first_text_block(mail)
        except Exception as e:
            raise Exception("Error getting payload of the mail: {:s}".format(str(e)))


        try:
            clean_payload = str(payload).replace('\r','').replace('\n','').replace('=','')
            print(payload)

        except Exception as e:
            raise Exception("Error generating link {:s}".format(str(e)))


class BtcTurkMail:

    def __init__(self,username:str,password:str):
        self.__username = username
        self.__password = password

    def decode_string(string):
        for charset in ("utf-8", 'latin-1', 'iso-8859-1', 'us-ascii', 'windows-1252', 'us-ascii'):
            try:
                return cgi.escape(unicode(string, charset)).encode('ascii', 'xmlcharrefreplace')
            except Exception:
                continue
        raise DecodeError("Could not decode string")

    def __get_first_text_block(self, email_message_instance):
        mail = email_message_instance

        content_of_mail = {}
        content_of_mail['text'] = ""
        content_of_mail['html'] = ""

        for part in mail.walk():
            part_content_type = part.get_content_type()
            part_charset = part.get_charsets()
            if part_content_type == 'text/plain':
                part_decoded_contents = part.get_payload(decode=True)
                try:
                    if part_charset[0]:
                        content_of_mail['text'] += cgi.escape(
                            (str(part_decoded_contents), part_charset[0])).encode(
                            'ascii', 'xmlcharrefreplace')
                    else:
                        content_of_mail['text'] += cgi.escape(str(part_decoded_contents)).encode('ascii',
                                                                                                 'xmlcharrefreplace')
                except Exception:
                    try:
                        content_of_mail['text'] += self.decode_string(part_decoded_contents)
                    except DecodeError:
                        content_of_mail['text'] += "Error decoding mail contents."
                        print("Error decoding mail contents")
                continue
            elif part_content_type == 'text/html':
                part_decoded_contents = part.get_payload(decode=True)

                part_decoded_contents = str(part_decoded_contents).replace('\n', '').replace('\r', '')

                continue
        return part_decoded_contents


    def __get_latest_btcturk_mail(self):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.__username, self.__password)
        mail.select()
        mail.list()

        result, data = mail.uid('search', None, "ALL")  # search and return uids instead #TODO: replace ALL with UnSeen!


        uids = data[0].split()
        last_index = len(uids) -1

        email_message = None
        while last_index >= 0 :
            latest_email_uid = uids[last_index]
            last_index -= 1
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]

            email_message = email.message_from_bytes(raw_email)
            src_address = email.utils.parseaddr(email_message['From'])  # for parsing "Yuji Tomita" <yuji@grovemade.com>
            if (src_address[1] == "destek@btcturk.com"):
                break

        if email_message is not None:
            return email_message

        else:
            raise Exception("Last Btcturk Mail couldn't retrived")



    def get_btcturk_confirmation_link(self):
        try:
            btcturk_mail = self.__get_latest_btcturk_mail()
        except Exception as e :
            raise e

        try:
            payload = self.__get_first_text_block(btcturk_mail)
        except Exception as e:
            raise Exception("Error getting payload of the mail: {:s}".format(str(e)))


        try:
            clean_payload = str(payload).replace('\r','').replace('\n','').replace('=','')
            code = clean_payload.split("confirm/")[1].split("\"")[0]
            link = "https://www.btcturk.com/cryptowithdrawalemailconfirmation/confirm/"+code

        except Exception as e:
            raise Exception("Error generating link {:s}".format(str(e)))

        return link


class KoineksMail:

    def __init__(self,username:str,password:str):
        self.__username = username
        self.__password = password


    def send_mail(self,to:str,msg:str):

        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.__username, self.__password)
            server.sendmail(self.__username,  to,msg)
        except Exception as e:
            error("Error during sending mail {:s}".format(str(e)))



    def __get_first_text_block(self, email_message_instance):
        maintype = email_message_instance.get_content_maintype()
        if maintype == 'multipart':
            for part in email_message_instance.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload()
        elif maintype == 'text':
            return email_message_instance.get_payload()


    def __get_latest_koineks_mail(self):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.__username, self.__password)
        mail.select()
        mail.list()

        result, data = mail.uid('search', None, "ALL")  # search and return uids instead


        uids = data[0].split()
        last_index = len(uids) -1

        email_message = None
        while last_index >= 0 :
            latest_email_uid = uids[last_index]
            last_index -= 1
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]

            email_message = email.message_from_bytes(raw_email)
            src_address = email.utils.parseaddr(email_message['From'])  # for parsing "Yuji Tomita" <yuji@grovemade.com>
            if (src_address[1] == "robot@koineks.com"):
                break

        if email_message is not None:
            return email_message

        else:
            raise Exception("Last Koineks Mail couldn't retrived")




    def __get_latest_mail_by_sender(self,sender:str):
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(self.__username, self.__password)
        mail.select()
        mail.list()

        result, data = mail.uid('search', None, "ALL")  # search and return uids instead


        uids = data[0].split()
        last_index = len(uids) -1

        email_message = None
        while last_index >= 0 :
            latest_email_uid = uids[last_index]
            last_index -= 1
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]

            email_message = email.message_from_bytes(raw_email)
            src_address = email.utils.parseaddr(email_message['From'])  # for parsing "Yuji Tomita" <yuji@grovemade.com>
            if (src_address[1] == sender):
                break

        if email_message is not None:
            return email_message

        else:
            raise Exception("Last Koineks Mail couldn't retrived")


    def get_sms_verification_code(self):
        try:
            user_feedback("get_sms_verification_code process is started now")
            sms_mail = self.__get_latest_mail_by_sender("btcturk.ozan@gmail.com")
        except Exception as e :
            error("Error occured during get_latest_mail_by_sender {:s}".format(str(e)))
            raise e

        try:
            payload = self.__get_first_text_block(sms_mail)
        except Exception as e:
            error("Error occured while fetching payload from sms_mail {:s}".format(str(e)))
            raise Exception("Error getting payload of the mail: {:s}".format(str(e)))

        code = None
        try:
            code = payload.split("kodunuz:")[1].split(' ')[0]
            code = code[0:6]
        except Exception as e:
            error("Error during parsing sms mail {:s}".format(str(e)))
            raise e

        return code


    def get_koineks_confirmation_link(self):
        try:
            koineks_mail = self.__get_latest_koineks_mail()
        except Exception as e :
            raise e

        try:
            payload = self.__get_first_text_block(koineks_mail)
        except Exception as e:
            raise Exception("Error getting payload of the mail: {:s}".format(str(e)))

        try:
            index = payload.index("confirm-ctransfer/")
        except Exception as e:
            raise Exception("Error finding confirm-ctransfer in payload {:s}".format(str(payload)))

        try:
            confirm = payload[index:(index + 100)]

            link_code = confirm.replace("\r", "").replace("\n", "").replace("=", "").split("Bol")[0]

            link = "https://www.koineks.com/" + link_code
        except Exception as e:
            raise Exception("Error generating link {:s}".format(str(e)))

        return link



