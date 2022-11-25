#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" sg_example.py

    This file illustrates a simple example of building a server with shotglass.

    Run this as:

        ./sg_example.py          # to serve on port 80; or
        ./sg_example.py --debug  # to serve on port 8080, with verbose output.

    See the docstring in shotglass.py for more details.
"""


# _______________________________________________________________________
# Imports

import shotglass


# _______________________________________________________________________
# Handler functions

# These functions receive the following data:
#  * URL path parameters, in the order given, and
#  * The raw data string (not yet parsed), *only if* it's a POST request.

def get_hello_html():
    return b'<html><body><h1>hello</h1></body></html>'


# _______________________________________________________________________
# Main

if __name__ == '__main__':

    # The format here is:
    # [<path>, <handler_fn>, <list_of_keywords>]; the last value is optional
    # and indicates which keyword arguments the handler function accepts.
    # The handler fn is called as fn(*path_args, [data, ] **kwargs); the
    # path_args are the $-delimited path words, data exists iff it's a POST,
    # and kwargs are the url query parameters listed in `optional_keywords`.

    GET_routes = [
            ['/', get_hello_html]
            # ['/a/$b$/c', my_handler_fn, ['optional_keyword']]
    ]

    POST_routes = [
    ]

    # Uncomment the next line to require basic authentication.
    # shotglass.set_basic_auth(True, 'user', 'pass')

    shotglass.register_routes(GET_routes, POST_routes)

    shotglass.run_server()
