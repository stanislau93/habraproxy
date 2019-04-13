import pytest
import shutil
import os
import io

from ..habr_helper import HabrHelper


class TestHabrHelper:

    helper = HabrHelper()

    test_dir = os.path.dirname(os.path.realpath(__file__))
    web_dir = os.path.dirname(os.path.realpath(__file__)).replace('/tests', '')

    testdata_getremotepath = [
        ('127.0.0.1', 'https://habr.com'),
        ('127.0.0.1/images/favicon-16x16.png',
         'https://habr.com/images/favicon-16x16.png'),
        ('127.0.0.1/css/custom.css', 'https://habr.com/css/custom.css'),
    ]

    testdata_create_subfolders = [
        ('images/0/1/2/ktulhu.jpg', 'images')
    ]

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
         '<a href="/something">Mein link</a>'),
        ('https://habr.com/images/00/01/02/image.jpg', '/images/00/01/02/image.jpg')
    ]

    @pytest.fixture(scope="session", autouse=True)
    def change_dir(self, request):
        os.chdir(self.test_dir)

    @pytest.mark.parametrize("data,expected_output", testdata_amend_with_tm)
    def test_amend_text_data_with_tm(self, data, expected_output):
        assert self.helper.amend_text_data_with_tm(data) == expected_output

    @pytest.mark.parametrize("tag,output_tag", testdata_replace_habrlinks)
    def test_replace_host_in_link(self, tag, output_tag):
        assert self.helper.replace_host_in_link(tag) == output_tag

    @pytest.mark.parametrize("local_path,expected_habr_path", testdata_getremotepath)
    def test_get_remote_path(self, local_path, expected_habr_path):
        assert expected_habr_path == self.helper.get_remote_path(local_path)

    @pytest.mark.parametrize("path,root_folder", testdata_create_subfolders)
    def test_create_subfolders_if_required(self, path, root_folder):
        self.helper.create_subfolders_if_required(path)
        assert os.path.isdir(self.test_dir + '/' +
                             '/'.join(path.split('/')[:-1]))

        shutil.rmtree(self.test_dir + '/' + root_folder)

    def test_store_file_css(self):
        os.chdir(self.web_dir)

        file_path = 'tests/files/test.css'
        output = io.BytesIO()

        output.write('#one {height: 20rem; width: 30rem;}'.encode('UTF-8'))
        output.seek(0)

        self.helper.store_file(file_path, output, is_media=False)
        assert os.path.isfile(file_path)

        with open(file_path, 'r') as test_file:
            assert test_file.read() == '#one {height: 20rem; width: 30rem;}'

        os.remove(file_path)
