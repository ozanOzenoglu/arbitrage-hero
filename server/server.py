import os
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import threading

from api.base.crypto_engine.MessageApi.debug import *
from api.base.crypto_engine.utils.safe_writer import SafeWriter

HOME  = os.path.dirname(os.path.realpath(__file__))

DATA_TO_SEND_PATH = 'data_to_send'

PRIVATE_KEY_FILE= HOME+"/private_key"
ORDER_BOOKS_DIR = HOME.split('src')[0] + 'src/order_books'
KOINEKS_ORDER_BOOK_FILE = ORDER_BOOKS_DIR + "/koineks.json"
PRIVATE_KEY = ""
with open(PRIVATE_KEY_FILE,"r") as private_key_file:
    PRIVATE_KEY = private_key_file.read()


current_path  = os.path.dirname(os.path.realpath(__file__))
ARBITRAGE_INFO_FILE = 'arbitrage_info.json'
DATA_TO_SEND = HOME.split('src')[0] + 'src/data_to_send'




class S(BaseHTTPRequestHandler):

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
        S.arbitrage_table_html_files = {}

        for file in os.listdir(DATA_TO_SEND):
            if file.endswith(".html"):
                S.arbitrage_table_html_files.update( {file : os.path.join(DATA_TO_SEND, file) } )



    def create_arbitrage_table_page(self):
        self.update_arbitrage_table_files()

        arbitrage_table_html_files_names = S.arbitrage_table_html_files.keys()
        links = ""
        for file_name in arbitrage_table_html_files_names:
            address = file_name
            links = links + "<a href =\""+ address + "\>" + file_name +  "</a><br>"

        return_html = '''<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Arbitrage Management Console!</title>
            </head>
            ''' + links +  '''
            <body>
            
            </body>
            </html>'''

        with open(S.arbitrage_table_path,"w") as arbitrage_table_page:
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
        if (S.is_initialised == True):
            return
        S.is_initialised = True

        S.data_dir = os.path.abspath('../' + DATA_TO_SEND_PATH)

    def is_private_key_valid(self,private_key:str):
        return  private_key == PRIVATE_KEY

    def return_error(self,error_code):
        if error_code == S.invalid_payload_error_code:
            S.wfile.write("invalid payload!")

    def handle_request(self, request: str, payload:str):

        private_key =""


        event =""
        data = ""

        address = request.split('.html')[0]
        address = address[1:]

        if ( address[0:].__contains__('api_call') is not True):
            if (address == "index") :
                #self._set_headers('text/html')
                self.return_page(S.index_file_path)
            elif (address == "koineks") :
                #self._set_headers('application/json')
                self.return_page(KOINEKS_ORDER_BOOK_FILE)
            elif (address == "arbitrage_table"):
                arbitrage_table_pages = self.find_html_files()
                if (len(arbitrage_table_pages) == 0):
                    S.return_error(S.no_arbitrage_table_found)
                else:
                    self.create_arbitrage_table_page()
                    self.return_page(S.arbitrage_table_path)
            elif request.endswith('.svg'):
                requested_svg_file_list = request.replace('%3E', '').replace('%3C', '').split('.html')
                size = len(requested_svg_file_list)
                requested_svg_file = requested_svg_file_list[size-1]
                self.return_page(DATA_TO_SEND + "/" + requested_svg_file)
            else:
                requested_arbitrage_table = request.split('.html')[0][1:]
                self.return_page(DATA_TO_SEND + "/" + requested_arbitrage_table + ".html")

        else: # api calls handle in this block !!
            try:
                if payload == None:
                    error("payload can't be None")
                    self.return_page(S.invalid_payload_error_code)
                    return

                payload = json.loads(payload)
                private_key = payload.__getitem__('private_key')
            except Exception as e:
                print("There is no private key")
            try:
                event = payload.__getitem__('event')
                try:
                    data = payload.__getitem__('data')
                except Exception as e:
                    print("There is no data of event{:s}".format(event))

            except Exception as e:
                print("There is no event")


            if(private_key != ""):
                valid_key = self.is_private_key_valid(private_key)
                if (valid_key):
                    if (event != "" and data !=""):
                        self.handle_event(event,data)
                    requested_page = self.path
                    self.return_page(requested_page)
            else:
                print("no private key ")
                self.wfile.write(S.data_404)



    def read_payload(self):
        len = self.headers.get('Content-Length')
        post_body = self.rfile.read(int(len))
        payload = post_body.decode()
        
        return payload

    def handle_event(self,event:str,data:dict):
        if (event == 'add_arbitrage_info'):
            print("add_arbitrage_info event is recevied")
            print("Data is {:s}".format(str(data)))
            S.arb_writer.write(data)
        elif (event == "fetch_koineks_orderbook"):
            print("fetch_koineks_order_book recevied!")
            self.path = KOINEKS_ORDER_BOOK_FILE
        pass

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
            self.wfile.write(S.data_404)

    def _set_headers(self,type):
        self.send_response(200)
        self.send_header('Content-type', type)
        self.end_headers()

    def do_GET(self):
        S.init()
        try:
            payload = self.read_payload()
        except Exception as e:
            payload = None
        self.handle_request(self.path,payload)


    def do_HEAD(self):
        self._set_headers('text/html')

    def do_POST(self):
        self._set_headers('text/html')
        print ("in post method")
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))

        self.send_response(200)
        self.end_headers()


        self.wfile.write("deneme")
        return


class HttpServerService():

    local_port = 8081
    public_port = 80

    local_address = "http://localhost:" + "{:d}".format(int(local_port))

    def __init__(self):
        self.__port = 0

    def set_port(self, port: int):
        self.__port = port
    def start_new_server_thread(port):
        service = HttpServerService()
        service.set_port(port)

        http_service_thread = threading.Thread(target=service.run, name="HTTPSERVER")
        http_service_thread.start()
        return http_service_thread

    def run(server_class=HTTPServer, handler_class=S, port=8081):
        server_address = ('', port)
        httpd = server_class(server_address, handler_class)
        print('Starting httpd...')
        httpd.serve_forever()



