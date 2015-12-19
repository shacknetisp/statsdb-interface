# -*- coding: utf-8 -*-
import urllib.parse
from datetime import datetime
import traceback
import web
import json
import dbselectors


# Response to be sent to the client
class Response:

    # Status strings for each used HTTP code
    HTTP_Codes = {
        200: "200 OK",
        301: "301 Moved Permanently",
        404: "404 Not Found",
        500: "500 Internal Server Error",
    }

    def __init__(self, body="", headers=None, status=200):
        self.body = body.encode()
        self.headers = headers or {}
        self.status = Response.HTTP_Codes[status]


# Styled page as a Response
class WebResponse (Response):

    def __init__(self, body="", title="", css="", status=200, debug=""):
        super(type(self), self).__init__(body=web.page(body, title, css, debug),
            status=status, headers={
                'Content-type': 'text/html',
                })


# Request from the client
class Request:

    def __init__(self, environ):
        self.path = environ['PATH_INFO']
        self.query = urllib.parse.parse_qs(environ['QUERY_STRING'], True)
        self.fullpath = "%s?%s" % (self.path, self.query)
        self.clientip = environ['REMOTE_ADDR']


# Handle a request
def handle(request, db):
    print(("{ts} {ip} {path} {query}".format(
            ts=datetime.now().strftime('%D %T'),
            ip=request.clientip,
            path=request.path,
            query=request.query,
        )))
    # Handle all errors
    try:
        return safe_handle(request, db)
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
    top = None
    sub = None
    specific = None
    # Go through list, popping.
    if paths:
        top = paths.pop(0)
    if paths:
        sub = paths.pop(0)
    if paths:
        specific = paths.pop(0)
    if not top:
        #Overview
        pass
    elif top == "api":
        # Return JSON
        ret = {'error': 'No such selector.'}
        if sub and sub in dbselectors.selectors:
            selector = dbselectors.selectors[sub](request.query, db, specific)
            ret = selector.single() if specific else selector.multi()
        return Response(json.dumps(ret), headers={
            'Content-type': 'application/json',
            })
    return WebResponse(
        "<h2 class='center'>404 Page not Found</h2>",
        title=Response.HTTP_Codes[404],
        status=404)
