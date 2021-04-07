import sys
import os
import tornado
import tornado.web
import tornado.ioloop
from urllib.parse import urlparse

################ UTILITY FUNCTIONS ################
"""
def getProxyKey(url):
    urlParsed = urlparse(url, scheme="http")
    proxyKey = "%s_proxy" % urlParsed.scheme
    return os.environ.get(proxyKey)

def getHostPort(url):
    urlParsed = urlparse(url, scheme="http")
    return urlParsed.hostname, urlParsed.port

def fetch_request(url, callback, **args):
    proxyKey = getProxyKey(url)
    if proxyKey:
        print("Forward request via upstream proxy " + proxyKey)
        tornado.httpclient.AsyncHTTPClient.configure(
            "tornado.curl_httpclient.CurlAsyncHTTPClient")
        host, port = getHostPort(proxyKey)
        args["proxy_host"] = host
        args["proxy_port"] = port

    req = tornado.httpclient.HTTPRequest(url, **args)
    client = tornado.httpclient.AsyncHTTPClient()
    client.fetch(req, callback, raise_error=False)
"""

################ EXAMPLE TORNADO HANDLERS ################

class basicRequestHandler(tornado.web.RequestHandler):
    def get(self):
        #self.set_header("Acces-Control-Allow-Origin", "*")
        self.write("Hello, world")

class staticRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class queryStringRequestHandler(tornado.web.RequestHandler):
    def get(self):
        number = int(self.get_argument("number"))
        result = "odd" if number % 2 else "even"
        self.write("the number " + str(number) + " is "+ result)

class resourceRequestRequestHandler(tornado.web.RequestHandler):
    def get(self, id):
        self.write("Querying tweet with id " + id)


################ PROXY HANDLER ################

class proxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")
    # TODO Handle all these methods

    def get(self):
        print("Handling " + self.request.method + " request to " + self.request.uri)

        # TODO Add response handling here

    def post(self):
        return self.get()

    def put(self):
        print("Handling " + self.request.method + " request to " + self.request.uri)

    def delete(self):
        print("Handling " + self.request.method + " request to " + self.request.uri)


################ MAIN ################

if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/tasks/", basicRequestHandler),
        (r"/", basicRequestHandler),
        (r"/blog", staticRequestHandler),
        (r"/isEven", queryStringRequestHandler),
        (r"/tweet/([0-9]+)", resourceRequestRequestHandler),
        (r".*", proxyHandler)
    ])

    port = 8881
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.listen(port)
    print("I'm listening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()