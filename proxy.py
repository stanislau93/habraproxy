from http.server import HTTPServer, SimpleHTTPRequestHandler, HTTPStatus
import http.server
import urllib.request
import urllib.parse
import urllib.error
import ssl
import os
from html.parser import HTMLParser
import re

PORT = 4443
HOST = '127.0.0.1'
HABR_HOST = 'https://habr.com/ru'
HTML_DIRECTORY = 'pages'


class HabrParser(HTMLParser):

  FORBIDDEN_TAGS = ['style', 'script']
  MAGIC_LENGTH = 6
  inside_forbidden_tag = False

  file = None

  def handle_starttag(self, tag, attrs):
    if tag in self.FORBIDDEN_TAGS:
      self.inside_forbidden_tag = True

    if tag == 'a' and 'href' in [i[0] for i in attrs]:
      text = self.get_starttag_text()
      self.file.write(text.replace(
          'href="https://habr.com/ru', 'href="'))
    else:
      self.file.write(self.get_starttag_text())

  def handle_endtag(self, tag):
    if tag in self.FORBIDDEN_TAGS:
      self.inside_forbidden_tag = False
    self.file.write('</' + tag + '>')

  def handle_data(self, data):
    if not self.inside_forbidden_tag:
      words = re.findall(r"[\w']+", data)
      data = ' '.join([(self.append_tm(w) if len(w) == self.MAGIC_LENGTH else w)
                       for w in words])
    self.file.write(data)

  def append_tm(self, word):
    return word + u"\u2122"

  def start_parsing(self, html, file_name):
    with open(file_name, 'w') as file:
      self.file = file
      self.feed(html)


class HabrHelper:

  def get_habr_path(self, local_path):
    if HOST in local_path:
      return local_path.replace(HOST, HABR_HOST)
    else:
      return HABR_HOST + local_path

  def get_file_name_from_habr_path(self, path):
    return HTML_DIRECTORY + '/page' + path.replace(HABR_HOST, '').replace('/', '_') + '.html'

  def replace_habr_links(self, html_string):
    return html_string.replace('href="https://habr.com/', 'href="127.0.0.1"')

  def parse_html(self, url, output_file_name):
    req = urllib.request.Request(url)

    try:
      response = urllib.request.urlopen(req)
      the_page = response.read().decode('utf-8')
      parser = HabrParser()
      parser.start_parsing(the_page, output_file_name)
    except urllib.error.HTTPError:
      print(url + " raised http error!")


class Proxy(http.server.SimpleHTTPRequestHandler):

  helper = HabrHelper()

  def do_GET(self):

    habr_path = self.helper.get_habr_path(self.path)
    output_file_name = self.helper.get_file_name_from_habr_path(habr_path)

    if not os.path.isfile(output_file_name):
      self.helper.parse_html(habr_path, output_file_name)

    if os.path.isfile(output_file_name):
      self.output_file_content(output_file_name)

  def output_file_content(self, file_path):
    self.send_response(200)
    self.end_headers()
    with open(file_path, 'rb') as file:
      self.wfile.write(file.read())

web_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(web_dir)

httpd = HTTPServer((HOST, PORT), Proxy)
httpd.serve_forever()
