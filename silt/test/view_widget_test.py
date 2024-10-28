import h5py
import numpy as np
import pytest

from pathlib import Path
from PyQt5.QtCore import Qt, QPoint, QRectF
from PyQt5.QtGui import QColor

from silt import view_widget, interactive_polygon_item
from utils import generate_image, generate_image_small, generate_pyramid, DummyQGraphicsItem, param_default, param_small

class TestViewWidgetSetup:

    @pytest.fixture()
    def view_widget(self, qtbot):
        widget = view_widget.ViewWidget()
        qtbot.addWidget(widget)
        return widget

    @pytest.fixture()
    def pyramid_h5(self, param_default, tmp_path):
        target_path = Path(tmp_path) / "example.h5"
        # Generate dummy image
        generate_image(target_path, M=5000, N=5000)

        generate_pyramid(target_path, param_default)

        return target_path
    
    @pytest.fixture()
    def pyramid_h5_small(self, param_small, tmp_path):
        target_path = Path(tmp_path) / "example.h5"
        # Generate dummy image
        generate_image_small(target_path)

        generate_pyramid(target_path, param_small)

        return target_path
    
    @pytest.fixture
    def view_widget_set_image(self, view_widget, pyramid_h5):
        view_widget.setImage(image_file=pyramid_h5,
                            original_image_key="data",
                            shadow=0,
                            mid=1,
                            highlight=2,
                            no_pyramid=False)
        return view_widget

