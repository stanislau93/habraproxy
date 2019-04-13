import os
from http.server import HTTPServer

PORT = 4443
HOST = '127.0.0.1'

from proxy.proxy import Proxy

if __name__ == '__main__':
    WEB_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(WEB_DIR)

    httpd = HTTPServer((HOST, PORT), Proxy)
    httpd.serve_forever()
