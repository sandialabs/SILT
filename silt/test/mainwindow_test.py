import h5py
import pytest

from pathlib import Path

from silt import mainwindow
from utils import generate_image, generate_pyramid, param_default


class TestMainWindow():

    @pytest.fixture()
    def main_window(self, qtbot):
        main_window = mainwindow.MainWindow()
        qtbot.addWidget(main_window)
        return main_window

    @pytest.fixture()
    def template_path(self):
        file = Path(Path(__file__).resolve().parent) / "test_data" / "test.silttemplate.json"
        return str(file)
    
    @pytest.fixture()
    def labels_path(self):
        file = Path(Path(__file__).resolve().parent) / "test_data" / "test.siltlabels.json"
        return str(file)

    @pytest.fixture()
    def generated_image_path_default(self, param_default, tmp_path):
        target_path = str(Path(tmp_path) / "example.h5")
        # Generate dummy image
        generate_image(target_path, M=1000, N=1000)
        # Create pyramid for image
        generate_pyramid(path=target_path, params=param_default)

        return target_path
    
    @pytest.fixture()
    def generated_series_path_default(self, tmp_path):
        target_path = Path(tmp_path) / "example_series"
        target_path.mkdir(parents=True, exist_ok=True)

        for i in range(3):
            generate_image(target_path / f"{i}.h5", M=200, N=200)

        filenames = [str(p) for p in sorted(target_path.glob("**/*.h5"))]

        return filenames
    
    def test_open_image_assert_image_opened(self, 
                                            main_window, 
                                            generated_image_path_default, 
                                            template_path, 
                                            mocker):
        """
        Test that the image file is set to something, and that the
        widget function is called.
        """
        mock = mocker.patch("silt.mainwidget.MainWidget.setImage")
        
        main_window._openTemplate(template_path)
        main_window._load_image(generated_image_path_default)

        # Is the image opened?
        assert main_window.image_file != None
        assert isinstance(main_window.image_file, str)

        mock.assert_called()

    def test_open_image_assert_correct_values(self, 
                                            main_window, 
                                            generated_image_path_default, 
                                            template_path, 
                                            mocker):
        """
        Test that the correct window values are set.
        """
        mock = mocker.patch("silt.mainwidget.MainWidget.setImage")
        
        main_window._openTemplate(template_path)
        main_window._load_image(generated_image_path_default)

        assert main_window.image_min == 0
        assert main_window.image_mid == 500
        assert main_window.image_max == 1000
        assert main_window.image_size == (1000,1000)

    def test_open_image_integration(self, 
                                    main_window, 
                                    generated_image_path_default, 
                                    template_path):
        """
        Test without mocking anything, check if image is loaded in view
        """
        main_window._openTemplate(template_path)
        main_window._load_image(generated_image_path_default)

        assert main_window.central_widget.image_widget.base_image_item.image_file == generated_image_path_default
        assert main_window.central_widget.image_widget.base_image_item.current_crop.shape == (1000,1000)

    def test_close_image_action_assert_image_closed(self, 
                                                    main_window):
        """
        Test that the image is closed.
        """
        main_window._closeImageAction()

        assert main_window.image_file == None

    def test_open_series_assert_series_opened(self, 
                                  main_window, 
                                  generated_series_path_default, 
                                  template_path):
        """
        Test that the series is opened.
        """
        main_window._openTemplate(template_path)
        main_window._openSeries(generated_series_path_default)

        assert main_window.series_mode == True
        assert main_window.central_widget.series_selection_widget != None

    def test_close_series_action_assert_series_closed(self,
                                                      main_window,
                                                      generated_series_path_default,
                                                      template_path):
        """
        Test that the series is closed properly.
        """
        main_window._openTemplate(template_path)
        main_window._openSeries(generated_series_path_default)
        main_window._closeSeriesAction()

        assert main_window.series_mode == False

    def test_open_saved_labels_assert_saved_labels_opened(self, 
                                        main_window, 
                                        template_path, 
                                        generated_image_path_default, 
                                        labels_path):
        """
        Test that labels are correctly set in both view window and multiinput panel.
        """

        main_window._openTemplate(template_path)
        main_window._load_image(generated_image_path_default)
        main_window._openSavedLabels(labels_path)

        # This function seems fairly subject to change, not completely useful
        # to test the specifics?
        assert len(main_window.central_widget.image_widget.label_items) == 3
        assert len(main_window.central_widget.user_input_widget.rows) == 3

        

    

