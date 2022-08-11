# shotglass
v0.1.1

A tiny Python library to build servers.

## Usage

The general usage of shotglass is to register routes by calling
`shotglass.register_routes()`, and then to run the server by calling
`shotglass.run_server()`.

A single route is given as a list like this:

    `[<string for the route>, <python handler fn>, <optional keywords>]`

eg, `<string for the route> = /my/$var_a$/path/`
When variables are in a route, they become the first parameters handed to
the handler function.

The `<optional keywords>` element is a list of strings. Shotglass passes
through url query values whose key is an element of this list. Those values
are given to the handler function as Python keywords in the function's
arguments.

As a simple security step, you can enable basic authentication by calling the
`set_basic_auth()` function before running your server. This function is used
like so:

    import shotglass
    # ...
    shotglass.set_basic_auth(True, 'user', 'pass')

The default port is 80. If you'd like, you can programmatically override this
port to be whatever you like, as such:

    shotglass.run_server(default_port=MY_PORT)

With or without that optional parameter, if the command-line flag `--debug` is
detected, then the port is switched to 8080, and additional debug output is sent
to stdout. The reason for switching to port 8080 is that high port numbers (such
as 8080) can be more easily bound on some systems (so you can develop your
server without needing administrative permissions), and this makes it easier for
you to simultaneously run two versions of your server code on one machine.

## Example

Below is the content of the file `sg_example.py`. It serves a simple "hello"
page at `http://localhost/`.

```
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
```