class TestViewWidget(TestViewWidgetSetup):
    def test_init_label_items_assert_items_initialized(self, view_widget, mocker):
        """
        Test that label_items are initialized if present.
        """
        mock = mocker.patch("silt.view_widget.ViewWidget.setLabelItems")

        label_items = ["dummy_list"]

        view_widget.initLabelItems(label_items)

        assert view_widget.label_items == label_items

        mock.assert_called_once_with(label_items)

    @pytest.fixture()
    def view_widget_setup_zoom(self, view_widget, mocker):
        view_widget.scene.setSceneRect(0, 
                                    0, 
                                    100, 
                                    100)
        
        # Avoid interaction with the GraphicsItem
        mocker = mocker.patch("silt.view_widget.BaseImageGraphicsItem.update_image_window")
        stub = mocker.stub(name="BaseImageGraphicsItemStub")
        view_widget.base_image_item = stub
        view_widget.current_zoom_level = 5

        return view_widget

    def test_update_zoom_assert_zoom_in_wheelEvent(self, view_widget_setup_zoom):
        """
        Test that zoom level is properly changed when zoom in.
        """
        # Set viewport bounds
        view_widget_setup_zoom.fitInView(10,10,10,10)

        pt = QPoint(0,120)

        view_widget_setup_zoom._update_zoom(pt)

        assert view_widget_setup_zoom.current_zoom_level == 4

    def test_update_zoom_assert_zoom_out_wheelEvent(self, view_widget_setup_zoom):
        """
        Test that zoom level is properly changed when zoom out.
        """
        # Set viewport bounds
        view_widget_setup_zoom.fitInView(10,10,10,10)

        pt = QPoint(0,-120)

        view_widget_setup_zoom._update_zoom(pt)

        assert view_widget_setup_zoom.current_zoom_level == 6

    def test_update_zoom_assert_zoom_in_max_wheelEvent(self, view_widget_setup_zoom):
        """
        Test that zoom stops when less than 1.
        """
        # Set viewport bounds
        view_widget_setup_zoom.fitInView(0,0,0.5,0.5)

        pt = QPoint(0,120)

        view_widget_setup_zoom._update_zoom(pt)

        assert view_widget_setup_zoom.current_zoom_level == 5

    def test_update_zoom_assert_zoom_out_max_wheelEvent(self, view_widget_setup_zoom):
        """
        Test that zoom stops when viewport bounds are greater than scene size.
        """
        # Set viewport bounds
        view_widget_setup_zoom.fitInView(10,10,101,101)

        pt = QPoint(0,-120)

        view_widget_setup_zoom._update_zoom(pt)

        assert view_widget_setup_zoom.current_zoom_level == 5

    def test_add_overlay_item_assert_item_added(self, view_widget):
        """
        Test that the overlay item is added as expected.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        x_1 = y_1 = y_2 = x_3 = 0
        x_2 = y_3 = 1
        line_width = 2.0
        color = [255, 0, 255, 255]
        style = 'solid'

        vertices = [(x_1,y_1),(x_2,y_2),(x_3,y_3)]

        view_widget.addOverlayItem(vertices=vertices, 
                                  color=color,
                                  style=style,
                                  line_width=line_width)

        # print(view_widget.overlay_items)

        assert len(view_widget.overlay_items) == 1
        
        assert view_widget.overlay_items[0][0].line().x1() == x_1
        assert view_widget.overlay_items[0][0].line().y1() == y_1
        assert view_widget.overlay_items[0][0].line().x2() == x_2
        assert view_widget.overlay_items[0][0].line().y2() == y_2

        assert view_widget.overlay_items[0][1].line().x1() == x_2
        assert view_widget.overlay_items[0][1].line().y1() == y_2
        assert view_widget.overlay_items[0][1].line().x2() == x_3
        assert view_widget.overlay_items[0][1].line().y2() == y_3

        assert view_widget.overlay_items[0][0].pen().style() == Qt.SolidLine
        assert view_widget.overlay_items[0][0].pen().widthF() == line_width
        assert view_widget.overlay_items[0][0].pen().color() == QColor(*color)

    def test_add_overlay_item_assert_item_added_with_overlay_item_vertices(self, 
                                                                           view_widget):
        """
        Test that the overlay item is added as expected with overlay_item_vertices.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        x_1 = y_1 = y_2 = x_3 = 0
        x_2 = y_3 = 1
        line_width = 2.0
        color = [255, 0, 255, 255]
        style = 'solid'

        overlay_item_vertices = [(x_1,y_1),(x_2,y_2),(x_3,y_3)]

        view_widget.addOverlayItem(overlay_item_vertices=overlay_item_vertices, 
                                  color=color,
                                  style=style,
                                  line_width=line_width)

        # print(view_widget.overlay_items)
        assert len(view_widget.overlay_items) == 1

        assert view_widget.overlay_items[0][0].line().x1() == x_1
        assert view_widget.overlay_items[0][0].line().y1() == y_1
        assert view_widget.overlay_items[0][0].line().x2() == x_2
        assert view_widget.overlay_items[0][0].line().y2() == y_2

        assert view_widget.overlay_items[0][1].line().x1() == x_2
        assert view_widget.overlay_items[0][1].line().y1() == y_2
        assert view_widget.overlay_items[0][1].line().x2() == x_3
        assert view_widget.overlay_items[0][1].line().y2() == y_3

        assert view_widget.overlay_items[0][0].pen().style() == Qt.SolidLine
        assert view_widget.overlay_items[0][0].pen().widthF() == line_width
        assert view_widget.overlay_items[0][0].pen().color() == QColor(*color)

    def test_add_overlay_item_assert_exit_if_no_vertices(self, view_widget):
        """
        Test that the overlay item is not added if the vertices are not specified.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        line_width = 2.0
        color = [255, 0, 255, 255]

        return_val = view_widget.addOverlayItem(color=color,
                                               line_width=line_width)

        assert return_val == -1

        # print(view_widget.overlay_items)
        assert len(view_widget.overlay_items) == 0

    def test_remove_overlay_items_assert_correct_overlay_item_removed(self, 
                                                                      view_widget):
        """
        Test that the correct overlay item is removed.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        vertices_1 = [(0,1),(1,0)]
        vertices_2 = [(1,2),(2,1)]

        view_widget.addOverlayItem(vertices=vertices_1)
        view_widget.addOverlayItem(vertices=vertices_2)

        removed_item = view_widget.removeOverlayItem(0)

        assert len(view_widget.overlay_items) == 1

        assert removed_item[0].line().x1() == vertices_1[0][0]
        assert removed_item[0].line().y1() == vertices_1[0][1]

        assert removed_item[0].line().x2() == vertices_1[1][0]
        assert removed_item[0].line().y2() == vertices_1[1][1]

    def test_clear_overlay_items_assert_overlay_items_cleared(self, 
                                                              view_widget):
        """
        Test that all overlay items are cleared.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        vertices_1 = [(0,1),(1,0)]
        vertices_2 = [(1,2),(2,1)]

        view_widget.addOverlayItem(vertices=vertices_1)
        view_widget.addOverlayItem(vertices=vertices_2)

        view_widget.clearOverlayItems()

        assert len(view_widget.overlay_items) == 0

    def test_show_overlay_assert_overlay_showing(self, 
                                                 view_widget):
        """
        Test that the overlay is showing.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        vertices_1 = [(0,1),(1,0)]
        vertices_2 = [(1,2),(2,1)]

        view_widget.addOverlayItem(vertices=vertices_1)
        view_widget.addOverlayItem(vertices=vertices_2)

        view_widget.showOverlay(True)

        assert len(view_widget.overlay_items) == 2

        assert view_widget.overlay_items[0][0].isVisible()

        assert view_widget.overlay_items[1][0].isVisible()

    def test_show_overlay_assert_overlay_not_showing(self, 
                                                     view_widget):
        """
        Test that the overlay is not showing.
        """
        # Don't give it a parent
        view_widget.base_grid = None

        vertices_1 = [(0,1),(1,0)]
        vertices_2 = [(1,2),(2,1)]

        view_widget.addOverlayItem(vertices=vertices_1)
        view_widget.addOverlayItem(vertices=vertices_2)

        view_widget.showOverlay(False)

        assert len(view_widget.overlay_items) == 2

        assert not view_widget.overlay_items[0][0].isVisible()

        assert not view_widget.overlay_items[1][0].isVisible()

    def test_set_image_assert_displayed(self, 
                                        view_widget_set_image):
        """
        Test that the image is displayed.
        """
        assert view_widget_set_image.base_image_item != None
        
    def test_set_label_items_assert_polygons_added(self, 
                                                   view_widget_set_image):
        """
        Test that label item overlays are added to scene
        """
        test_label_items = [{'label_item_type':'polygon',
                             'label_item_vertices':[(0,0),(0,1),(1,0)],
                             'label_item_uuid':'test_1'},
                             {'label_item_type':'polygon',
                             'label_item_vertices':[(1,1),(1,2),(2,1)],
                             'label_item_uuid':'test_2'}]
        
        view_widget_set_image.setLabelItems(test_label_items)

        assert len(view_widget_set_image.label_items) == 2

    def test_get_label_items_assert_correct_items_retrieved(self, 
                                                            view_widget_set_image):
        """
        Test that the expected items are returned correctly.
        """
        test_label_items = [{'label_item_type':'polygon',
                             'label_item_vertices':[(0,0),(0,1),(1,0)],
                             'label_item_uuid':'test_1'},
                             {'label_item_type':'polygon',
                             'label_item_vertices':[(1,1),(1,2),(2,1)],
                             'label_item_uuid':'test_2'}]
        
        view_widget_set_image.setLabelItems(test_label_items)

        items = view_widget_set_image.getLabelItems(get_label_item_pixels=True,
                                         get_label_item_brect=True)

        expected_items = [{'label_item_type': 'polygon', 
                        'label_item_vertices': [(0.0, 0.0), (0.0, 1.0), (1.0, 0.0), (0.0, 0.0)], 
                        'label_item_uuid': 'test_1', 
                        'label_item_pixels': [(0, 0)], 
                        'label_item_bounding_rect': [(0, 0), (1, 0), (1, 1), (0, 1)]}, 
                        {'label_item_type': 'polygon', 
                        'label_item_vertices': [(1.0, 1.0), (1.0, 2.0), (2.0, 1.0), (1.0, 1.0)], 
                        'label_item_uuid': 'test_2', 
                        'label_item_pixels': [(1, 1)], 
                        'label_item_bounding_rect': [(1, 1), (2, 1), (2, 2), (1, 2)]}]

        assert items == expected_items
        
    def test_get_label_item_pixels_assert_correct_values(self, 
                                                         view_widget_set_image):
        """
        Test that the correct pixel values are returned.
        """
        test_label_items = [{'label_item_type':'polygon',
                             'label_item_vertices':[(0,0),(0,1),(1,0)],
                             'label_item_uuid':'test_1'},
                             {'label_item_type':'polygon',
                             'label_item_vertices':[(1,1),(1,2),(2,1)],
                             'label_item_uuid':'test_2'}]
        
        view_widget_set_image.setLabelItems(test_label_items)

        label_item_pixels = view_widget_set_image.getLabelItemPixels()

        expected_label_item_pixels = [{'label_item_pixels': [(0, 0)]}, 
                                    {'label_item_pixels': [(1, 1)]}]

        assert label_item_pixels == expected_label_item_pixels

    def test_add_label_graphics_item_assert_item_added(self, 
                                                       view_widget_set_image):
        """
        Test that the graphics item is correctly added.
        """
        label_item = DummyQGraphicsItem()

        view_widget_set_image.addLabelGraphicsItem(label_item)

        assert len(view_widget_set_image.label_items) == 1

        assert view_widget_set_image.label_items[0] == label_item

    def test_clear_image_assert_image_cleared(self, 
                                              view_widget_set_image):
        """
        Test that the image is cleared.
        """
        view_widget_set_image.clearImage()

        assert view_widget_set_image.base_image_item == None
        assert view_widget_set_image.label_items == []
        # Should only contain base grid
        assert len(view_widget_set_image.scene.items()) == 1

    def test_clear_label_items_assert_label_items_cleared(self, 
                                                          view_widget_set_image):
        """
        Test that the label items are correctly cleared.
        """
        # Set image
        test_label_items = [{'label_item_type':'polygon',
                             'label_item_vertices':[(0,0),(0,1),(1,0)],
                             'label_item_uuid':'test_1'},
                             {'label_item_type':'polygon',
                             'label_item_vertices':[(1,1),(1,2),(2,1)],
                             'label_item_uuid':'test_2'}]
        
        view_widget_set_image.setLabelItems(test_label_items)

        view_widget_set_image.clearLabelItems()
        assert view_widget_set_image.label_items == []

    def test_add_polygon_assert_polygon_added(self, 
                                              view_widget_set_image):
        """
        Test that the polygon is added.
        """
        view_widget_set_image.addPolygon()

        assert len(view_widget_set_image.label_items) == 1
        assert type(view_widget_set_image.label_items[0]) == interactive_polygon_item.InteractivePolygon

    def test_add_polygon_assert_correct_polygon_values(self, 
                                                       view_widget_set_image):
        """
        Test that the added polygon had the correct values
        """
        pts = [(0,1),(1,0),(0,0)]
        uuid = 42
        
        view_widget_set_image.addPolygon(pts, uuid)

        item = view_widget_set_image.label_items[0]

        assert item.polygon().value(0).x() == pts[0][0]
        assert item.polygon().value(0).y() == pts[0][1]

        assert item.polygon().value(1).x() == pts[1][0]
        assert item.polygon().value(1).y() == pts[1][1]

        assert item.polygon().value(2).x() == pts[2][0]
        assert item.polygon().value(2).y() == pts[2][1]

        assert item.uuid == uuid

    def test_remove_item_assert_correct_item_removed(self, 
                                                     view_widget_set_image):
        """
        Test that the correct item is removed.
        """
        pts_1 = [(0,1),(1,0)]
        uuid_1 = 1
        pts_2 = [(1,2),(2,1)]
        uuid_2 = 2
        
        view_widget_set_image.addPolygon(pts_1, uuid_1)
        view_widget_set_image.addPolygon(pts_2, uuid_2)

        removed_item = view_widget_set_image.removeItem(0)

        assert len(view_widget_set_image.label_items) == 1

        assert removed_item.uuid == uuid_1
        assert removed_item.polygon().value(0).x() == pts_1[0][0]
        assert removed_item.polygon().value(0).y() == pts_1[0][1]

        assert removed_item.polygon().value(1).x() == pts_1[1][0]
        assert removed_item.polygon().value(1).y() == pts_1[1][1]

    def test_update_vertex_diameters_assert_correct_diameters(self, 
                                                              view_widget_set_image):
        """
        Test that the vertex diameters are computed as expected.
        """
        view_widget_set_image.addPolygon()

        view_widget_set_image.update_vertex_diameters(zoom_level=3)

        view_widget_set_image.label_item_vertex_diameter = 3.0
        view_widget_set_image.zoom_factor = 2.0

        expected_diameter = 48.0

        assert view_widget_set_image.label_items[0].handle_size == expected_diameter


