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
        # due to a parameter mismatch in the WSGIRefServer class
        self.host = host
        self.port = port

        # flag to indicate whether we have closed the server
        self.stopped = False

        # patch the WSGTRefServer.run function at runtime by adding the line "self.srv = srv" at the end of the routine
        # this is necessary to shut down the server after we have
        code = WSGIRefServer.run.__code__
        WSGIRefServer.__code__ = CodeType(code.co_argcount, code.co_kwonlyargcount, code.co_nlocals, code.co_stacksize,
                                          code.co_flags,
                                          code.co_code[:154] + b'\x88\x01_\x0b|\x07j\x0c' + code.co_code[156:],
                                          code.co_consts,
                                          code.co_names[:-1] + ('srv', 'serve_forever'),
                                          code.co_varnames, code.co_filename, code.co_name, code.co_firstlineno,
                                          code.co_lnotab, code.co_freevars, code.co_cellvars,
                                          )

    def shutdown(self):
        self.stopped = True  # set the stop flag

        if hasattr(self, "srv"):
            self.srv.shutdown()
            self.srv.server_close()

        else:
            raise RuntimeError("Could not patch WSGIRefServer.run!")

    def is_alive(self):
        return not self.stopped


def start_server(handler, port=50123, quiet=True):
    def begin():
        run(server=server, port=port, quiet=quiet)

    server = MyServer(host="localhost", port=port)

    @post("/")
    def index():
        game = request.json
        print(f'round: {game["round"]}, outcome: {game["outcome"]}')

        if game["outcome"] == "loss" or game["outcome"] == "win":
            server.shutdown()

        # warning, we actually do not send a last response after the game finished
        # todo: check the unknown behaviour of the ic20 tool

        return handler.solve(game)

    server_thread = Thread(target=begin)
    server_thread.daemon = True
    server_thread.start()

    # wait until the game finished
    while server.is_alive():
        time.sleep(SLEEP_TIME)
