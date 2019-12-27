#!/usr/bin/env python3

from bottle import Bottle, request, BaseRequest, json_loads

from gevent import monkey
from gevent.pywsgi import WSGIServer

import threading

import time

from pandemie.operations import end_round

BaseRequest.MEMFILE_MAX = 1024 * 1024
SLEEP_TIME = 0.01
monkey.patch_all()

app = Bottle()


class WebServer(threading.Thread):
    def __init__(self, handler, port=50123, log=None):
        super().__init__()
        self.handler = handler
        self.port = port
        self.log = log

        self.server = WSGIServer(('127.0.0.1', port), app, log=log)
        server = self.server

        @app.post("/")
        def index():
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
        server_thread = threading.Thread(target=self.begin)
        server_thread.daemon = True
        server_thread.start()

        while not self.server.closed:
            time.sleep(SLEEP_TIME)

    def begin(self):
        self.server.serve_forever()

    def stop(self):
        self.server.stop()
