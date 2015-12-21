# -*- coding: utf-8 -*-
import urllib.parse
from datetime import datetime
import traceback
import web
import json
import dbselectors
from web import displays
import time
import cfg

cache = {}


# Response to be sent to the client
class Response:

    # Status strings for each used HTTP code
    HTTP_Codes = {
        200: "200 OK",
        301: "301 Moved Permanently",
        404: "404 Not Found",
        500: "500 Internal Server Error",
    }

    def __init__(self, body="", headers=None, status=200, cache=True):
        self.body = body.encode() if type(body) is str else body
        self.headers = headers or {}
        self.status = Response.HTTP_Codes[status]
        self.cache = cache


# Styled page as a Response
class WebResponse (Response):

    def __init__(self, body="", title="", css="",
        status=200, debug="", cache=True):
            super(
                type(self), self).__init__(
                    body=web.page(body, title, css, debug),
                    status=status, headers={
                            'Content-type': 'text/html',
                        },
                    cache=cache)


# Request from the client
class Request:

    def __init__(self, environ):
        self.path = environ['PATH_INFO']
        self.query = urllib.parse.parse_qs(environ['QUERY_STRING'], True)
        self.fullpath = "%s?%s" % (self.path, self.query)
        self.clientip = environ['REMOTE_ADDR']


# Handle a request
def handle(request, db):
    index = str([request.path, request.query])
    if index in cache:
        if time.time() - cache[index][0] < cfg.get('cache_web'):
            print(("{ts} {ip} {path} {query} [cached]".format(
                ts=datetime.now().strftime('%D %T'),
                    ip=request.clientip,
                    path=request.path,
                    query=request.query,
            )))
            return cache[index][1]
    print(("{ts} {ip} {path} {query}".format(
        ts=datetime.now().strftime('%D %T'),
            ip=request.clientip,
            path=request.path,
            query=request.query,
    )))
    # Handle all errors
    try:
        result = safe_handle(request, db)
        if result.cache:
            cache[index] = (time.time(), result)
        return result
    except:
        traceback.print_exc()
        return WebResponse(
            "<h2 class='center'>The server has encountered an error.</h2>",
            title=Response.HTTP_Codes[500],
            status=500)


# Dispatch the requests
def safe_handle(request, db):
    # Split paths and find where to call
    paths = [x for x in request.path.split('/') if x]
    top = ''
    sub = None
    specific = None
    # Go through list, popping.
    if paths:
        top = paths.pop(0)

    def filepath(t):
        return str('files/' + t + '/' + '/'.join(paths)).replace('..', '')

    # Check if the DB exists, return an error message.
    if db.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='games'"
        ).fetchone() is None:
            if top == "api":
                return Response(json.dumps({"error": "No database"}), headers={
                    'Content-type': 'application/json',
                }, cache=False)
            else:
                return WebResponse(
                    "<h2 class='center'>There is no statistics database.</h2>",
                    title="No database.", cache=False)

    # Return JSON directly from the selectors
    if top == "api":
        if paths:
            sub = paths.pop(0)
        if paths:
            specific = paths.pop(0)
        ret = {'error': 'No such selector.'}
        if sub and sub in dbselectors.selectors:
            selector = dbselectors.selectors[sub](request.query, db, specific)
            ret = selector.single() if specific else selector.multi()
        return Response(json.dumps(ret), headers={
            'Content-type': 'application/json',
        })
    # Files
    elif top == "images":
        return Response(open(filepath('images'), 'rb').read(), headers={
            'Content-type': 'image/png',
        })
    elif top == "styles":
        return Response(open(filepath('styles')).read(), headers={
            'Content-type': 'text/css',
        })
    elif top == "robots.txt":
        return Response(open('files/robots.txt').read(), headers={
            'Content-type': 'text/plain',
        })
    # Displays
    elif top in displays.displays:
        if paths:
            specific = paths.pop(0)
        display = displays.displays[top]
        out = None
        if specific and hasattr(display, 'single'):
            out = display.single(request, db, specific)
        elif hasattr(display, 'multi'):
            out = display.multi(request, db)
        if out is not None:
            return Response(out, headers={
                'Content-type': 'text/html',
            })

    return WebResponse(
        "<h2 class='center'>404 Page not Found</h2>",
        title=Response.HTTP_Codes[404],
        status=404)
