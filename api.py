# -*- coding: utf-8 -*-
import urllib.parse
from datetime import datetime
import traceback
import web


# Response to be sent to the client
class Response:

    # Status strings for each used HTTP code
    HTTP_Codes = {
        200: "200 OK",
        301: "301 Moved Permanently",
        404: "404 Not Found",
        500: "500 Internal Server Error",
    }

    def __init__(self, body="", headers={}, status=200):
        self.body = body.encode()
        self.headers = headers
        self.status = Response.HTTP_Codes[status]


# Styled page as a Response
class WebResponse (Response):

    def __init__(self, body="", title="", css="", status=200, debug=""):
        super(type(self), self).__init__(body=web.page(body, title, css, debug),
            status=status)


# Request from the client
class Request:

    def __init__(self, environ):
        self.path = environ['PATH_INFO']
        self.query = urllib.parse.parse_qs(environ['QUERY_STRING'], True)
        self.fullpath = "%s?%s" % (self.path, self.query)
        self.clientip = environ['REMOTE_ADDR']


# Handle a request
def handle(request):
    print(("{ts} {ip} {path} {query}".format(
            ts=datetime.now().strftime('%D %T'),
            ip=request.clientip,
            path=request.path,
            query=request.query,
        )))
    # Handle all errors
    try:
        return safe_handle(request)
    except:
        traceback.print_exc()
        return WebResponse(
            "<h2 class='center'>The server has encountered an error.</h2>",
            title=Response.HTTP_Codes[500],
            status=500)


# Dispatch the requests
def safe_handle(request):
    return WebResponse(
        "<h2 class='center'>404 Page not Found</h2>",
        title=Response.HTTP_Codes[404],
        status=404)

