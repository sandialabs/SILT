import logging
import math
import time
import random
import numpy as np
import scipy
import skimage
import matplotlib.pyplot as plt
from .polygonAssist import (PolygonAssist,PolygonAssistGUI)
from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QLabel,
                             QPushButton,QComboBox, QSizePolicy, QApplication)
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal)

# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(filename='act_cont.log', level=logging.INFO)

class testAssistGUI(QWidget):
    """This is an example implementation of a polygon assist algorithm. It does NOT help with segmentation, 
    but instead randomly moves polygon vertices to demonstrate functionality"""
    alg_options_changed = pyqtSignal(dict)
    
    def __init__(self,
                 parent = None):
        # Call parent class's constructor (__init__ function)
        super(testAssistGUI,self).__init__(parent)
        
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.setInterval(1000)
        self.update_timer.timeout.connect(self._onUpdateAlgOptions)
        self.poly_assist_configs = {'method':None,'options':None}
        self.test="test"
        self._initUI()

    def _initUI(self):
        self.layout = QGridLayout(self)
        
        # Slider for alpha parameter
        paramater_min: int = 1
        paramater_max: int = 10
        self.GUIparts = []
        print(self)
        self.alpha_label = QLabel('Alpha',self)
        self.GUIparts.append(self.alpha_label)
        self.alpha_slider = QSlider(Qt.Horizontal, self)
        self.GUIparts.append(self.alpha_slider)
        self.alpha_slider.setMinimum(paramater_min)
        self.alpha_slider.setMaximum(paramater_max)
        self.alpha_slider.setSliderPosition(1)
        self.alpha_slider.setTracking(True)
          
        self.setOptions()
        
        self.alpha_slider.valueChanged.connect(self._onAlphaSliderMoved)
        self.alpha_slider.setToolTip(str(self.alpha_slider.value()))
        
        self.layout.addWidget(self, 3, 1, 1, 3)
        self.layout.addWidget(self.alpha_label, 5, 1, 1, 1)
        self.layout.addWidget(self.alpha_slider, 5, 2, 1, 2)
 
        self.setLayout(self.layout)
        # Update the size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('update alg op tions')
        self._onUpdateAlgOptions()
        
    def _onUpdateAlgOptions(self):
        self.alg_options_changed.emit(self.getAlgOptions())
             
    def setOptions(self,
                   alpha: int = 1,
                   ):
       
        # Set the slider positions
        # Make sure signals are blocked for this
        self.alpha_slider.blockSignals(True)
        self.alpha_slider.setValue(alpha)
        self.alpha_slider.setToolTip(str(self.alpha_slider.value()))
        self.alpha_slider.blockSignals(False)
        
    def removeGUI(self):
        for GUIpart in self.GUIparts:
            self.layout.removeWidget(GUIpart)
            GUIpart.deleteLater()
            del GUIpart
            
    def getAlgOptions(self):
        alg_options = {
            'alpha':self.alpha_slider.value(),
            }
        return alg_options
        
    def _onAlphaSliderMoved(self,pos):
        """
        """
        self.alpha_slider.setToolTip(str(self.alpha_slider.value())) 
        self.update_timer.start()
        
class testAssist():
    def __init__(self):
        # Call parent class's constructor (__init__ function)
        super().__init__()
    
    def refine_polygon(self,image_chip,vertices,alg_options):
        if alg_options['alpha'] is None:
            alg_options['alpha']=10
        alpha = alg_options['alpha']*100
        plt.clf()
        plt.imshow(image_chip)
        plt.plot(*zip(*vertices), 'r-o')
        # newpts = [(pt[0]+int(random.randrange(1,alpha)-alpha/2),
        #            pt[1]+int(random.randrange(1,10)-alpha/2)) for pt in vertices]
        newpts = [(pt[0]+100,
                   pt[1]+100) for pt in vertices]
        plt.plot(*zip(*newpts), 'g-o')
        plt.savefig('foo.png')
        return newpts
    
        
        