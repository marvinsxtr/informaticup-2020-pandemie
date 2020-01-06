# !/usr/bin/env python3

import time
import threading

from bottle import Bottle, request, BaseRequest, json_loads

from gevent import monkey
from gevent.pywsgi import WSGIServer

from pandemie.util.operations import end_round
from pandemie.tester import AbstractStrategy

BaseRequest.MEMFILE_MAX = 1024 * 1024
SLEEP_TIME = 0.01

# Patch some parts of the standard library to make it gevent compatible
monkey.patch_all()

# Initiate bottle
app = Bottle()


class WebServer(threading.Thread):
    """
    Web Server implementation to pass the json request to the strategy and to return our turn.
    This should be run in its own thread and therefore inherits from threading.Thread.

    Example usage:
        server = WebServer(your_strategy)
        server.start()
    """
    def __init__(self, handler: AbstractStrategy, port=50123, log=None):
        """
        Constructs the WebServer.
        :param handler: reference to the handler, here an AbstractStrategy implementation
        :param port: port to bind the server to
        :param log: log file, this is passed to the WSGI Server
        """
        if not isinstance(handler, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        super().__init__()  # Init thread
        self.handler = handler
        self.port = port
        self.log = log

        server = WSGIServer(('127.0.0.1', port), app, log=log)
        self.server = server

        @app.post("/")
        def index():
            """
            This gets called upon a http request.

            The json of the request gets passed to the strategy and its solution is returned to the http client.
            If the request is invalid a empty string is returned. We answer a broken json request with the end round
            operation to prevent the game from stopping.

            :return: HTTP response / json answer
            """
            c_type = request.environ.get('CONTENT_TYPE', '').lower().split(';')[0]
            if c_type == 'application/json':
                max_tries = 5
                for _ in range(max_tries):
                    body = request.body.read()
                    if body:
                        try:
                            game = json_loads(body)
                            break
                        except Exception as e:
                            print("[!] ", e)
                            print("[!] Could not decode json, possible because of an internal server error!")
                            return end_round()

                else:
                    print("[!] Could not read request body after %d tries!" % max_tries)
                    return ""

                return handler.solve(game)

            else:
                print("[!] Received an invalid content type, dropping request")
                return ""

    def run(self):
        """
        Start the server in another thread and wait until it is closed.
        :return: None
        """
        server_thread = threading.Thread(target=self.begin)
        server_thread.daemon = True
        server_thread.start()

        while not self.server.closed:
            time.sleep(SLEEP_TIME)

    def begin(self):
        """
        Start to serve. This is blocking.
        :return: None
        """
        self.server.serve_forever()

    def stop(self):
        """
        Stops the server.
        :return: None
        """
        self.server.stop()
