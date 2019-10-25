#!/usr/bin/env python3

from bottle import post, request, run, BaseRequest

BaseRequest.MEMFILE_MAX = 10 * 1024 * 1024


def start_server(handler, port=50123, quiet=True):

    @post("/")
    def index():
        game = request.json
        print(f'round: {game["round"]}, outcome: {game["outcome"]}')
        return handler.solve(game)

    run(host="0.0.0.0", port=port, quiet=quiet)
