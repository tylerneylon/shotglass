#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" sg_example.py

    This file illustrates a simple exmple of building a server with shotglass.

    Run this as:

        ./sg_example          # to serve on port 80; or
        ./sg_example --debug  # to serve on port 8080, with more verbose output.

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

    GET_routes = [
            ['/', get_hello_html]
            # ['/a/$b$/c', my_handler_fn, ['optional_keyword']]
    ]

    POST_routes = [
    ]

    shotglass.register_routes(GET_routes, POST_routes)

    shotglass.run_server()
