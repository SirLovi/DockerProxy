import tornado.web
import tornado.ioloop

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




if __name__ == '__main__':
    app = tornado.web.Application([
        (r"/", basicRequestHandler),
        (r"/blog", staticRequestHandler),
        (r"/isEven", queryStringRequestHandler),
        (r"/tweet/([0-9]+)", resourceRequestRequestHandler)
    ])

    app.listen(8881)
    print("I'm listening on port 8881")
    tornado.ioloop.IOLoop.current().start()