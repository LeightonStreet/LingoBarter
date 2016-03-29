#!/usr/bin/python
"""
wsgi.py
=======
This file is used by openshift, please use lingo.py
to start lingobarter. This file should be left untouched.
"""

import argparse

from lingobarter import create_app
from lingobarter.utils.paas import activate
from werkzeug.serving import run_simple
from werkzeug.wsgi import DispatcherMiddleware

# in the future, we will write the api routing
application = DispatcherMiddleware(create_app())

application = app = activate(application)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Lingobarter App for WSGI")
    parser.add_argument('-p', '--port', help='App Port')
    parser.add_argument('-i', '--host', help='App Host')
    parser.add_argument('-r', '--reloader', action='store_true',
                        help='Turn reloader on')
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Turn debug on')
    args = parser.parse_args()
    run_simple(
        args.host or '0.0.0.0',
        int(args.port) if args.port else 5000,
        application,
        use_reloader=args.reloader or False,
        use_debugger=args.debug or False,
    )
