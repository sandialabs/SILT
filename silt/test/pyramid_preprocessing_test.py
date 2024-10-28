import pytest
import logging
import h5py
from pathlib import Path

from silt import pyramid_preprocessing
from utils import generate_image, generate_pyramid, param_default

class TestPyramidPreprocessing:

    @pytest.fixture()
    def generated_image_path_default(self, tmp_path):
        target_path = Path(tmp_path) / "example.h5"
        # Generate dummy image
        generate_image(target_path, M=1000, N=1000)

        return target_path
    
    @pytest.fixture()
    def generated_image_path_large(self, tmp_path):
        target_path = Path(tmp_path) / "example.h5"
        # Generate dummy image
        generate_image(target_path, M=5000, N=5000)

        return target_path
    
    def generate_level(self, path, params):
        with h5py.File(path, "a") as h5_image:
            h5_image.create_group("pyramid")
            _, _ = pyramid_preprocessing.block_filter_to_pyramid(
                input_image = h5_image[params["input_image"]],
                output_destination = h5_image[params["output_destination"]],
                target = params["target"],
                blocksize = params["blocksize"],
                downsample = params["downsample"],
                sigma = params["sigma"],
                radius = params["radius"])
            
    @pytest.fixture()
    def generate_image_level_default(self, generated_image_path_default, param_default):
        self.generate_level(generated_image_path_default, param_default)
        return generated_image_path_default
    
    @pytest.fixture()
    def generate_image_pyramid_default(self, generated_image_path_default, param_default):
        generate_pyramid(generated_image_path_default, param_default)
        return generated_image_path_default
    
    @pytest.fixture()
    def generate_image_pyramid_large(self, generated_image_path_large, param_default):
        generate_pyramid(generated_image_path_large, param_default)
        return generated_image_path_large


class TestBlockFilter(TestPyramidPreprocessing):

    def test_assert_image_generated(self, generate_image_level_default, param_default):
        with h5py.File(generate_image_level_default, "r") as image:
            assert len(image["pyramid"].keys()) == 1
            assert param_default["target"] in image["pyramid"].keys()
            assert image["pyramid"][param_default["target"]] != None

    def test_assert_correct_image_size(self, generate_image_level_default, param_default):
        expected_len = 500

        with h5py.File(generate_image_level_default, "r") as image:
            im = image["pyramid"][param_default["target"]]
            len = im.shape[0]
            width = im.shape[1]
            assert len == expected_len
            assert width == expected_len

    def test_assert_correct_min_max(self, generated_image_path_default, param_default):
        expected_min = 0
        expected_max = 1000
        with h5py.File(generated_image_path_default, "a") as h5_image:
            h5_image.create_group("pyramid")
            min, max = pyramid_preprocessing.block_filter_to_pyramid(
                input_image = h5_image[param_default["input_image"]],
                output_destination = h5_image[param_default["output_destination"]],
                target = param_default["target"],
                blocksize = param_default["blocksize"],
                downsample = param_default["downsample"],
                sigma = param_default["sigma"],
                radius = param_default["radius"])
            
        assert min == expected_min
        assert max == expected_max

class TestGeneratePyramid(TestPyramidPreprocessing):

    def test_assert_group_exists(self, generate_image_pyramid_large):
        with h5py.File(generate_image_pyramid_large, "r") as image:
            assert image["pyramid"] != None
            assert isinstance(image["pyramid"], h5py.Group)

    def test_assert_exit_when_pyramid_exists(self, generated_image_path_large, param_default, caplog):
        caplog.set_level(logging.INFO)
        with h5py.File(generated_image_path_large, "a") as h5_image:
            h5_image.create_group("pyramid")
        
        generate_pyramid(generated_image_path_large, param_default)

        assert "Pyramid already exists\n" in caplog.text
    
    def test_assert_correct_num_levels(self, generate_image_pyramid_default):
        expected = 1
        with h5py.File(generate_image_pyramid_default, "r") as image:
            assert len(image.keys()) == expected

    def test_assert_correct_num_levels_large(self, generate_image_pyramid_large):
        expected = 3
        with h5py.File(generate_image_pyramid_large, "r") as image:
            assert len(image["pyramid"].items()) == expected

    def test_assert_correct_sizes(self, generate_image_pyramid_large):
        expected=[2500,1250,625]
        with h5py.File(generate_image_pyramid_large, "r") as image:
            for i in range(1, len(image["pyramid"].items())):
                assert image["pyramid"][str(i)].shape == (expected[i-1], expected[i-1])
