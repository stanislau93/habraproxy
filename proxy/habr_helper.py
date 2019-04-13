"""contains HabrHelper class"""
import re

from .proxy_helper import ProxyHelper


class HabrHelper(ProxyHelper):
    """Contains habr.com specific helper functionality"""
    MAGIC_LENGTH = 6

    # order is important for the replacement
    REMOTE_HOST_LINKS = ['https://habr.com/ru', 'https://habr.com']
    LOCALHOST_FULL = 'http://127.0.0.1:4443'

    LOCALHOST = '127.0.0.1'
    REMOTE_HOST = 'https://habr.com'

    def amend_text_data_with_tm(self, data):
        """
        insert TM sign after each word with exactly 6 chars in it
        """
        words = re.findall(r"[\w']+", data)
        word_delimiters = re.findall(r"[\W]+", data)

        if not words:
            return ''.join(word_delimiters) if word_delimiters else data

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
        """appends tm sign to a given word"""
        return word + u"\u2122"
