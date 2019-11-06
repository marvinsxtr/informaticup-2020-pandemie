#!/usr/bin/env python3

from bottle import Bottle, request, BaseRequest

from gevent import monkey
from gevent.pywsgi import WSGIServer

from threading import Thread

import time
import logging

BaseRequest.MEMFILE_MAX = 1024 * 1024
SLEEP_TIME = 0.01
monkey.patch_all()


def start_server(handler, port=50123, log=None):
    """
    Starts a WSGI Server listening on the provided port.
    It passes the json it gets from the post request to the handler.
    :param handler: handler function that performs the simulation, should return a valid json answer
    :param port: port for the server to listen on
    :param quiet: whether the server should show debug output
    :return: None
    """

    app = Bottle()

    def begin():
        server.serve_forever()

    @app.post("/")
    def index():
        game = request.json
        # print(f'round: {game["round"]}, outcome: {game["outcome"]}')

        return handler.solve(game, server)

    server = WSGIServer(('127.0.0.1', port), app, log=log)

    # start server thread
    server_thread = Thread(target=begin)
    server_thread.daemon = True
    server_thread.start()

    # wait until the game finished
    while not server.closed:
        time.sleep(SLEEP_TIME)
