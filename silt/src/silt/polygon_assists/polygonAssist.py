from abc import ABC, abstractmethod
from PyQt5.QtWidgets import (QWidget)
from .image_preprocessor import ImagePrepreprocessor

# Do not instantiate an instance of this class. This is only for base class
class PolygonAssistGUI(QWidget):
    """Abstract class only used for inheritance. Instantiate the derived classes instead""" 
    def __init__(self):
        super().__init__()
        pass
    
    @abstractmethod
    def setGUI(self):
        pass
    
    @abstractmethod
    def setOptions(self):
        pass
    
    @abstractmethod
    def removeGUI(self):
        pass
    
    @abstractmethod
    def getAlgOptions(self):
        pass
         
# Do not instantiate an instance of this class. This is only for base class
class PolygonAssist(ABC):
    """Abstract class only used for inheritance. Instantiate the derived classes instead""" 
    def __init__(self):
        pass

    @abstractmethod
    def refinePolygon(self):
        """Redefine (override) this method in the derived classes"""
        # if self.processed_img is None or self.poly is None:
        # We should ensure that img and poly are already set
        raise Exception("Parent class method not overriden")
        # return new_polygon
    
    