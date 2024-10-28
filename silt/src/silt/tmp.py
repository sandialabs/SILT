from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QLabel,
                             QPushButton,QComboBox, QSizePolicy, QApplication)

from PyQt5.QtCore import (Qt, QTimer, pyqtSignal)
import sys
import importlib
from . import utils

            
class PolyAssistWidget(QWidget):
    """A side-bar widget to integrate modular polygon assist algorithms into SILT
    """
    
    alg_options_changed = pyqtSignal(dict)
    alg_options_updated = pyqtSignal(dict)
    alg_method_changed = pyqtSignal(str)
    refine_poly = pyqtSignal()
    reset = pyqtSignal()
    
    def __init__(self,
                 paramater_min: int = -10,
                 paramater_max: int = 10,
                 parent = None):
        """
        Initialize the widget
        """
        super(PolyAssistWidget, self).__init__(parent)
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self._onUpdateAlgOptions)
        self.poly_assist_configs = {'method':None,'options':None}
        self._initUI()

    def _initUI(self):
        """
        Set up the UI
        Individual algorithm UI needs will be instantiated when they are selected.
        """
        # Grid layout
        self.layout = QGridLayout(self)
        
        # Top label
        method_label = QLabel('Polygon Assist Method', self)
        
        #Selection box
        self.assist_method_combobox = QComboBox()
        self.assist_method_combobox.addItems(['Segment Anything Model', 'Active Contour', 'Fake Shift (TEST)'])
        self.assist_method_combobox.setCurrentText('Fake Shift (TEST)')
        self.assist_method_combobox.currentTextChanged.connect(self._onPolyAssistMethodChange) # Connect signal when method changes
        
        # Add initial layout components
        self.layout.addWidget(method_label, 1, 1, 1, 3)
        self.layout.addWidget(self.assist_method_combobox, 2, 1, 1, 3)
        
        # Run 'change method' even on init to get default Alg 
        polygon_assistant = self._onPolyAssistMethodChange() 
        
        # Setup GUI for default Alg
        self.layout = polygon_assistant.setGUI(self.layout)
        polygon_assistant.setsetOptions() # Set default options on init
        self.setLayout(self.layout)

        # Update the size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def _onPolyAssistMethodChange(self):
        """
        On change in method from user, update configs, get new assist class, and send signal to update
        return:
            class for poly_assistant that has inherited from ABC.
        """
        self.poly_assist_configs['method'] = self.assist_method_combobox.currentText()
        poly_assistant = utils.get_poly_assist(self.poly_assist_configs['method'])
        self.alg_method_changed.emit(self.assist_method_combobox.currentText())
        return poly_assistant
      
    def _onUpdateAlgOptions(self):
        if self.assist_method_combobox.currentText() == 'Active Contour':
            alg_options = {
                'alpha':self.alpha_slider.value(),
                'beta':self.beta_slider.value(),
                'gamma':self.gamma_slider.value()
                }
            self.alg_options_updated.emit(self.assist_method_combobox.currentText(),alg_options)

    def _onRefinePolyButtonPressed(self):
        self.refine_poly.emit()
        
    def _onResetButtonPressed(self):
        self.reset.emit()
        self.setSliders(self.paramater_min,
                        self.paramater_mid,
                        self.paramater_max)
            
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PolyAssistWidget()
    ex.show()
    app.exec_()
    app.quit()
