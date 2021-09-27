import sys
import json
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
    global config # create a global variable: config
    with open(path, 'r') as f: # open the file in `path` for reading
        content = f.read()
        config = json.loads(content) # read the file as a dictionary into the config variable


################ EXAMPLE HANDLERS ################

class testPageHandler(tornado.web.RequestHandler): # a new class that adds to `RequestHandler`
    def get(self): # when there is a get request, respond with the contents of `testPage.html`
        self.render("testPage.html")


################ PROXY HANDLER ################

class proxyHandler(tornado.web.RequestHandler):
    SUPPORTED_METHODS = ("GET", "POST") # a tuple of http methods this will support

   
    async def get(self): # in a get request

        def handleResponse(response):
            if (response.error and not (isinstance(response.error, tornado.httpclient.HTTPError))):
                self.set_status(500)
                self.write("Error\n" + str(response.error)) # if there is an error that is not HTTPError, respond with code 500
            else: # if no error, respond with `response`
                self.set_status(response.code, response.reason) 
                self._headers = tornado.httputil.HTTPHeaders()

                for header, v in response.headers.get_all():
                    if header not in ('Content-Length', 'Transfer-Encoding', 'Content-Encoding', 'Connection'):
                        self.add_header(header, v)
                
                if response.body:                   
                    self.set_header('Content-Length', len(response.body))
                    self.write(response.body)
            self.finish()

        print("Handling " + self.request.method + " request to '" + self.request.uri + "' from '" + self.request.host + "'")
        # log the response
        # adress = self.request.host # idk

        firstUri = self.request.uri.split("/")[1] # rozdělí self.request.uri po každém `/` znaku and a získá 2nd odpověd

        newServer = config.get(firstUri)
        print("First uri key '" + firstUri + "' corresponds to: '" + newServer + "' in the database")

        self.request.host = newServer # change self.request.host to something from that `config` variable

        newAdress = "http://" + newServer + self.request.uri # create new address with protocol, server, and URI
        print("New adress: " + newAdress)

        req = tornado.httpclient.HTTPRequest(
            newAdress,
            method=self.request.method,
            headers=self.request.headers,
            body=self.request.body,
            allow_nonstandard_methods=True) # make an http request based on the information in this object

        client = tornado.httpclient.AsyncHTTPClient() # vytvoří asyncrhonní http client

        try:
            response = await client.fetch(req, raise_error=False)
            handleResponse(response) # handle the response

        except tornado.httpclient.HTTPError as error: # pokud je http error, odpoví s kodem 500
            if hasattr(error, 'response') and error.response:
                handleResponse(error.response)
            else:
                self.set_status(500)
                self.write("Error\n" + str(error))
                self.finish()

    async def post(self): 
        print("Handling " + self.request.method + " request to '" + self.request.uri + "' from '" + self.request.host + "'")
        return await self.get() # in a post request, use it as a get request

################ MAIN ################

if __name__ == '__main__': # when you run the file

    config = dict() # config is an empty dictionary
    parseKeys("keys.json") # read keys.json into a dictionary

    port = 80 # přidá hodnotu variable 80 k portu
    if len(sys.argv) > 1: # pokud tam je přikad line arguments, změní port první argument
        port = int(sys.argv[1])

    #vytvoří tornado webovou apliaci appTask
    appProxy = tornado.web.Application([
        (r".*", proxyHandler)
    ])

    # vytvoří tornado webovou apliaci appTask
    appTask = tornado.web.Application([
        (r"/serverApp1", testPageHandler)
    ])
    
    proxy_sockets = tornado.netutil.bind_sockets(port) # nabinduje proxy sockety k portu
    task_sockets = tornado.netutil.bind_sockets(8054) # nabinduje zadání socketu k portu

    serverProxy = tornado.httpserver.HTTPServer(appProxy) # create an http server
    serverProxy.add_sockets(proxy_sockets) # přidá socket na server

    serverTask = tornado.httpserver.HTTPServer(appTask) # vytvoří http server
    serverTask.add_sockets(task_sockets) # přidá socket na server

    print("I'm listening on port " + str(port)) # poslouchá na portu: ..

    tornado.ioloop.IOLoop.current().start() # poslouchá na response loop
