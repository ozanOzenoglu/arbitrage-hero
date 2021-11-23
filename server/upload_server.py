import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

import subprocess
import urllib
import time
import os
import posixpath
import urllib.request, urllib.parse, urllib.error
import cgi
import shutil
import mimetypes
import re
from io import BytesIO
import threading
from library import orderbook, sms

# from api.base.crypto_engine.MessageApi.debug import *
# from api.base.crypto_engine.utils.safe_writer import SafeWriter

HOME = os.path.dirname(os.path.realpath(__file__))

DATA_TO_SEND_PATH = 'data_to_send'

PRIVATE_KEY_FILE = HOME + "/private_key"
SMS_DIR = HOME + "/sms_codes/"
ORDER_BOOKS_DIR = HOME.split('src')[0] + '/order_books/'
KOINEKS_ORDER_BOOK_FILE = ORDER_BOOKS_DIR + "/koineks.json"
PRIVATE_KEY = "osman_is_my_girl"

current_path = os.path.dirname(os.path.realpath(__file__))
ARBITRAGE_INFO_FILE = 'arbitrage_info.json'
DATA_TO_SEND = HOME.split('src')[0] + 'src/data_to_send'



class HttpHandler(BaseHTTPRequestHandler):
    HTTP_HANDLER_BUSY = False
    invalid_payload_error_code = 31
    no_arbitrage_table_found = 32

    file_path_404 = HOME + "/www/404.html"
    index_file_path = HOME + "/www/index.html"
    arbitrage_table_path = HOME + "/www/arbitrage_table.html"

    is_initialised = False
    data_dir = ""
    data_404 = ""
    data_index_html = ""

    arbitrage_table_html_files = {}

    def update_arbitrage_table_files(self):
        HttpHandler.arbitrage_table_html_files = {}

        for file in os.listdir(DATA_TO_SEND):
            if file.endswith(".html"):
                HttpHandler.arbitrage_table_html_files.update({file: os.path.join(DATA_TO_SEND, file)})

    def create_arbitrage_table_page(self):
        self.update_arbitrage_table_files()

        arbitrage_table_html_files_names = HttpHandler.arbitrage_table_html_files.keys()
        links = ""
        for file_name in arbitrage_table_html_files_names:
            address = file_name
            links = links + "<a href =\"" + address + "\>" + file_name + "</a><br>"

        return_html = '''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Arbitrage Management Console!</title>
            </head>
            ''' + links + '''
            <body>

            </body>
            </html>'''

        with open(HttpHandler.arbitrage_table_path, "w") as arbitrage_table_page:
            arbitrage_table_page.seek(0)
            arbitrage_table_page.truncate()
            arbitrage_table_page.write(return_html)

    def find_html_files(self):
        html_files = []
        for file in os.listdir(DATA_TO_SEND):
            if file.endswith(".html"):
                html_files.append(os.path.join(DATA_TO_SEND, file))
        return html_files

    @staticmethod
    def init():
        if (HttpHandler.is_initialised == True):
            return
        HttpHandler.is_initialised = True

        HttpHandler.data_dir = os.path.abspath('../' + DATA_TO_SEND_PATH)

    def is_private_key_valid(self, private_key: str):
        print("is private key valid ,our key {:s} , their key {:s}".format(str(PRIVATE_KEY),str(private_key)))
        print("comparing our private key {:s} to user private key {:s} ".format(str(PRIVATE_KEY),str(private_key)))
        if str(private_key) == str(PRIVATE_KEY):
            return True
        else:
            return False

    def return_error(self, error_code):
        if error_code == HttpHandler.invalid_payload_error_code:
            self.send_error(401, "invalid payload")

    def handle_request(self, request: str, payload: str):
        print("handle_request")
        private_key = ""

        event = ""
        data = ""

        address = request.split('.html')[0]
        address = address[1:]

        if (address[0:].__contains__('api_call') is not True):
            if (address == "index"):
                # self._set_headers('text/html')
                self.return_page(HttpHandler.index_file_path)
            elif (address == "koineks"):
                # self._set_headers('application/json')
                self.return_page(KOINEKS_ORDER_BOOK_FILE)
            elif (address == "arbitrage_table"):
                arbitrage_table_pages = self.find_html_files()
                if (len(arbitrage_table_pages) == 0):
                    HttpHandler.return_error(HttpHandler.no_arbitrage_table_found)
                else:
                    self.create_arbitrage_table_page()
                    self.return_page(HttpHandler.arbitrage_table_path)
            elif request.endswith('.svg'):
                requested_svg_file_list = request.replace('%3E', '').replace('%3C', '').split('.html')
                size = len(requested_svg_file_list)
                requested_svg_file = requested_svg_file_list[size - 1]
                self.return_page(DATA_TO_SEND + "/" + requested_svg_file)
            else:
                requested_arbitrage_table = request.split('.html')[0][1:]
                self.return_page(DATA_TO_SEND + "/" + requested_arbitrage_table + ".html")

        else:  # api calls handle in this block !!
            try:
                if payload == None:
                    print("payload can't be None")
                    self.return_page(HttpHandler.invalid_payload_error_code)
                    return
                payload = json.loads(payload)
            except Exception as e:
                print("There is error during json.loads of payload {:s}".format(str(e)))
            try:
                private_key = payload.__getitem__('private_key')
                event = payload.__getitem__('event')
                try:
                    data = payload.__getitem__('data')
                except Exception as e:
                    print("There is no data of event{:s}".format(event))

            except Exception as e:
                print("There is no event")

            if (private_key != ""):
                valid_key = self.is_private_key_valid(private_key)
                if (valid_key):
                    print("private key is valid")
                    if (event != "" and data != ""):
                        try:
                            ret = self.handle_event(event, data)
                            '''
                            if (ret == 0):
                                self.send_response(200,"success")
                            else:
                                self.send_error(201,"fail") # TODO: return fail content.
                            '''
                        except Exception as e:
                            print("error during handling event {:s}".format(str(e)))
                            self.send_error(201,"fail")

                    else:
                        self.send_error(401, "empty event or data")
                else:
                        self.send_error(31, "Hey motherfucker , why don't you put your keyboard back and go outside and play ball with other kids ?")
            else:
                print("no private key ")
                self.wfile.write(HttpHandler.data_404)

    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.
        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)
        """
        # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.parse.unquote(path))
        words = path.split('/')
        words = [_f for _f in words if _f]
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path


    opportunities_path = '/var/www/html/opportunities/all_opportunities.json'


    def handle_opportunity_file(sel,path:str):
        print("handle_opp file started for path {:s}".format(str(path)))
        time.sleep(1)

        process = subprocess.Popen("cat %s" % (path), shell=True,stdout=subprocess.PIPE)
        stdout = process.communicate()[0]
        data = json.loads(stdout.decode("utf-8"))
        #print("Data GATHERED {:s}".format(str(data)))

        try:
            with open(HttpHandler.opportunities_path, 'r+') as all_opportunities_file:
                    print("{:s} is opened for read".format(str(HttpHandler.opportunities_path)))
                    all_opportunities = {}
                    try:
                        all_opportunities = json.load(all_opportunities_file)
                    except Exception as e:
                        error("Mal formed json type in all_opportunities_file")

                    all_opportunities.update(data)
                    all_opportunities_file.close()

            with open(HttpHandler.opportunities_path, 'wb') as all_opportunities_file:
                    #print("{:s} is opened for write".format(str(HttpHandler.opportunities_path)))
                    byte_array = bytearray(json.dumps(all_opportunities), 'utf8')
                    all_opportunities_file.write(byte_array)
                    #print("DATA MERGED!")


        except Exception as e:
            print('error during read newly uploaded opportunity file {:s}'.format(str(e)))
            return

    def deal_post_data(self):
        content_type = self.headers['content-type']
        if not content_type:
            return (False, "Content-Type header doesn't contain boundary")
        boundary = content_type.split("=")[1].encode()
        remainbytes = int(self.headers['content-length'])
        line = self.rfile.readline()
        remainbytes -= len(line)
        if not boundary in line:
            return (False, "Content NOT begin with boundary")
        line = self.rfile.readline()
        remainbytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line.decode())
        if not fn:
            return (False, "Can't find out file name...")
        path = self.translate_path(self.path)

        file_name = str(fn[0])
        fn = os.path.join(path, fn[0])
        if (fn.__contains__("upload_svg")):
            if (fn.endswith(".svg") is not True):
                error("table file format must be svg")
                return

            fn = fn.replace("upload_svg", "tables")
        elif fn.__contains__("upload_order_books"):
            if (fn.endswith(".json") is not True):
                error("order book type format must be json.")
                return
            fn = "/var/www/html/order_books/"+file_name
        elif fn.__contains__("upload_opportunity_result"):
            if (fn.endswith(".json") is not True):
                error("arbitrage result file format must be json.")
                return
            fn = "/var/www/html/opportunities/"+file_name


        line = self.rfile.readline()
        remainbytes -= len(line)
        #line = self.rfile.readline()
        #remainbytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Can't create file to write, do you have permission to write?")

        preline = self.rfile.readline()
        remainbytes -= len(preline)
        while remainbytes > 0:
            line = self.rfile.readline()
            remainbytes -= len(line)
            if boundary in line:
                preline = preline[0:-1]
                if preline.endswith(b'\r'):
                    preline = preline[0:-1]
                out.write(preline)
                out.close()
                return (True, "'%s'" % fn)
            else:
                out.write(preline)
                preline = line
        return (False, "Unexpect Ends of data.")

    def copyfile(self, source, outputfile):
        """Copy all data between two file objects.
        The SOURCE argument is a file object open for reading
        (or anything with a read() method) and the DESTINATION
        argument is a file object open for writing (or
        anything with a write() method).
        The only reason for overriding this would be to change
        the block size or perhaps to replace newlines by CRLF
        -- note however that this the default server uses this
        to copy binary data as well.
        """
        shutil.copyfileobj(source, outputfile)

    def send_head(self):
        """Common code for GET and HEAD commands.
        This sends the response code and MIME headers.
        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.
        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            if not self.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(301)
                self.send_header("Location", self.path + "/")
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                ret = self.list_directory(path)
                return ret
        ctype = self.guess_type(path)
        try:
            # Always read in binary mode. Opening files in text mode may cause
            # newline translations, making the actual size of the content
            # transmitted *less* than the content-length!
            f = open(path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None
        self.send_response(200)
        self.send_header("Content-type", ctype)
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        return f

    def is_authorized_request(self, path):
        if (path.__contains__('tables') or path.__contains__("order_books") ):
            return True
        else:
            return False

    def list_directory(self, path):
        if self.is_authorized_request(path) is False:
            self.send_error(401, "Unauthorized Access")
            return None

        """Helper to produce a directory listing (absent index.html).
        Return value is either a file object, or None (indicating an
        error).  In either case, the headers are sent, making the
        interface the same as for send_head().
        """
        try:
            list = os.listdir(path)
        except os.error:
            self.send_error(404, "No permission to list directory")
            return None
        list.sort(key=lambda a: a.lower())
        f = BytesIO()
        displaypath = cgi.escape(urllib.parse.unquote(self.path))
        f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
        f.write(("<html>\n<title>Directory listing for %s</title>\n" % displaypath).encode())
        f.write(("<body>\n<h2>Directory listing for %s</h2>\n" % displaypath).encode())
        f.write(b"<hr>\n")
        f.write(b"<form ENCTYPE=\"multipart/form-data\" method=\"post\">")
        if (str(path).__contains__("upload")) is True:
            f.write(b"<input name=\"file\" type=\"file\"/>")
            f.write(b"<input type=\"submit\" value=\"upload\"/></form>\n")
        if (path.__contains__("table")):
            f.write(b"Tarihe gore sirali arbitrage tablolarin en gunceli 20 dk onceki piyasa kosullarini gosterir!!!")
            f.write(b"Anlik verileri gosteren mobil uygulama calismalari surmekte..")
            f.write(b"Islem yapmadan once kendi kontorlunuzu lutfen yapin!")
        f.write(b"<hr>\n<ul>\n")
        for name in list:
            fullname = os.path.join(path, name)
            displayname = linkname = name
            # Append / for directories or @ for symbolic links
            if os.path.isdir(fullname):
                displayname = name + "/"
                linkname = name + "/"
            if os.path.islink(fullname):
                displayname = name + "@"
                # Note: a link to a directory displays with @ and links with /
            f.write(('<li><a href="%s">%s</a>\n'
                     % (urllib.parse.quote(linkname), cgi.escape(displayname))).encode())
        f.write(b"</ul>\n<hr>\n</body>\n</html>\n")
        length = f.tell()
        f.seek(0)
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-Length", str(length))
        self.end_headers()
        return f

    def guess_type(self, path):
        """Guess the type of a file.
        Argument is a PATH (a filename).
        Return value is a string of the form type/subtype,
        usable for a MIME Content-type header.
        The default implementation looks the file's extension
        up in the table self.extensions_map, using application/octet-stream
        as a default; however it would be permissible (if
        slow) to look inside the data to make a better guess.
        """

        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()  # try to read system mime.types
    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',  # Default
        '.py': 'text/plain',
        '.c': 'text/plain',
        '.h': 'text/plain',
    })

    def read_payload(self):
        len = self.headers.get('Content-Length')
        post_body = self.rfile.read(int(len))
        payload = post_body.decode()

        return payload

    def return_text_message(self, message: str):
        self._set_headers("application/json")
        self.wfile.write(message.encode("UTF-8"))


    def handle_event(self, event: str, data: dict):
        if event == 'add_arbitrage_info':
            print("add_arbitrage_info event is recevied")
            HttpHandler.arb_writer.write(data)

        elif event == "fetch_koineks_orderbook":
            print("fetch_koineks_order_book recevied!")
            self.path = KOINEKS_ORDER_BOOK_FILE

        elif event == "update_sms_code":
            ts = time.time() * 1000 #ms
            sms_content = data.get('data', {})
            sms_content += " update_time:"  + str(ts)
            sms_file = data.get("sms_name", {})
            sms.create_sms_file(sms_file, sms_content)
            self.return_text_message("success")

        elif event == "get_sms_code":
            type = data
            sms_code = sms.get_code(type)
            if sms_code:
                self.return_text_message(sms_code)
            else:
                print("No sms code found.")

        elif event == "new_orderbook":
            print("new_orderbook event handling.")
            '''here orderbook_name is actually market_name'''
            market_name = data.get("orderbook_name", "")
            ob_data = data.get("data", {})
            orderbook.create_new_orderbook(market_name, ob_data)
            self.return_text_message("success")
        elif event == "get_orderbook":
            if data:
                market = data
            print("get_orderbook event handling.")
            ob = orderbook.get_file_content(market)
            self.return_text_message(ob)
        else:
            print("unsupported event {:s}".format(str(event)))
            self.return_text_message("unsupported event {:s}".format(str(event)))
            return -1

    def return_page(self, file: str):
        if (file.endswith("json") is not True):
            self._set_headers('text/html')
        else:
            self._set_headers("application/json")

        try:
            with open(file, 'rb') as page:
                self.wfile.write(page.read())
        except Exception as e:
            print(str(e))
            self.wfile.write(HttpHandler.data_404)

    def _set_headers(self, type):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def do_GET(self):
        print("do_get")
        try:
            if (self.path.__contains__("api_call")):
                return self._do_GET()
            HttpHandler.HTTP_HANDLER_BUSY = True
            print("http handler busy set true!")
            """Serve a GET request."""

            print("Get request by: {:s}".format(str(self.client_address)))
            if self.is_authorized_request(self.path) is not True:
                self.send_error(401, "Unauthorized Access")
                return

            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
        except Exception as e:
            print("Error during handing get request {:s}".format(str(e)))
        finally:
            HttpHandler.HTTP_HANDLER_BUSY = False


    def _do_GET(self):
        print("_do_get")
        try:
            HttpHandler.HTTP_HANDLER_BUSY = True
            HttpHandler.init()
            try:
                payload = self.read_payload()
                if (payload.__contains__("'")):
                    print("payload sent in wrong format for json.loads ' will be changed as \" ")
                    payload = payload.replace("'","\"")
                if (payload.__contains__('\n')):
                    payload = payload.replace("\n"," ");
            except Exception as e:
                payload = None
            self.handle_request(self.path,payload)
            '''
            f = self.send_head()
            if f:
                self.copyfile(f, self.wfile)
                f.close()
            '''

        except Exception as e:
            print("error druing do_Get {:s}".format(str(e)))
        finally:
            HttpHandler.HTTP_HANDLER_BUSY = False


    def do_HEAD(self):
        self._set_headers('text/html')

    def do_POST(self):
        try:
            if (self.path.__contains__("api_call")):
                return self._do_GET()

            HttpHandler.HTTP_HANDLER_BUSY = True
            #print("Post request by: {:s}".format(str(self.client_address)))

            """Serve a POST request."""
            if (self.path.__contains__('upload')):
                r, info = self.deal_post_data()

                #print((r, info, "by: ", self.client_address))
                f = BytesIO()
                f.write(b'<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">')
                f.write(b"<html>\n<title>Upload Result Page</title>\n")
                f.write(b"<body>\n<h2>Upload Result Page</h2>\n")
                f.write(b"<hr>\n")
                if r:
                    f.write(b"<strong>Success:</strong>")
                else:
                    f.write(b"<strong>Failed:</strong>")
                f.write(info.encode())
                f.write(("<br><a href=\"%s\">back</a>" % self.headers['referer']).encode())
                f.write(b"<hr><small>Powerd By: bones7456, check new version at ")
                f.write(b"<a href=\"http://li2z.cn/?s=SimpleHTTPServerWithUpload\">")
                f.write(b"here</a>.</small></body>\n</html>\n")
                length = f.tell()
                f.seek(0)
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.send_header("Content-Length", str(length))
                self.end_headers()
                if f:
                    self.copyfile(f, self.wfile)
                    f.close()
                if (info.__contains__('opportunity') and r == True):
                    op_handler = threading.Thread(target=HttpHandler.handle_opportunity_file, args=[self, info])
                    op_handler.start()
                    #self.handle_opportunity_file(info)
                #print("do_POST upload is finished")
            else:
                self.send_error(404, "Page Not Found")
                return None
        except Exception as e:
            print("Error during handing post request {:s}".format(str(e)))
        finally:
            HttpHandler.HTTP_HANDLER_BUSY = False


