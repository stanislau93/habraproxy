import pytest
from ..proxy import HabrHelper, Proxy, HabrParser


class TestHabrHelper:

  helper = HabrHelper()

  def test_test(self):
    assert 1 == 1

  def test_get_habr_path(self):
    local_path = '127.0.0.1'
    expected_habr_path = 'https://habr.com/ru'
    assert expected_habr_path == self.helper.get_habr_path(local_path)

  def test_get_file_name_from_habr_path(self):
    habr_path = 'https://habr.com/ru/444'
    expected_file_name = 'pages/page_444.html'
    assert expected_file_name == self.helper.get_file_name_from_habr_path(
        habr_path)
