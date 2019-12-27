#!/usr/bin/env python3

import time
import threading

from bottle import Bottle, request, BaseRequest, json_loads

from gevent import monkey
from gevent.pywsgi import WSGIServer

from pandemie.operations import end_round
from pandemie.tester import AbstractStrategy

BaseRequest.MEMFILE_MAX = 1024 * 1024
SLEEP_TIME = 0.01

# patch some parts of the standard library to make it gevent compatible
monkey.patch_all()

# initiate bottle
app = Bottle()


class WebServer(threading.Thread):
    """
    Web Server implementation to pass the json request to the strategy and to return our turn.
    This should be run in its own thread and therefore inherits from threading.Thread.

    Example usage:
        server = WebServer(your_strategy)
        server.start()
    """
    def __init__(self, handler, port=50123, log=None):
        """

        :param handler:
        :param port:
        :param log:
        """
        if not isinstance(handler, AbstractStrategy):
            raise ValueError("Strategy is not valid.")

        super().__init__()  # init thread
        self.handler = handler
        self.port = port
        self.log = log

        self.server = WSGIServer(('127.0.0.1', port), app, log=log)
        server = self.server

        @app.post("/")
        def index():
            """

            :return:
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

                return handler.solve(game, server)

            else:
                print("[!] Received an invalid content type, dropping request")
                return ""

    def run(self):
        """

        :return:
        """
        server_thread = threading.Thread(target=self.begin)
        server_thread.daemon = True
        server_thread.start()

        while not self.server.closed:
            time.sleep(SLEEP_TIME)

    def begin(self):
        """

        :return:
        """
        self.server.serve_forever()

    def stop(self):
        """

        :return:
        """
        self.server.stop()