class TestImageGraphicsItem(TestViewWidgetSetup):
    @pytest.fixture()
    def baseImageGraphicsItemWidget(self, qtbot, pyramid_h5, param_default):
        widget = view_widget.BaseImageGraphicsItem(image_file=pyramid_h5,
                                                   original_image_key=param_default['image_key'],
                                                   shadow=0, 
                                                   mid=10, 
                                                   highlight=20)
        return widget
    
    @pytest.fixture()
    def baseImageGraphicsItemWidgetSmallImage(self, qtbot, pyramid_h5_small, param_small):
        widget = view_widget.BaseImageGraphicsItem(image_file=pyramid_h5_small,
                                                   original_image_key=param_small['image_key'],
                                                   shadow=0, 
                                                   mid=10, 
                                                   highlight=20)
        return widget
    
    @pytest.mark.parametrize("new_zoom_level, zoom_factor, expected_scale", 
                             [(1, 2.0, 2.0), 
                              (3, 2.0, 8.0), 
                              (0, 2.0, 1.0), 
                              (-3, 2.0, 1.0),
                              (None, None, 1.0),
                              (2, 3.0, 9.0)])
    def test_update_image_window_assert_scale_correctly(self, 
                                                        baseImageGraphicsItemWidget,
                                                        new_zoom_level,
                                                        zoom_factor,
                                                        expected_scale):
        """
        Test that the graphics object is scaled correctly, 
        given a zoom level and zoom_factor.
        """
        new_coordinates = QRectF(0,0,10,10)

        baseImageGraphicsItemWidget.update_image_window(new_coordinates, 
                                                        new_zoom_level, 
                                                        zoom_factor)
        
        assert baseImageGraphicsItemWidget.scale() == expected_scale

    def test_update_image_window_assert_attributes_updated(self, 
                                                        baseImageGraphicsItemWidget):
        """
        Test that the correct attributes are updated.
        """
        new_coordinates = QRectF(0,0,10,10)
        new_zoom_level = 1
        zoom_factor = 2.0

        baseImageGraphicsItemWidget.update_image_window(new_coordinates=new_coordinates, 
                                                        new_zoom_level=new_zoom_level, 
                                                        zoom_factor=zoom_factor)

        assert baseImageGraphicsItemWidget.current_coordinates == new_coordinates
        assert baseImageGraphicsItemWidget.current_zoom_level == 1

    def test_compute_new_image_levels_assert_correct_image_levels(self,
                                                                  baseImageGraphicsItemWidget,
                                                                  mocker):
        """
        Test that the adjusted image levels are computed as expected
        """

        image = np.array([[0,0,0],[10,10,10],[20,20,20]])
        shadow = 0
        mid = 5
        highlight = 10

        result_image = baseImageGraphicsItemWidget._compute_new_image_levels(image=image,
                                                             shadow=shadow,
                                                             mid=mid,
                                                             highlight=highlight)
        expected_image = np.array([[  0,   0,   0,   0],
                                    [255, 255, 255,   0],
                                    [255, 255, 255,   0]])

        np.testing.assert_array_equal(result_image, expected_image)
        
    def test_compute_new_image_levels_no_contrast(self,
                                                baseImageGraphicsItemWidget):
        """
        Test that correct behaviour occurs when the image has no contrast
        """
        image = np.array([[0,0,0],[0,0,0],[0,0,0]])
        shadow = 0
        mid = 5
        highlight = 10

        result_image = baseImageGraphicsItemWidget._compute_new_image_levels(image=image,
                                                             shadow=shadow,
                                                             mid=mid,
                                                             highlight=highlight)
        expected_image = np.array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])

        np.testing.assert_array_equal(result_image, expected_image)

    def test_auto_set_image_levels_in_bounds_assert_correct_values(self, 
                                                                   baseImageGraphicsItemWidget):
        """
        Test that the correct levels are selected from the crop
        """
        image = np.array([[0,1,2],[5,10,15],[16,17,20]])

        (shadow, mid, highlight) = baseImageGraphicsItemWidget._calculate_auto_image_levels(image)

        assert shadow == 0
        assert mid == 10
        assert highlight == 20

    def test_get_max_zoom_assert_correct(self,
                                         baseImageGraphicsItemWidget):
        """
        Test that the correct max zoom value is returned
        """
        max_zoom = baseImageGraphicsItemWidget.get_max_zoom()

        assert max_zoom == 3

    def test_calculate_crop_assert_correct_pyramid_level_selected_1(self,
                                                                  baseImageGraphicsItemWidget):
        """
        Test that the resulting crop is the right size, and the right part of the image, as expected
        """
        new_coordinates = QRectF(10,10,10,10)
        new_zoom_level = 0
        # Use small tiles for easier testing
        baseImageGraphicsItemWidget.processing_tile_size = 20

        crop = baseImageGraphicsItemWidget._calculate_crop(
            new_coordinates=new_coordinates, 
            new_zoom_level=new_zoom_level,
            shadow = baseImageGraphicsItemWidget.current_shadow,
            mid = baseImageGraphicsItemWidget.current_mid,
            highlight = baseImageGraphicsItemWidget.current_highlight,
            autoset_levels = False
        )

        assert crop.shape == (40,40)
        # "data" is the label used by generate_image utility function
        with h5py.File(baseImageGraphicsItemWidget.image_file, "r") as image_data:
            np.testing.assert_array_equal(crop, image_data["data"][0:40, 0:40])

    def test_calculate_crop_assert_correct_pyramid_level_selected_2(self,
                                                                  baseImageGraphicsItemWidgetSmallImage):
        """
        Test that the resulting crop is the right size, and the right part of the image, as expected
        """
        new_coordinates = QRectF(5,5,5,5)
        new_zoom_level = 3
        # Use small tiles for easier testing
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 20

        crop = baseImageGraphicsItemWidgetSmallImage._calculate_crop(
            new_coordinates=new_coordinates, 
            new_zoom_level=new_zoom_level,
            shadow = baseImageGraphicsItemWidgetSmallImage.current_shadow,
            mid = baseImageGraphicsItemWidgetSmallImage.current_mid,
            highlight = baseImageGraphicsItemWidgetSmallImage.current_highlight,
            autoset_levels = False
        )

        expected_crop = [[  0,  51, 125, 189, 227,   0,  0,   0],
                        [ 51,  92, 156, 213, 248,   0,   0,   0],
                        [125, 156, 207, 254, 255,   0,   0,   0],
                        [189, 213, 254, 255, 255,   0,   0,   0],
                        [227, 248, 255, 255, 255,   0,   0,   0]]

        assert crop.shape == (5,8)
        np.testing.assert_array_equal(crop, expected_crop)

    def test_calculate_crop_assert_correct_pyramid_level_selected_3(self,
                                                                  baseImageGraphicsItemWidgetSmallImage):
        """
        Test that the resulting crop is the right size, and the right part of the image, as expected
        """
        new_coordinates = QRectF(5,5,2,2)
        new_zoom_level = 1
        # Use small tiles for easier testing
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 3

        crop = baseImageGraphicsItemWidgetSmallImage._calculate_crop(
            new_coordinates=new_coordinates, 
            new_zoom_level=new_zoom_level,
            shadow = baseImageGraphicsItemWidgetSmallImage.current_shadow,
            mid = baseImageGraphicsItemWidgetSmallImage.current_mid,
            highlight = baseImageGraphicsItemWidgetSmallImage.current_highlight,
            autoset_levels = False
        )

        expected_crop = [[  0,  75, 142, 201, 255, 255,   0,   0],
                        [ 75, 142, 201, 255, 255, 255,   0,   0],
                        [142, 201, 255, 255, 255, 255,   0,   0],
                        [201, 255, 255, 255, 255, 255,   0,   0],
                        [255, 255, 255, 255, 255, 255,   0,   0],
                        [255, 255, 255, 255, 255, 255,   0,   0]]

        assert crop.shape == (6,8)
        np.testing.assert_array_equal(crop, expected_crop)

    def test_calculate_crop_assert_correct_pyramid_level_selected_4(self,
                                                                  baseImageGraphicsItemWidgetSmallImage):
        """
        Test that the resulting crop is the right size, and the right part of the image, as expected
        """
        new_coordinates = QRectF(500,500,2,2)
        new_zoom_level = 1
        # Use small tiles for easier testing
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 3

        crop = baseImageGraphicsItemWidgetSmallImage._calculate_crop(
            new_coordinates=new_coordinates, 
            new_zoom_level=new_zoom_level,
            shadow = baseImageGraphicsItemWidgetSmallImage.current_shadow,
            mid = baseImageGraphicsItemWidgetSmallImage.current_mid,
            highlight = baseImageGraphicsItemWidgetSmallImage.current_highlight,
            autoset_levels = False
        )

        assert crop == None

    def test_calculate_crop_assert_correct_pyramid_level_selected_5(self,
                                                                  baseImageGraphicsItemWidgetSmallImage):
        """
        Test that the resulting crop is the right size, and the right part of the image, as expected
        """
        new_coordinates = QRectF(5,5,2,2)
        new_zoom_level = -500
        # Use small tiles for easier testing
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 3

        crop = baseImageGraphicsItemWidgetSmallImage._calculate_crop(
            new_coordinates=new_coordinates, 
            new_zoom_level=new_zoom_level,
            shadow = baseImageGraphicsItemWidgetSmallImage.current_shadow,
            mid = baseImageGraphicsItemWidgetSmallImage.current_mid,
            highlight = baseImageGraphicsItemWidgetSmallImage.current_highlight,
            autoset_levels = False
        )
        
        expected_crop = [[  0,  34,  65,  94, 121, 146,   0,   0],
                        [ 34,  65,  94, 121, 146, 170,   0,   0],
                        [ 65,  94, 121, 146, 170, 193,   0,   0],
                        [ 94, 121, 146, 170, 193, 214,   0,   0],
                        [121, 146, 170, 193, 214, 235,   0,   0],
                        [146, 170, 193, 214, 235, 255,   0,   0]]

        assert crop.shape == (6,8)
        np.testing.assert_array_equal(crop, expected_crop)

    def test_collect_processing_tiles_assert_correct_tiles_1(self, baseImageGraphicsItemWidgetSmallImage):
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 3
        with h5py.File(baseImageGraphicsItemWidgetSmallImage.image_file, "r") as image_data:
            pyramid_level = image_data[baseImageGraphicsItemWidgetSmallImage.original_image_key]
            crop = baseImageGraphicsItemWidgetSmallImage._collect_processing_tiles(pyramid_level, 0, 1, 0, 1)

        expected_crop = [[ 0.,  1.,  2.,  3.,  4.,  5.],
                        [ 1.,  2.,  3.,  4.,  5.,  6.],
                        [ 2.,  3.,  4.,  5.,  6.,  7.],
                        [ 3.,  4.,  5.,  6.,  7.,  8.],
                        [ 4.,  5.,  6.,  7.,  8.,  9.],
                        [ 5.,  6.,  7.,  8.,  9., 10.]]
        
        assert crop.shape == (6,6)
        np.testing.assert_array_equal(crop, expected_crop)
    
    def test_collect_processing_tiles_assert_correct_tiles_2(self, baseImageGraphicsItemWidgetSmallImage):
        baseImageGraphicsItemWidgetSmallImage.processing_tile_size = 2
        with h5py.File(baseImageGraphicsItemWidgetSmallImage.image_file, "r") as image_data:
            pyramid_level = image_data[baseImageGraphicsItemWidgetSmallImage.original_image_key]
            crop = baseImageGraphicsItemWidgetSmallImage._collect_processing_tiles(pyramid_level, 2, 5, 3, 6)

        expected_crop = [[10., 11., 12., 13., 14., 15., 16., 17.,],
                        [11., 12., 13., 14., 15., 16., 17., 18.,],
                        [12., 13., 14., 15., 16., 17., 18., 19.,],
                        [13., 14., 15., 16., 17., 18., 19., 20.,],
                        [14., 15., 16., 17., 18., 19., 20., 21.,],
                        [15., 16., 17., 18., 19., 20., 21., 22.,],
                        [16., 17., 18., 19., 20., 21., 22., 23.,],
                        [17., 18., 19., 20., 21., 22., 23., 24.,]]
        
        assert crop.shape == (8,8)
        np.testing.assert_array_equal(crop, expected_crop)

    def test_gamma_correct_assert_correct_values(self, baseImageGraphicsItemWidget):
        """
        Test that an input image is gamma corrected correctly.
        """
        image = np.array([[0.0,0.05,0.1],[0.15,0.2,0.25],[0.3,0.35,0.40]])
        shadow = 0.0
        mid = 0.1
        highlight = 0.35

        result_image = baseImageGraphicsItemWidget._gamma_correct(image, shadow, mid, highlight)

        expected_image = np.array([[0.,0.789,0.858], [0.902,0.934,0.96 ],[0.981,1.,1.]])

        np.testing.assert_array_equal(np.round(result_image, decimals=3), expected_image)

    def test_get_pad_assert_correct_values_1(self, baseImageGraphicsItemWidget):
        """
        Test that the padding is correct.
        """
        image = np.array([[0,0,0],[0,0,0],[0,0,0]])
        result_pad = baseImageGraphicsItemWidget._get_pad(image)
        expected_pad = np.array([[0],[0],[0]])

        np.testing.assert_array_equal(result_pad, expected_pad)

    def test_get_pad_assert_correct_values_2(self, baseImageGraphicsItemWidget):
        """
        Test that the padding is correct.
        """
        image = np.array([[0,0,0,0],[0,0,0,0],[0,0,0,0]])
        result_pad = baseImageGraphicsItemWidget._get_pad(image)
        expected_pad = np.zeros((3,0))

        np.testing.assert_array_equal(result_pad, expected_pad)
    
    def test_get_pad_assert_correct_values_3(self, baseImageGraphicsItemWidget):
        """
        Test that an error is thrown with an incorrect input size.
        """
        image = np.array([[[0,0,0],[0,0,0],[0,0,0]]])

        with pytest.raises(SystemExit) as error:
            baseImageGraphicsItemWidget._get_pad(image)

        assert error.type == SystemExit

    def test_rescale_to_8bit_assert_correct_values(self, baseImageGraphicsItemWidget):
        """
        Test that the image is rescaled correctly.
        """
        image = np.array([[[0,1,2],[3,4,5],[6,7,8]]])

        result_image = baseImageGraphicsItemWidget._rescale_to_8_bit(image)

        expected_image = np.array([[[0,31,63],[95,127,159],[191,223,255]]])

        np.testing.assert_array_equal(result_image, expected_image)