class GarbageCollector: #delete garbage files

    @classmethod
    def remove_garbages(cls):
        try:
            removed_file = 0
            TABLES_DIR = os.path.abspath("") + "/tables/"
            yesterday = datetime.datetime.now().day -1
            month = datetime.datetime.now().month

            for file in os.listdir(TABLES_DIR):
                try:
                    day_of_file = int(file.split("-")[2].split("_")[0])
                    month_of_file = int(file.split("-")[1].split("_")[0])


                    if month_of_file < month or day_of_file < yesterday:
                        os.remove(TABLES_DIR + file)
                        removed_file = removed_file + 1
                except Exception as e:
                    print("Wrong format file name {:s}".format(str(file)))

            print("{:d} garbage(s) are/is deleted".format(removed_file))
        except Exception as e:
            print("Error during removing garbages {:s}".format(str(e)))

class HttpServerService():
    local_port = 8000
    public_port = 80

    local_address = "http://localhost:" + "{:d}".format(int(local_port))

    def __init__(self,port):
        self.__shutdown_request = False
        self.__port = port
        server_address = ('',port)
        self.__httpd = HTTPServer(server_address, HttpHandler)

    def set_port(self, port: int):
        self.__port = port

    def get_httpd(self):
        return self.__httpd


    def stop_service(self):

        while(HttpHandler.HTTP_HANDLER_BUSY == True):
            wait_time = 0
            print("Shutdown wait handler to be ready to close..")
            time.sleep(1)
            wait_time = wait_time + 1
            if (wait_time > 10): # if waited more than 10 sec , close it anyway.
                print("waited more than 10 sec. SHUT DOWN MOTHA FUCKKA")
                break
        self.__shutdown_request = True
        print("stop_service set shutdown_request flag")


    def handle_requests(self):
        print("handle requests func started")
        while self.__shutdown_request == False:
            self.__httpd.handle_request()
            print("One request is handled sucessfully!")
        print("handle requests funct stopped")

    def start_service(self):
        httpd = self.get_httpd()
        self.__shutdown_request = False

        http_service_thread = threading.Thread(target=self.handle_requests, name="REQUEST_HANDLER")
        http_service_thread.start()
        print("service thread started")
        return http_service_thread


if __name__ == "__main__":
    GarbageCollector.remove_garbages()

    service = HttpServerService(HttpServerService.local_port)

    while True:
        service.start_service()
        time.sleep(60)
        service.stop_service()
        print("stopped")
        time.sleep(1)

    exit(0)
