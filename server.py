"""Launcher module of the habr proxy project"""
import os
from http.server import HTTPServer
from proxy.proxy import Proxy

PORT = 4443
HOST = '127.0.0.1'


if __name__ == '__main__':
    WEB_DIR = os.path.dirname(os.path.realpath(__file__)) + '/proxy'
    os.chdir(WEB_DIR)

    httpd = HTTPServer((HOST, PORT), Proxy)
    httpd.serve_forever()
