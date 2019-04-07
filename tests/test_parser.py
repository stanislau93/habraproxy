import pytest
import sys
from ..proxy import HabrParser


class TestHabrParser:
  parser = HabrParser()
  file = None

  testdata_amend_with_tm = [
      ('hellow, my name is jooooe!', 'hellow™, my name is jooooe™!'),
      (' hellow, my name is jooooe!', ' hellow™, my name is jooooe™!'),
      ('привет, меня зовут Гришка Отрепьев',
       'привет™, меня зовут Гришка™ Отрепьев'),
      ('....привет, меня зовут Гришка Отрепьев',
       '....привет™, меня зовут Гришка™ Отрепьев'),
  ]

  testdata_replace_habrlinks = [
      ('<a href="https://habr.com/something">Mein link</a>',
       '<a href="/something">Mein link</a>'),
      ('<a href="https://habr.com/ru/something">Mein link</a>',
       '<a href="/something">Mein link</a>')
  ]

  testdata_forbidden_tags = [
      ('script'), ('style')
  ]

  @pytest.mark.parametrize("data,expected_output", testdata_amend_with_tm)
  def test_amend_text_data_with_tm(self, data, expected_output):
    assert self.parser.amend_text_data_with_tm(data) == expected_output

  @pytest.mark.parametrize("tag,output_tag", testdata_replace_habrlinks)
  def test_replace_habr_links(self, tag, output_tag):
    assert self.parser.replace_habr_links(tag) == output_tag

  @pytest.mark.parametrize("tag", testdata_forbidden_tags)
  def test_inside_forbidden_tag(self, tag):
    self.parser.file = sys.stdout
    # Dummy data - needed to avoid Exception on get_starttag_text
    self.parser.feed('<html></html>')

    self.parser.handle_starttag(tag, [])
    assert self.parser.inside_forbidden_tag
    self.parser.handle_endtag(tag)
    assert not self.parser.inside_forbidden_tag
