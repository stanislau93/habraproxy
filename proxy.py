"""Contains Proxy class and launches the habrproxy programm"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import os

from .habr_helper import HabrHelper
from parser import HabrParser

PORT = 4443
HOST = '127.0.0.1'


class Proxy(SimpleHTTPRequestHandler):
    """Handles redirect from localhost to habr.com pages"""
    helper = HabrHelper()
    parser = HabrParser()

    def do_GET(self):
        """Handles GET requests to localhost"""
        habr_url = self.helper.get_remote_path(self.path)

        request = urllib.request.Request(habr_url)

        try:
            response = urllib.request.urlopen(request)
            self.process_response(habr_url, response)
        except urllib.error.HTTPError:
            print(habr_url + " raised http error!")

    def process_response(self, url, response):
        """Handles response, obtained from the habr page, redirected to from localhost"""
        content_type = response.getheader('Content-Type')

        if not content_type:
            return

        if content_type in ['text/css', 'application/javascript']:
            file_path = self.helper.replace_host_in_link(url)
            self.helper.store_file(file_path, response.fp, is_media=False)
        elif 'text/html' in content_type:
            charset = self.helper.get_charset(content_type)
            content = response.read().decode(charset)
            self.send_response(200)
            self.end_headers()
            parsed = self.parser.parse(content)
            self.wfile.write(parsed)
        elif content_type.split('/')[0] in ['image', 'font']:
            file_path = self.helper.replace_host_in_link(url)
            self.helper.store_file(file_path, response.fp, is_media=True)

if __name__ == '__main__':
    WEB_DIR = os.path.dirname(os.path.realpath(__file__))
    os.chdir(WEB_DIR)

    httpd = HTTPServer((HOST, PORT), Proxy)
    httpd.serve_forever()
