import sys
import json
import asyncio
import tornado
import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.ioloop
import tornado.iostream
import tornado.httpclient
import tornado.httputil
import tornado.netutil
from urllib.parse import urlparse


################ UTILITY FUNCTIONS ################

def parseKeys(path=""):
    global config
    with open(path, 'r') as f:
        content = f.read()
        config = json.loads(content)

class staticRequestHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")


################ PROXY HANDLER ################

class proxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "POST", "PUT", "DELETE")

   
    async def get(self):

        def handleResponse(response):
            if (response.error and not (isinstance(response.error, tornado.httpclient.HTTPError))):
                self.set_status(500)
                self.write("Error\n" + str(response.error))
            else:
                self.set_status(response.code, response.reason)
                self._headers = tornado.httputil.HTTPHeaders()

                for header, v in response.headers.get_all():
                    if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                        self.add_header(header, v)
                
                if response.body:                   
                    self.set_header('Content-Length', len(response.body))
                    self.write(response.body)
            self.finish()

        print("Handling " + self.request.method + " request to " + self.request.uri + " from " + self.request.host)

        adress = self.request.host
        newServer = config.get(adress)
        self.request.host = newServer
        newAdress = "http://" + newServer + self.request.uri

        print("New adress: " + newAdress)

        req = tornado.httpclient.HTTPRequest(
            newAdress,
            method=self.request.method,
            headers=self.request.headers,
            body=self.request.body,
            allow_nonstandard_methods=True)

        client = tornado.httpclient.AsyncHTTPClient()

        try:
            response = await client.fetch(req, raise_error=False)
            handleResponse(response)

        except tornado.httpclient.HTTPError as error:
            if hasattr(error, 'response') and error.response:
                handleResponse(error.response)
            else:
                self.set_status(500)
                self.write("Error\n" + str(error))
                self.finish()


    async def post(self):
        return await self.get()

   
    async def put(self, *args, **kwargs):
        print("Handling " + self.request.method + " request to " + self.request.uri)

   
    async def delete(self):
        print("Handling " + self.request.method + " request to " + self.request.uri)


################ MAIN ################

if __name__ == '__main__':

    config = dict()
    parseKeys("keys.json")

    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])

    appProxy = tornado.web.Application([
        (r".*", proxyHandler)
    ])

    appTask = tornado.web.Application([
        (r"/task54", staticRequestHandler)
    ])
    
    proxy_sockets = tornado.netutil.bind_sockets(port)
    task_sockets = tornado.netutil.bind_sockets(8054)

    serverProxy = tornado.httpserver.HTTPServer(appProxy)
    serverProxy.add_sockets(proxy_sockets)

    serverTask = tornado.httpserver.HTTPServer(appTask)
    serverTask.add_sockets(task_sockets)

    print("I'm listening on port " + str(port))

    tornado.ioloop.IOLoop.current().start()