from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
import http.server
import urllib.request, urllib.parse, urllib.error
import ssl

PORT = 4443
HOST = '127.0.0.1'
HABR_HOST = 'https://habr.com'


class HabrHelper:
    def getHabrPath(self, localPath):
        if HOST in localPath:
            return localPath.replace(HOST, HABR_HOST)
        else:
            return HABR_HOST + localPath

class Proxy(http.server.SimpleHTTPRequestHandler):
    
    helper = HabrHelper()
    
    """
     def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        self.send_response(200)
        self.end_headers()
        response = BytesIO()
        response.write(b'This is POST request. ')
        response.write(b'Received: ')
        response.write(body)
        self.wfile.write(response.getvalue())
    """
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Hello, world!\n')
        self.wfile.write(bytearray(self.helper.getHabrPath(self.path), 'UTF-8'))

        print(self.__dict__)
        print(self.headers.__dict__)

httpd = HTTPServer((HOST, PORT), Proxy)
#httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, keyfile='key.pem', certfile='cert.pem')
print("serving at port", PORT)
httpd.serve_forever()


