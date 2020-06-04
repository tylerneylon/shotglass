#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" shotglass.py

    A micro-library to provide basic support for a Python-based server.

    See the file sg_example.py for a usage example.

    The general usage of shotglass is to register routes by calling
    shotglass.register_routes(), and then to run the server by calling
    shotglass.run_server().

    A single route is given as a list like this:

        [<string for the route>, <python handler fn>, <optional keywords>]

    eg, <string for the route> = /my/$var_a$/path/
    When variables are in a route, they become the first parameters handed to
    the handler function.

    The <optional keywords> element is a list of strings. Shotglass passes
    through url query values whose key is an element of this list. Those values
    are given to the handler function as Python keywords in the function's
    arguments.
"""


# _______________________________________________________________________
# Imports

import http.server
import json
import os
import socketserver
import sys
import threading
from urllib.parse import parse_qsl, unquote, urlparse

import sg_debug
from sg_debug import debug_print


# _______________________________________________________________________
# Constants and globals

PRODUCTION_PORT = 80
DEBUG_PORT = 8080
port = PRODUCTION_PORT  # This is changed to DEBUG_PORT in debug mode.

# Shotglass uses semantic versioning 2.0.0: https://semver.org/
VERSION = '0.0.0'

# This is a sentinal return object to identify when routing has failed.
BAD_PATH = {}

is_debug_mode = False

server = None


# _______________________________________________________________________
# Internal functions

def _check_path_match(path, template):
    """ Return `does_match`, `args`. The first is a boolean indicating a match,
        while `args` is a list of matched template strings when they match.
    """

    args = []
    path_terms = path.split('/')
    template_terms = template.split('/')

    if len(path_terms) != len(template_terms):
        return False, args

    for p_term, t_term in zip(path_terms, template_terms):
        if len(t_term) > 0 and t_term[0] == '$' and t_term[-1] == '$':
            args.append(unquote(p_term.replace('_', ' ')))
        elif p_term.lower() != t_term.lower():
            return False, args

    return True, args

def _route_path(method, path, data=None, **kwargs):

    global all_routes

    routes = all_routes[method]

    # At this point it's important that the templates are sorted longest to
    # shortest. That should be handled by the sorting done in register_routes().
    for route in routes:
        does_match, args = _check_path_match(path, route[0])
        if not does_match:
            continue
        fn = route[1]
        accepted_keywords = route[2] if len(route) >= 3 else []
        kwargs = { k:v for k, v in kwargs.items() if k in accepted_keywords }
        if method == 'POST':
            return fn(*args, data, **kwargs)
        if method == 'GET':
            return fn(*args, **kwargs)

    return BAD_PATH

def parse_data(data):
    return json.loads(data)

def enter_debug_mode(checkpoint_interval=None):

    global is_debug_mode, port

    print('Entering debug mode.')

    is_debug_mode = True
    # Use a different port to avoid debug mode in production.
    port = DEBUG_PORT
    sg_debug.do_debug_print = True


# _______________________________________________________________________
# Classes

class ShotGlassHandler(http.server.BaseHTTPRequestHandler):

    # ______________________________________________________________________
    # Utility methods.

    def _init_response(self, content_type):
        """ This is meant as a high-level general setup for both HEAD and GET
            requests. """
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.end_headers()

    # ______________________________________________________________________
    # HTTP method handlers.

    def do_HEAD(self):
        self._init_response()

    def _do_COMMON(self, method, data=None):

        parsed = urlparse(self.path)
        kwargs = dict(parse_qsl(parsed.query))
        path = parsed.path
        response = None
        try:
            response = _route_path(method, path, data, **kwargs)
        except:
            threading.Thread(target=server.shutdown, daemon=True).start()
            raise

        if response is BAD_PATH:
            self.send_error(404, message='Unsupported path: %s' % path)
            return

        if type(response) is bytes:
            content_type = 'text/html'
        else:
            content_type = 'application/json'
            response = json.dumps(response).encode('utf-8') + b'\n'

        self._init_response(content_type)
        self.wfile.write(response)

    def do_GET(self):

        debug_print('GET Request:', self.path)
        self._do_COMMON('GET')

    def do_POST(self):

        debug_print('POST Request:', self.path)

        data = None

        # There may legitimately be no data. But if there is some, read it.
        data_len_list = self.headers.get_all('content-length')
        if data_len_list and len(data_len_list) > 0:
            data_len = int(data_len_list[-1])
            data = self.rfile.read(data_len).decode('utf-8')

        self._do_COMMON('POST', data)


# _______________________________________________________________________
# Public functions

def register_routes(GET_routes, POST_routes):

    global all_routes

    all_routes = {
        'GET':  sorted(GET_routes,  key=lambda x: len(x[0]), reverse=True),
        'POST': sorted(POST_routes, key=lambda x: len(x[0]), reverse=True)
    }

def run_server(exit_on_error=False, checkpoint_interval=None):

    global server

    if len(sys.argv) > 1 and sys.argv[1] == '--debug':
        enter_debug_mode()

    mode_name = 'debug' if is_debug_mode else 'production'
    print(f'*** {mode_name} mode ***')

    # Initiate the local HTTP server.
    server = socketserver.TCPServer(
            ('', port),
            ShotGlassHandler,
            False  # Delay binding to allow addr re-use.
    )
    server.allow_reuse_address = True

    try:
        server.server_bind()
        server.server_activate()
        print('shotglass serving at port %d.' % port)
        debug_print(f'My pid is {os.getpid()}.')
        server.serve_forever()

    except KeyboardInterrupt:
        server.shutdown()
        print('\nThank you for using shotglass!')
        sys.exit(0)
