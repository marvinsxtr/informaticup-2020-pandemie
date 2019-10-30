#!/usr/bin/env python3

from bottle import BaseRequest
from bottle import WSGIRefServer
from bottle import run, post, request

from threading import Thread
import time
from types import CodeType

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024
SLEEP_TIME = 0.01


class MyServer(WSGIRefServer):
    def __init__(self, host="127.0.0.1", port=50123):
        super().__init__()

        # overwrite the values in the ServerAdapter.__init__ method because we cannot call it directly
        # due to a parameter mismatch in the WSGIRefServer class constructor
        self.host = host
        self.port = port

        # flag to indicate whether we have closed the server
        self.stopped = False

    # override the WSGTRefServer.run function
    # we added the line "self.srv = srv" at the end of the routine to be able to shut down the server after
    # we have completed the simulation

    def run(self, app):
        from wsgiref.simple_server import WSGIRequestHandler, WSGIServer
        from wsgiref.simple_server import make_server
        import socket

        class FixedHandler(WSGIRequestHandler):
            def address_string(self):  # Prevent reverse DNS lookups please.
                return self.client_address[0]

            def log_request(*args, **kw):
                if not self.quiet:
                    return WSGIRequestHandler.log_request(*args, **kw)

        handler_cls = self.options.get('handler_class', FixedHandler)
        server_cls = self.options.get('server_class', WSGIServer)

        if ':' in self.host:  # Fix wsgiref for IPv6 addresses.
            if getattr(server_cls, 'address_family') == socket.AF_INET:
                class server_cls(server_cls):
                    address_family = socket.AF_INET6

        srv = make_server(self.host, self.port, app, server_cls, handler_cls)
        self.srv = srv  # we added this line to be able to access the former local var srv
        srv.serve_forever()


    def shutdown(self):
        self.stopped = True  # set the stop flag

        if hasattr(self, "srv"):
            self.srv.server_close()
            self.srv.shutdown()

        else:
            raise RuntimeError("Could not patch WSGIRefServer.run!")

    def is_alive(self):
        return not self.stopped


def start_server(handler, port=50123, quiet=True):
    """
    Starts a WSGI Server listening on the provided port.
    It passes the json it gets from the post request to the handler.
    :param handler: handler function that performs the simulation, should return a valid json answer
    :param port: port for the server to listen on
    :param quiet: whether the server should show debug output
    :return: None
    """

    def begin():
        run(server=server, quiet=quiet)

    @post("/")
    def index():
        game = request.json
        # print(f'round: {game["round"]}, outcome: {game["outcome"]}')

        return handler.solve(game, server)

    server = MyServer(host="localhost", port=port)

    # start server thread
    server_thread = Thread(target=begin)
    server_thread.daemon = True
    server_thread.start()

    # wait until the game finished
    while server.is_alive():
        time.sleep(SLEEP_TIME)
