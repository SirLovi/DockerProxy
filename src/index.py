import sys
import tornado.web
import tornado.ioloop

################ EXAMPLE TORNADO HANDLERS ################

class basicRequestHandler(tornado.web.RequestHandler):
    def get(self):
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
    def get(self):
        print("Handling " + self.request.method + " request to " + self.request.uri)

        # TODO Add response handling here

    def post(self):
        return self.get()

    def connect(self):
        print("Handling CONNECT to " + self.request.uri)
        host, port = self.request.uri.split(':')
        client = self.request.connection.stream

        # TODO Add client read/write/connect/close functions


################ MAIN ################

if __name__ == '__main__':
    app = tornado.web.Application([
        # (r"/", basicRequestHandler),
        # (r"/blog", staticRequestHandler),
        # (r"/isEven", queryStringRequestHandler),
        # (r"/tweet/([0-9]+)", resourceRequestRequestHandler),
        (r".*", proxyHandler)
    ])

    port = 8881
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    app.listen(port)
    print("I'm listening on port " + str(port))
    tornado.ioloop.IOLoop.current().start()