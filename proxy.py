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
HABR_HOST = 'https://habr.com'
HTML_DIRECTORY = 'pages'


class HabrParser(HTMLParser):

  FORBIDDEN_TAGS = ['style', 'script']
  MAGIC_LENGTH = 6
  inside_forbidden_tag = False

  # order is important for the replacement
  HABR_LINKS = ['href="https://habr.com/ru', 'href="https://habr.com']

  file = None

  def handle_starttag(self, tag, attrs):
    """
    Write the tag along with its attributes.
    Change the href in case it's a link
    In case we enter script or style tag - 
    we should memorize it and do not change the text inside before we leave the tag
    """
    if tag in self.FORBIDDEN_TAGS:
      self.inside_forbidden_tag = True

    text = self.get_starttag_text()

    if tag == 'a' and 'href' in [i[0] for i in attrs]:
      self.file.write(self.replace_habr_links(text))
    else:
      self.file.write(text)

  def replace_habr_links(self, text):
    for link in self.HABR_LINKS:
      text = text.replace(link, 'href="')
    return text

  def handle_endtag(self, tag):
    """
    Write the end tag. In case we leave script or style tag -
    remove the constraint that does not allow us to change the data
    """
    if tag in self.FORBIDDEN_TAGS:
      self.inside_forbidden_tag = False
    self.file.write('</' + tag + '>')

  def handle_data(self, data):
    if not self.inside_forbidden_tag:
      data = self.amend_text_data_with_tm(data)

    self.file.write(data)

  def amend_text_data_with_tm(self, data):
    """
    insert TM sign after each word with exactly 6 chars in it
    """
    words = re.findall(r"[\w']+", data)
    word_delimiters = re.findall(r"[\W]+", data)

    if not words:
      if not word_delimiters:
        return data
      else:
        return ''.join(word_delimiters)

    begins_with_word = data.index(words[0]) == 0

    output_data = ''

    if not begins_with_word:
      output_data = word_delimiters[0]
      word_delimiters = word_delimiters[1:]

    for index, word in enumerate(words):
      output_data += self.append_tm(word) if len(
          word) == self.MAGIC_LENGTH else word
      if index < len(word_delimiters):
        output_data += word_delimiters[index]

    return output_data

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
    if path.split('.')[-1] in ['png', 'woff', 'woff2', 'ttf', 'css', 'js', 'jpg']:
      return path.replace(HABR_HOST + '/', '')
    return HTML_DIRECTORY + '/page' + path.replace(HABR_HOST, '').replace('/', '_') + '.html'

  def load_file(self, url, content_stream, is_media):
    file_path = url.replace(HABR_HOST, '')
    self.create_subfolders_if_required(file_path)
    mode = 'wb+' if is_media else 'w+'
    content = content_stream.read() if is_media else content_stream.read().decode('utf-8')
    with open(os.path.dirname(os.path.realpath(__file__)) + file_path, mode) as file:
      file.write(content)

  def create_subfolders_if_required(self, path):
    builded_path = ''

    # remove first slash and parent folder redirects
    path = path[1:] if path[0] == '/' else path
    path = path.replace('..', '')

    for folder in path.split('/')[:-1]:
      builded_path += folder + '/'

      if (os.path.isdir(builded_path)):
        continue
      else:
        os.mkdir(builded_path)

  def get_file_from_server(self, url, output_file_name):
    req = urllib.request.Request(url)

    try:
      response = urllib.request.urlopen(req)
      content_type = response.getheader('Content-Type')
      if content_type.split('/')[0] in ['image', 'font']:
        self.load_file(url, response.fp, is_media=True)
      elif content_type in ['text/css', 'application/javascript']:
        self.load_file(url, response.fp, is_media=False)
      else:
        the_page = response.read().decode('utf-8')
        parser = HabrParser()
        parser.start_parsing(the_page, output_file_name)
    except urllib.error.HTTPError:
      print(url + " raised http error!")
    except UnicodeDecodeError:
      print(url + " content type " + content_type +
            " content could not be decoded!")


class Proxy(http.server.SimpleHTTPRequestHandler):

  helper = HabrHelper()

  def do_GET(self):
    habr_path = self.helper.get_habr_path(self.path)
    output_file_name = self.helper.get_file_name_from_habr_path(habr_path)

    # if not os.path.isfile(output_file_name):
    self.helper.get_file_from_server(habr_path, output_file_name)

    if os.path.isfile(output_file_name):
      self.output_file_content(output_file_name)

  def output_file_content(self, file_path):
    self.send_response(200)
    self.end_headers()
    with open(file_path, 'rb') as file:
      self.wfile.write(file.read())

if __name__ == '__main__':
  web_dir = os.path.dirname(os.path.realpath(__file__))
  os.chdir(web_dir)

  if not os.path.isdir(HTML_DIRECTORY):
    os.mkdir(HTML_DIRECTORY)

  httpd = HTTPServer((HOST, PORT), Proxy)
  httpd.serve_forever()
