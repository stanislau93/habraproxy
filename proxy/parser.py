"""Contains HTMLParser extension for Habr"""
import html
import os

from html.parser import HTMLParser
from .habr_helper import HabrHelper


class HabrParser(HTMLParser):
    """Handles parsing of Habr html pages"""
    FORBIDDEN_TAGS = ['style', 'script']
    TEMP_FILE_NAME = 'tmp.html'
    inside_forbidden_tag = False

    file = None

    helper = HabrHelper()

    """
    Required for e.g. XML files, that cannot be used via http due to host
    mismatch and have to be copied and injected directly into HTML
    """
    prepend_before_end = ''
    prepended_resources = []

    def set_output_buffer(self, buffer):
        """Needed for testing the parsing"""
        self.file = buffer

    def parse(self, html_string):
        """
        Begins parsing process. Writes parsed page to a
        temp file which can be read by the Proxy class
        """
        with open(self.TEMP_FILE_NAME, 'w+') as tmp_file:
            self.set_output_buffer(tmp_file)
            self.feed(html_string)

        with open(self.TEMP_FILE_NAME, 'rb') as tmp_file:
            output = tmp_file.read()

        os.remove(self.TEMP_FILE_NAME)

        return output

    def handle_starttag(self, tag, attrs):
        """
        Write the tag along with its attributes. Change the href in case it's a link
        In case we enter script or style tag we should memorize it and do not
        change the text inside before we leave the tag
        """
        if tag in self.FORBIDDEN_TAGS:
            self.inside_forbidden_tag = True

        text = self.get_starttag_text()

        if tag in ['a', 'form']:
            text = self.helper.replace_host_in_link(text)
        elif tag == 'use':
            text = text.replace(self.parse_tag_use(attrs), '')

        self.file.write(text)

    def parse_tag_use(self, attrs):
        """
        Tag <use> inside the <svg> construct hast to be handled separately.
        We cannot reference XML from a different host and thus have to copy and prepend
        it before the end of our parsed DOM tree.
        """
        for attr in attrs:
            if attr[0] in ['href', 'xlink:href']:
                url = attr[1][:attr[1].index('#')]

                if url not in self.prepended_resources:
                    self.prepend_before_end += self.helper.get_resource_content_string(attr[
                        1])
                    self.prepended_resources.append(url)

        return url

    def handle_endtag(self, tag):
        """
        Write the end tag. In case we leave script or style tag -
        remove the constraint that does not allow us to change the data
        """
        if tag in self.FORBIDDEN_TAGS:
            self.inside_forbidden_tag = False

        if tag == 'body':
            self.file.write(self.prepend_before_end)

        self.file.write('</' + tag + '>')

    def handle_data(self, data):
        """Parse text data. Send to helper in order to perform specific logic"""
        if not self.inside_forbidden_tag:
            data = self.helper.amend_text_data_with_tm(data)
            data = html.escape(data)

        self.file.write(data)
