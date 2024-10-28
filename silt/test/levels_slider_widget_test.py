import pytest

from PyQt5.QtCore import Qt

from silt import levels_slider_widget


class TestLevelsSliderWidget:

    @pytest.fixture
    def levelsSliderWidget(self, qtbot):
        widget = levels_slider_widget.LevelsSliderWidget()
        widget.setSliders(20, 200, 220)
        qtbot.addWidget(widget)
        return widget

    @pytest.mark.parametrize("image_max", [100, 10000, -100])
    def test_setImageMaximum_sets_all_max(self, levelsSliderWidget, image_max):
        """
        Test if all sliders are set at their maximum value
        """
        levelsSliderWidget.setImageMaximum(image_max, reset_slider_pos=False)

        # Assert the max for each slider == image_max
        assert levelsSliderWidget.shadow_slider.maximum() == image_max
        assert levelsSliderWidget.midtone_slider.maximum() == image_max
        assert levelsSliderWidget.highlight_slider.maximum() == image_max

    @pytest.mark.parametrize("image_max", [100, 10000, -100])
    def test_setImageMaximum_resets_slider_position(
        self, levelsSliderWidget, image_max
    ):
        """
        Test if the slider position is properly reset
        """
        levelsSliderWidget.setImageMaximum(image_max, reset_slider_pos=True)

        assert levelsSliderWidget.highlight_slider.value() == image_max
        assert levelsSliderWidget.highlight_slider.toolTip() == str(image_max)

    @pytest.mark.parametrize("image_min", [100, 10000, -100])
    def test_setImageMinimum_sets_all_min(self, levelsSliderWidget, image_min):
        """
        Test if all sliders are set at their minimum value
        """
        levelsSliderWidget.setImageMinimum(image_min, reset_slider_pos=False)

        # Assert the max for each slider == image_max
        assert levelsSliderWidget.shadow_slider.minimum() == image_min
        assert levelsSliderWidget.midtone_slider.minimum() == image_min
        assert levelsSliderWidget.highlight_slider.minimum() == image_min

    @pytest.mark.parametrize("image_min", [100, 10000, -100])
    def test_setImageMinimum_resets_slider_position(
        self, levelsSliderWidget, image_min
    ):
        """
        Test if the slider position is properly reset
        """
        levelsSliderWidget.setImageMinimum(image_min, reset_slider_pos=True)

        assert levelsSliderWidget.shadow_slider.value() == image_min
        assert levelsSliderWidget.shadow_slider.toolTip() == str(image_min)

    @pytest.fixture()
    def levelsSliderWidget_set_min_max(self, levelsSliderWidget, request):
        min, max = request.param
        levelsSliderWidget.image_min = min
        levelsSliderWidget.image_max = max
        return levelsSliderWidget

    @pytest.mark.parametrize(
        "levelsSliderWidget_set_min_max, image_mid",
        [((0, 255), 100)],
        indirect=["levelsSliderWidget_set_min_max"],
    )
    def test_setImageMidpoint_sets_midpoint(
        self, levelsSliderWidget_set_min_max, image_mid
    ):
        """
        Test if image midpoint is set properly
        """
        levelsSliderWidget_set_min_max.setImageMidpoint(image_mid)
        # Assert midpoint is image_mid
        assert levelsSliderWidget_set_min_max.image_mid == image_mid
        assert levelsSliderWidget_set_min_max.midtone_slider.value() == image_mid
        assert levelsSliderWidget_set_min_max.midtone_slider.toolTip() == str(image_mid)

    @pytest.mark.parametrize(
        "levelsSliderWidget_set_min_max, image_mid",
        [((0, 255), 10000), ((0, 255), -100)],
        indirect=["levelsSliderWidget_set_min_max"],
    )
    def test_setImageMidpoint_raises_value_error(
        self, levelsSliderWidget_set_min_max, image_mid
    ):
        """
        Test if image midpoint is set properly when out of value range
        """
        # Assert the ValueError is raised properly
        with pytest.raises(ValueError):
            levelsSliderWidget_set_min_max.setImageMidpoint(image_mid)

    @pytest.mark.parametrize(
        "levelsSliderWidget_set_min_max, expected",
        [((0, 10), 5), ((-100, 100), 0)],
        indirect=["levelsSliderWidget_set_min_max"],
    )
    def test_setImageMidpoint_with_none(self, levelsSliderWidget_set_min_max, expected):
        """
        Test if image midpoint is set properly when None is passed
        """
        levelsSliderWidget_set_min_max.setImageMidpoint(None)

        # Assert midpoint is image_mid
        assert levelsSliderWidget_set_min_max.image_mid == expected
        assert levelsSliderWidget_set_min_max.midtone_slider.value() == expected
        assert levelsSliderWidget_set_min_max.midtone_slider.toolTip() == str(expected)

    @pytest.fixture()
    def levelsSliderWidget_set_sliders_min_and_max(self, levelsSliderWidget):
        levelsSliderWidget.shadow_slider.setMinimum(0)
        levelsSliderWidget.shadow_slider.setMaximum(255)
        levelsSliderWidget.midtone_slider.setMinimum(0)
        levelsSliderWidget.midtone_slider.setMaximum(255)
        levelsSliderWidget.highlight_slider.setMinimum(0)
        levelsSliderWidget.highlight_slider.setMaximum(255)

        return levelsSliderWidget

    @pytest.mark.parametrize(
        "shadow_val, midtone_val, highlight_val", [(0, 100, 200), (250, 250, 250)]
    )
    def test_setSliders(
        self,
        levelsSliderWidget_set_sliders_min_and_max,
        shadow_val,
        midtone_val,
        highlight_val,
    ):
        """
        Test that sliders are set properly according to values
        """
        levelsSliderWidget_set_sliders_min_and_max.setSliders(
            shadow_val, midtone_val, highlight_val
        )

        assert (
            levelsSliderWidget_set_sliders_min_and_max.shadow_slider.value()
            == shadow_val
        )
        assert (
            levelsSliderWidget_set_sliders_min_and_max.midtone_slider.value()
            == midtone_val
        )
        assert (
            levelsSliderWidget_set_sliders_min_and_max.highlight_slider.value()
            == highlight_val
        )

        assert (
            levelsSliderWidget_set_sliders_min_and_max.shadow_slider.toolTip()
            == str(shadow_val)
        )
        assert (
            levelsSliderWidget_set_sliders_min_and_max.midtone_slider.toolTip()
            == str(midtone_val)
        )
        assert (
            levelsSliderWidget_set_sliders_min_and_max.highlight_slider.toolTip()
            == str(highlight_val)
        )

    @pytest.mark.parametrize(
        "shadow_val, midtone_val, highlight_val",
        [
            (100, 0, 200),
            (100, 100, 0),
            (-100, 100, 100),
            (1000, 100, 100),
            (100, -100, 100),
            (100, 1000, 100),
            (100, 100, -100),
            (100, 100, 1000),
        ],
    )
    def test_setSliders_raises_value_error(
        self,
        levelsSliderWidget_set_sliders_min_and_max,
        shadow_val,
        midtone_val,
        highlight_val,
    ):
        """
        Test that a ValueError is properly raised if the given value is outside of the proper range
        """
        with pytest.raises(ValueError):
            levelsSliderWidget_set_sliders_min_and_max.setSliders(
                shadow_val, midtone_val, highlight_val
            )

    @pytest.mark.parametrize("pos", [100])
    def test_onShadowSliderMoved(self, levelsSliderWidget, pos):
        """
        Test that the tool tip is properly set.
        """
        levelsSliderWidget._onShadowSliderMoved(pos)

        assert levelsSliderWidget.shadow_slider.toolTip() == str(
            levelsSliderWidget.shadow_slider.value()
        )

    @pytest.mark.parametrize("pos", [1000])
    def test_onShadowSliderMoved_over_midtone(self, levelsSliderWidget, pos):
        """
        Test that shadow slider is properly bounded by midtone slider.
        """
        levelsSliderWidget._onShadowSliderMoved(pos)

        assert (
            levelsSliderWidget.shadow_slider.sliderPosition()
            == levelsSliderWidget.midtone_slider.sliderPosition()
        )

        assert levelsSliderWidget.shadow_slider.toolTip() == str(
            levelsSliderWidget.shadow_slider.value()
        )

    @pytest.mark.parametrize("pos", [200])
    def test_onMidtoneSliderMoved(self, levelsSliderWidget, pos):
        """
        Test that the tool tip is properly set.
        """
        levelsSliderWidget._onMidtoneSliderMoved(pos)

        assert levelsSliderWidget.midtone_slider.toolTip() == str(
            levelsSliderWidget.midtone_slider.value()
        )

    @pytest.mark.parametrize("pos", [-100])
    def test_onMidtoneSliderMoved_under_shadow(self, levelsSliderWidget, pos):
        """
        Test that midtone slider is properly bounded by the shadow slider.
        """
        levelsSliderWidget._onMidtoneSliderMoved(pos)

        assert (
            levelsSliderWidget.midtone_slider.sliderPosition()
            == levelsSliderWidget.shadow_slider.sliderPosition()
        )

        assert levelsSliderWidget.midtone_slider.toolTip() == str(
            levelsSliderWidget.midtone_slider.value()
        )

    @pytest.mark.parametrize("pos", [1000])
    def test_onMidtoneSliderMoved_over_highlight(self, levelsSliderWidget, pos):
        """
        Test that midtone slider is properly bounded by the highlight slider.
        """
        levelsSliderWidget._onMidtoneSliderMoved(pos)

        assert (
            levelsSliderWidget.midtone_slider.sliderPosition()
            == levelsSliderWidget.highlight_slider.sliderPosition()
        )

        assert levelsSliderWidget.midtone_slider.toolTip() == str(
            levelsSliderWidget.midtone_slider.value()
        )

    @pytest.mark.parametrize("pos", [225])
    def test_onHighlightSliderMoved(self, levelsSliderWidget, pos):
        """
        Test that the tool tip is properly set.
        """
        levelsSliderWidget._onHighlightSliderMoved(pos)

        assert levelsSliderWidget.highlight_slider.toolTip() == str(
            levelsSliderWidget.highlight_slider.value()
        )

    @pytest.mark.parametrize("pos", [-100])
    def test_onHighlightSliderMoved_under_midtone(self, levelsSliderWidget, pos):
        """
        Test that highlight slider is properly bounded by midtone slider.
        """
        levelsSliderWidget._onHighlightSliderMoved(pos)

        assert (
            levelsSliderWidget.highlight_slider.sliderPosition()
            == levelsSliderWidget.midtone_slider.sliderPosition()
        )

        assert levelsSliderWidget.highlight_slider.toolTip() == str(
            levelsSliderWidget.highlight_slider.value()
        )
