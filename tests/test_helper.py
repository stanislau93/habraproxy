import pytest
import shutil
import os

from ..proxy import HabrHelper


class TestHabrHelper:

  helper = HabrHelper()

  test_dir = os.path.dirname(os.path.realpath(__file__))

  testdata_gethabrpath = [
      ('127.0.0.1', 'https://habr.com'),
      ('127.0.0.1/images/favicon-16x16.png',
       'https://habr.com/images/favicon-16x16.png'),
      ('127.0.0.1/css/custom.css', 'https://habr.com/css/custom.css'),
  ]

  testdata_filename_from_habrpath = [
      ('https://habr.com/444', 'pages/page_444.html'),
      ('https://habr.com/images/abc.png', 'images/abc.png'),
      ('https://habr.com/css/mycustom.css', 'css/mycustom.css'),
  ]

  testdata_create_subfolders = [
      ('images/0/1/2/ktulhu.jpg', 'images')
  ]

  @pytest.fixture(scope="session", autouse=True)
  def change_dir(self, request):
    os.chdir(self.test_dir)

  @pytest.mark.parametrize("local_path,expected_habr_path", testdata_gethabrpath)
  def test_get_habr_path(self, local_path, expected_habr_path):
    assert expected_habr_path == self.helper.get_habr_path(local_path)

  @pytest.mark.parametrize("habr_path,expected_file_name", testdata_filename_from_habrpath)
  def test_get_file_name_from_habr_path(self, habr_path, expected_file_name):
    assert expected_file_name == self.helper.get_file_name_from_habr_path(
        habr_path)

  @pytest.mark.parametrize("path,root_folder", testdata_create_subfolders)
  def test_create_subfolders_if_required(self, path, root_folder):
    self.helper.create_subfolders_if_required(path)
    assert os.path.isdir(self.test_dir + '/' + '/'.join(path.split('/')[:-1]))

    shutil.rmtree(self.test_dir + '/' + root_folder)
