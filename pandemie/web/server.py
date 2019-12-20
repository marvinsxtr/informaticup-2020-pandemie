#!/usr/bin/env python3

from bottle import Bottle, request, BaseRequest, json_loads

from gevent import monkey
from gevent.pywsgi import WSGIServer

from threading import Thread

import time

BaseRequest.MEMFILE_MAX = 1024 * 1024
SLEEP_TIME = 0.01
monkey.patch_all()


# todo: move this into a class Server(threading.thread)
def start_server(handler, port=50123, log=None):
    """
    Starts a WSGI Server listening on the provided port.
    It passes the json it gets from the post request to the handler.
    :param handler: handler function that performs the simulation, should return a valid json answer
    :param port: port for the server to listen on
    :param log: whether the server should show debug output
    :return: None
    """

    app = Bottle()

    def begin():
        server.serve_forever()

    @app.post("/")
    def index():

        # game = request.json

        # warning! hotfix in place
        # the bottle api sometimes does not read the request body right
        c_type = request.environ.get('CONTENT_TYPE', '').lower().split(';')[0]
        if c_type == 'application/json':
            max_tries = 5
            for _ in range(max_tries):
                body = request.body.read()
                if body:
                    try:
                        game = json_loads(body)
                        break
                    except:
                        raise RuntimeError("Could not decode json...")

            else:
                raise RuntimeError("Could not read request body after %d tries.." % max_tries)

            return handler.solve(game, server)

        else:
            raise RuntimeError("Invalid content type, dropping request")

    server = WSGIServer(('127.0.0.1', port), app, log=log)

    # start server thread
    server_thread = Thread(target=begin)
    server_thread.daemon = True
    server_thread.start()

    # wait until the game finished
    while not server.closed:
        time.sleep(SLEEP_TIME)
