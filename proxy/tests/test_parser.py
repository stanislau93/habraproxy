import sys
import io

import pytest

from ..parser import HabrParser


class TestHabrParser:
    parser = HabrParser()
    file = None

    testdata_forbidden_tags = [
        ('script'), ('style')
    ]

    testdata_parsedata = [
        ('<html><head></head><body><script type="">whoami</script></body></html>',
         ['<script type="">whoami</script>'], []),
        ('<html><head></head><body><style type="">whoami</style></body></html>',
         ['<style type="">whoami</style>'], []),
        ('<html><head></head><body><span class="">whoami</span></body></html>',
         ['<span class="">whoami™</span>'], []),
        ('<html><head></head><body>&lt;i&gt;</body></html>',
         ['&lt;i&gt;'], ['<i>'])
    ]

    @pytest.mark.parametrize("tag", testdata_forbidden_tags)
    def test_inside_forbidden_tag(self, tag):
        self.parser.file = sys.stdout
        # Dummy data - needed to avoid Exception on get_starttag_text
        self.parser.feed('<html></html>')

        self.parser.handle_starttag(tag, [])
        assert self.parser.inside_forbidden_tag
        self.parser.handle_endtag(tag)
        assert not self.parser.inside_forbidden_tag

    @pytest.mark.parametrize("html, expected_contains, expected_contains_not", testdata_parsedata)
    def test_parse_data(self, html, expected_contains, expected_contains_not):
        output_buffer = io.StringIO()
        self.parser.set_output_buffer(output_buffer)

        self.parser.feed(html)

        output_buffer.seek(0)

        for substring in expected_contains:
            assert substring in output_buffer.read()

        for substring in expected_contains_not:
            assert substring not in output_buffer.read()

        output_buffer.close()
