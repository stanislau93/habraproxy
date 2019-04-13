"""Contains Proxy class and launches the habrproxy programm"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import urllib.request
import os

from .habr_helper import HabrHelper
from .parser import HabrParser


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

        if 'text/html' in content_type:
            charset = self.helper.get_charset(content_type)
            content = response.read().decode(charset)
            parsed = self.parser.parse(content)

            self.send_response(200)
            self.end_headers()
            self.wfile.write(parsed)
        else:
            is_media = content_type not in [
                'text/css', 'application/javascript']
            file_path = self.helper.replace_host_in_link(url)
            file_path = file_path[1:] if file_path[0] == '/' else file_path

            self.helper.store_file(file_path, response.fp, is_media=is_media)

            if os.path.isdir(file_path):
                file_path = file_path + 'file'

            with open(file_path, 'rb') as resource_file:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(resource_file.read())
