"""Generic helper solution. Should be extended by e.g. HabrHelper"""
import os
import re
import urllib.request


class ProxyHelper(object):
    """Contains helper functions for proxying requests"""

    REMOTE_HOST_LINKS = []
    LOCALHOST_FULL = ''

    REMOTE_HOST = ''
    LOCALHOST = ''
    DEFAULT_CHARSET = 'utf-8'

    def get_remote_path(self, local_path):
        """Given a path to localhost resource converts it into a remote host path"""
        if self.LOCALHOST in local_path:
            return local_path.replace(self.LOCALHOST, self.REMOTE_HOST)
        else:
            return self.REMOTE_HOST + local_path

    def replace_host_in_link(self, text, remove=True):
        """Given a text replaces all occurencies of links to remote host by either empty string or localhost link"""
        for link in self.REMOTE_HOST_LINKS:
            text = text.replace(link, ('' if remove else self.LOCALHOST_FULL))
        return text

    def store_file(self, file_path, content_stream, is_media):
        """Given file content stores it either as a binary (e.g. image) or string file on local system"""
        file_path = '/' + file_path if file_path[0] != '/' else file_path
        file_path = file_path + 'file' if file_path[-1] == '/'else file_path

        self.create_subfolders_if_required(file_path)

        mode = 'wb+' if is_media else 'w+'

        content = content_stream.read(
        ) if is_media else content_stream.read().decode(self.DEFAULT_CHARSET)

        local_path = os.path.dirname(os.path.realpath(__file__)) + file_path

        with open(local_path, mode) as local_file:
            local_file.write(content)

    def create_subfolders_if_required(self, path):
        """For each folder in path - creates it on local system, if it does not exist yet, so the file can be stored safely"""
        builded_path = ''

        # remove first slash and parent folder redirects
        path = path[1:] if path[0] == '/' else path
        path = path.replace('..', '')

        for folder in path.split('/')[:-1]:
            builded_path += folder + '/'

            if os.path.isdir(builded_path):
                continue
            else:
                os.mkdir(builded_path)

    def get_charset(self, content_type=''):
        """Tries to extract charset from the content-type header. Alternatively returns default charset"""
        match = re.search(r'charset=([\w-]+)', content_type)
        return match.group(1) if match else self.DEFAULT_CHARSET

    def get_resource_content_string(self, url):
        """Returns a decoded string from a certain internet address"""
        response = urllib.request.urlopen(url)
        return response.read().decode(self.DEFAULT_CHARSET)
