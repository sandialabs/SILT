from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QLabel,
                             QPushButton,QComboBox, QSizePolicy, QApplication)

from PyQt5.QtCore import (Qt, QTimer, pyqtSignal)
import sys
import importlib
from . import utils

class PolyAssistWidget(QWidget):
    """A side-bar widget to integrate modular polygon assist algorithms into SILT
    """
    
    alg_method_changed = pyqtSignal(str)
    refine_poly = pyqtSignal()
    reset = pyqtSignal()
    
    def __init__(self,
                 parent = None):
        """
        Initialize the widget
        """
        super(PolyAssistWidget, self).__init__(parent)
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(1000)
        self.poly_assist_configs = {'method':None,'options':None}
        self.polygon_assistant = None
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
        
        # Refine Polygon button
        self.refine_poly_button = QPushButton('Refine Polygon', self)
        self.refine_poly_button.setToolTip('Refine the polygon to the target using a contouring algorithm')
        self.refine_poly_button.clicked.connect(self._onRefinePressed)
        
        #Selection box
        self.assist_method_combobox = QComboBox()
        self.assist_method_combobox.addItems(['Segment Anything Model', 'Active Contour', 'Fake Shift (TEST)'])
        self.assist_method_combobox.setCurrentText('Active Contour')
        self.assist_method_combobox.currentTextChanged.connect(self._onPolyAssistMethodChange) # Connect signal when method changes
        
        # Add initial layout components
        self.layout.addWidget(self.refine_poly_button, 1, 1, 1, 3)
        self.layout.addWidget(method_label, 2, 1, 1, 3)
        self.layout.addWidget(self.assist_method_combobox, 3, 1, 1, 3)
        self.setLayout(self.layout)
        # Update the size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Run 'change method' even on init to get default Alg 
        self._onPolyAssistMethodChange()

    def _onPolyAssistMethodChange(self):
        
        """
        On change in method from user, update configs, get new assist class, and send signal to update
        return:
            class for poly_assistant that has inherited from ABC.
        """
        self.poly_assist_configs['method'] = self.assist_method_combobox.currentText()
        self.polygon_assistant = self.poly_assist_configs['method']
        self.alg_method_changed.emit(self.assist_method_combobox.currentText())    
            
    def _onRefinePressed(self):
        self.refine_poly.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = PolyAssistWidget()
    ex.show()
    app.exec_()
    app.quit()
