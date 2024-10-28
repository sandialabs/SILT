from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QLabel,
                             QPushButton, QSizePolicy, QApplication)
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal)
import sys

class LevelsSliderWidget(QWidget):
    """A widget with three sliders to adjust image levels
    (shadows, midtones, and highlights) for improving contrast.
    
    This widget is intended to be used within an imaging
    application.  Its signals should interact directly with the
    image.
    
    Signals
    -------
    levels_changed -> int, int, int
        Emits the 3 slider values: shadows, midtones, and 
        highlights, on every slider movement.
    levels_updated -> int, int, int 
        Emits the 3 slider values: shadows, midtones, and 
        highlights, only after slider movement has stopped for 
        an entire second.
    auto_range
        Signals that the user pressed the "Auto range" button.
    reset
        Signals that the user pressed the "Reset" button
    
    Attributes
    ----------
    image_min: int
        The minimum possible value for all sliders.
    image_max: int
        The maximum possible value for all sliders.
    """
    
    levels_changed = pyqtSignal(int, int, int)
    levels_updated = pyqtSignal(int, int, int)
    auto_range = pyqtSignal()
    reset = pyqtSignal()
    
    def __init__(self,
                 image_min: int = 0,
                 image_max: int = 255,
                 parent = None):
        """Initialize the widget
        """
        super(LevelsSliderWidget, self).__init__(parent)
        self.image_min = image_min
        self.image_max = image_max
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self._onUpdateLevels)
        self._initUI()

    def _initUI(self):
        """Set up the UI
        """
        layout = QGridLayout(self)
        
        # Slider for shadows
        shadow_label = QLabel('Shadows', self)
        self.shadow_slider = QSlider(Qt.Horizontal, self)
        self.shadow_slider.setMinimum(self.image_min)
        self.shadow_slider.setMaximum(self.image_max)
        self.shadow_slider.setTracking(True)
        self.shadow_slider.setSliderPosition(self.image_min)
        self.shadow_slider.valueChanged.connect(self._onShadowSliderMoved)
        self.shadow_slider.setToolTip(str(self.shadow_slider.value()))
        
        # Slider for midtones
        midtone_label = QLabel('Midtones', self)
        self.midtone_slider = QSlider(Qt.Horizontal, self)
        self.midtone_slider.setMinimum(self.image_min)
        self.midtone_slider.setMaximum(self.image_max)
        self.midtone_slider.setTracking(True)
        self.image_mid = int((self.image_max - self.image_min)/2)
        self.midtone_slider.setSliderPosition(self.image_mid)
        self.midtone_slider.valueChanged.connect(self._onMidtoneSliderMoved)
        self.midtone_slider.setToolTip(str(self.midtone_slider.value()))
        
        # Slider for highlights
        highlight_label = QLabel('Highlights', self)
        self.highlight_slider = QSlider(Qt.Horizontal, self)
        self.highlight_slider.setMinimum(self.image_min)
        self.highlight_slider.setMaximum(self.image_max)
        self.highlight_slider.setTracking(True)
        self.highlight_slider.setSliderPosition(self.image_max)
        self.highlight_slider.valueChanged.connect(self._onHighlightSliderMoved)
        self.highlight_slider.setToolTip(str(self.highlight_slider.value()))
        
        # Auto update button
        auto_range_button = QPushButton('Auto Range', self)
        auto_range_button.clicked.connect(self._onAutoRangeButtonPressed)
        auto_range_button.setToolTip('Auto adjust the shadows and highlights')
        
        # Reset button
        reset_button = QPushButton('Reset', self)
        reset_button.clicked.connect(self._onResetButtonPressed)
        reset_button.setToolTip('Reset to original image levels')
        
        # Add everything to the layout
        layout.addWidget(shadow_label, 1, 1, 1, 1)
        layout.addWidget(self.shadow_slider, 1, 2, 1, 2)
        layout.addWidget(midtone_label, 2, 1, 1, 1)
        layout.addWidget(self.midtone_slider, 2, 2, 1, 2)
        layout.addWidget(highlight_label, 3, 1, 1, 1)
        layout.addWidget(self.highlight_slider, 3, 2, 1, 2)
        layout.addWidget(auto_range_button, 4, 1, 1, 3)
        layout.addWidget(reset_button, 5, 1, 1, 3)
        
        self.setLayout(layout)

        # Update the size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
    def setImageMaximum(self,
                        image_max: int,
                        reset_slider_pos: bool = True):
        """Sets the maximum possible value for all sliders.
        """
        self.image_max = image_max

        # Set the slider maximum values
        # Make sure signals are blocked in case the sliders move
        self.shadow_slider.blockSignals(True)
        self.shadow_slider.setMaximum(image_max)
        self.shadow_slider.blockSignals(False)

        self.midtone_slider.blockSignals(True)
        self.midtone_slider.setMaximum(image_max)
        self.midtone_slider.blockSignals(False)
        
        self.highlight_slider.blockSignals(True)
        self.highlight_slider.setMaximum(image_max)
        if reset_slider_pos:
            self.highlight_slider.setValue(image_max)
            self.highlight_slider.setToolTip(str(self.highlight_slider.value()))
        self.highlight_slider.blockSignals(False)

    def setImageMinimum(self,
                        image_min: int,
                        reset_slider_pos: bool = True):
        """Sets the minimum possible value for all sliders.
        """
        self.image_min = image_min

        # Set the slider min values
        # Make sure signals are blocked in case the sliders move
        self.shadow_slider.blockSignals(True)
        self.shadow_slider.setMinimum(image_min)
        if reset_slider_pos:
            self.shadow_slider.setValue(image_min)
            self.shadow_slider.setToolTip(str(self.shadow_slider.value()))
        self.shadow_slider.blockSignals(False)
        
        self.midtone_slider.blockSignals(True)
        self.midtone_slider.setMinimum(image_min)
        self.midtone_slider.blockSignals(False)
        
        self.highlight_slider.blockSignals(True)
        self.highlight_slider.setMinimum(image_min)
        self.highlight_slider.blockSignals(False)

    def setImageMidpoint(self, image_mid: int = None):
        if image_mid is None:
            self.image_mid = int((self.image_max - self.image_min)/2) + self.image_min
        else:
            # If image_mid is outside min/max bounds, raise ValueError
            if (image_mid < self.image_min) or (image_mid > self.image_max):
                raise ValueError("image_mid value outside of image min/max range.")
            self.image_mid = image_mid
        
        self.midtone_slider.blockSignals(True)
        self.midtone_slider.setValue(self.image_mid)
        self.midtone_slider.setToolTip(str(self.midtone_slider.value()))
        self.midtone_slider.blockSignals(False)

    def setSliders(self,
                   shadow_val: int,
                   midtone_val: int,
                   highlight_val: int):
        
        # Make sure all the values are in the correct ranges
        if shadow_val > midtone_val:
            raise ValueError("Shadow value cannot be greater than midtone value.")
        if highlight_val < midtone_val:
            raise ValueError("Midtone value cannot be greater than highlight value.")
        if shadow_val < self.shadow_slider.minimum():
            raise ValueError("Shadow value cannot be less than shadow minimum.")
        if shadow_val > self.shadow_slider.maximum():
            raise ValueError("Shadow value cannot be greater than shadow maximum.")
        if midtone_val < self.midtone_slider.minimum():
            raise ValueError("Midtone value cannot be less than midtone minmum.")
        if midtone_val > self.midtone_slider.maximum():
            raise ValueError("Midtone value cannot be greater than midtone maximum.")
        if highlight_val < self.highlight_slider.minimum():
            raise ValueError("Highlight value cannot be less than highlight minmum.")
        if highlight_val > self.highlight_slider.maximum():
            raise ValueError("Highlight value cannot be greater than highlight maximum.")
        
        # Set the slider positions
        # Make sure signals are blocked for this
        self.shadow_slider.blockSignals(True)
        self.shadow_slider.setValue(shadow_val)
        self.shadow_slider.setToolTip(str(self.shadow_slider.value()))
        self.shadow_slider.blockSignals(False)
        
        self.midtone_slider.blockSignals(True)
        self.midtone_slider.setValue(midtone_val)
        self.midtone_slider.setToolTip(str(self.midtone_slider.value()))
        self.midtone_slider.blockSignals(False)
        
        self.highlight_slider.blockSignals(True)
        self.highlight_slider.setValue(highlight_val)
        self.highlight_slider.setToolTip(str(self.highlight_slider.value()))
        self.highlight_slider.blockSignals(False)
        
    #########
    # SLOTS #
    #########
    def _onShadowSliderMoved(self, pos):
        """Upper bounds the shadow slider with the midtone
        slider.  Also starts the update timer and emits the 
        levels_changed signal.
        """
        if pos > self.midtone_slider.sliderPosition():
            self.shadow_slider.blockSignals(True)
            self.shadow_slider.setSliderPosition(self.midtone_slider.sliderPosition())
            self.shadow_slider.blockSignals(False)
        self.shadow_slider.setToolTip(str(self.shadow_slider.value()))
        
        self.update_timer.start()
        self.levels_changed.emit(self.shadow_slider.value(),
                                 self.midtone_slider.value(),
                                 self.highlight_slider.value())
    
    def _onMidtoneSliderMoved(self, pos):
        """Bounds the midtone slider with the shadow slider and
        the highlight slider.  Also starts the update timer and 
        emits the levels_changed signal.
        """
        # Keep lower bound
        if pos < self.shadow_slider.sliderPosition():
            self.midtone_slider.blockSignals(True)
            self.midtone_slider.setSliderPosition(self.shadow_slider.sliderPosition())
            self.midtone_slider.blockSignals(False)
            
        # Keep upper bound
        if pos > self.highlight_slider.sliderPosition():
            self.midtone_slider.blockSignals(True)
            self.midtone_slider.setSliderPosition(self.highlight_slider.sliderPosition())
            self.midtone_slider.blockSignals(False)
            
        self.midtone_slider.setToolTip(str(self.midtone_slider.value()))
        
        self.update_timer.start()
        self.levels_changed.emit(self.shadow_slider.value(),
                                 self.midtone_slider.value(),
                                 self.highlight_slider.value())
    
    def _onHighlightSliderMoved(self, pos):
        """Bounds the highlight slider with the midtone slider.
        Also starts the update timer and emits the 
        levels_changed signal.
        """
        # Keep lower bound
        if pos < self.midtone_slider.sliderPosition():
            self.highlight_slider.blockSignals(True)
            self.highlight_slider.setSliderPosition(self.midtone_slider.sliderPosition())
            self.highlight_slider.blockSignals(False)
        self.highlight_slider.setToolTip(str(self.highlight_slider.value()))
        
        self.update_timer.start()
        self.levels_changed.emit(self.shadow_slider.value(),
                                 self.midtone_slider.value(),
                                 self.highlight_slider.value())

    def _onUpdateLevels(self):
        self.levels_updated.emit(self.shadow_slider.value(),
                                 self.midtone_slider.value(),
                                 self.highlight_slider.value())

    def _onAutoRangeButtonPressed(self):
        self.auto_range.emit()

    def _onResetButtonPressed(self):
        self.reset.emit()
        self.setSliders(self.image_min,
                        self.image_mid,
                        self.image_max)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = LevelsSliderWidget()
    ex.show()
    ex.setSliders(20, 200, 220)
    app.exec_()
    app.quit()
