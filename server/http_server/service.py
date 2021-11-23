from http.server import HTTPServer
import threading

from api.base.crypto_engine.MessageApi.debug import *


class HttpServerService:

    def __init__(self, handler_class, port):
        self.server_address = ('', port)
        self.port = port
        self.server = HTTPServer(self.server_address, handler_class)
        self.http_server_thread = None
        
    def run_forever(self):
        try:
            self.http_server_thread = threading.Thread(target = self.server.serve_forever, name="HttpServer")
            self.http_server_thread.start()
            user_feedback("started new server on port {}".format(self.port))
            self.http_server_thread.join()
        except KeyboardInterrupt:
            error("KeyboardInterrept handled we will be shutting down the web server...")
            self. server.socket.close()

    def stop(self):
        try:
            self.server.shutdown()
            self.server.socket.close()
            user_feedback("http server is closed")
            return self.http_server_thread.isAlive()
        except Exception as e:
            error("Exception ocured during stoping http server {:s}".format(str(e)))

    def is_server_alive(self):
        return self.http_server_thread.isAlive