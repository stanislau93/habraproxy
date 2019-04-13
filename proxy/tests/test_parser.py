import pytest
import sys
from ..parser import HabrParser


class TestHabrParser:
    parser = HabrParser()
    file = None

    testdata_forbidden_tags = [
        ('script'), ('style')
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
