#!/usr/bin/env python3

import tornado.ioloop
import tornado.web

HOST_NAME = '0.0.0.0'
PORT_NUMBER = 80

class Handler(tornado.web.RequestHandler):
    def get(self):
        self.set_status(200)
        self.set_header("Content-type", "text/html; charset=utf-8")
        self.write("<!DOCTYPE html><html><head><meta charset=\"utf-8\"></head><body><div>Hello World!</div></body></html>")

app = tornado.web.Application([(r'/', Handler)])
app.listen(PORT_NUMBER)
tornado.ioloop.IOLoop.current().start()