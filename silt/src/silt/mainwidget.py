#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Code for SILT main application widget, especially
# for handling interactions between the subwidgets via signals
# and slots.  Also communicates with the mainwindow about 
# adding to the undo stack.
#################################################################

import logging

from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QSplitter, 
                             QUndoCommand, QListWidget)
from PyQt5.QtCore import (pyqtSignal)
from os.path import basename
from .multi_input_panel import MultiInputPanel
from .view_widget import ViewWidget

logging.basicConfig(level=logging.INFO)

class MainWidget(QWidget):
    """Main widget in the base application.  Handles the interactive
    widget portions of UI and the communications amongst them.
    """
    
    command_added = pyqtSignal(QUndoCommand)
    series_selection_changed = pyqtSignal(str, str)
    
    def __init__(self, parent=None):
        """Initialize the main widget.
        """
        super(MainWidget, self).__init__(parent)
        self._initUI()
    
    def _initUI(self):
        """Set up the UI.
        """
        self.layout = QHBoxLayout(self)
        self.splitter = QSplitter(self)
        
        self.user_input_widget = MultiInputPanel(self)
        self.splitter.addWidget(self.user_input_widget)
        
        self.image_widget = ViewWidget(parent=self)
        self.splitter.addWidget(self.image_widget)
        
        self.splitter.setSizes([300, 700])
        self.layout.addWidget(self.splitter)
        self.setLayout(self.layout)
        
        # Make signal/slot connections between image viewer
        # and side panel
        self.image_widget.label_item_selection_changed.connect(self.user_input_widget.setCurrentWidget)
        self.image_widget.delete_item_request.connect(self.onDeleteItemRequested)
        self.image_widget.command_added.connect(self._onCommandAdded)
        
        self.user_input_widget.multi_input_panel_selection_changed.connect(
            self.image_widget.setLabelItemSelected)
        self.user_input_widget.command_added.connect(self._onCommandAdded)
    
    
    def setTemplate(self, template_list, template_file: str = None):
        """Set the template for the input rows.
        """
        self.user_input_widget.setTemplate(template_list)
        if template_file is not None:
            self.addDisplayItem(label="Template:",
                                value=basename(template_file),
                                tooltip=template_file)
    
    def setImage(self, 
                 image_file: str, 
                 original_image_key: str, 
                 shadow: int, 
                 mid: int, 
                 highlight: int, 
                 no_pyramid: bool = False):
        """
        Set the image.

        Params:

        image_file: str
            String representing the path to the image H5 file.
        original_image_key: str
            Key value for the original image in the H5 file.
        shadow: int
            Original shadow value of the image.
        mid: int
            Original mid value of the image.
        highlight: int
            Original highlight value of the image.
        no_pyramid: bool
            Whether a image pyramid should be used or not.
        """
        self.image_widget.setImage(
            image_file, 
            original_image_key, 
            shadow, 
            mid, 
            highlight, 
            no_pyramid
        )

    def clearImage(self):
        """Clear the current image
        """
        self.image_widget.clearImage()

    def setImageLevels(self, shadow: int, mid: int, highlight: int):
        self.image_widget.setImageLevels(shadow, mid, highlight)
        
    def autoSetImageLevelsInBounds(self):
        shadow, mid, highlight = self.image_widget.autoSetImageLevelsInBounds()
        return (shadow, mid, highlight)

    def refinePolyPressed(self):
        self.image_widget.refinePoly()
    
    def updatePolyAssistMethod(self, method:str):
        self.image_widget.setPolyAssistMethod(method)
         
    def updatePolyAssistOptions(self,options: dict):   
        self.image_widget.setPolyAssistParamaters(options)
        
    def resetImageLevels(self):
        self.image_widget.resetImageLevels()

    def setListOverlay(self, overlay_list, overlay_item_vertices_key: str = None):
        """Set up an informational overlay of line segments/polygons 
        on top of the image.
        """
        ret = 0
        for item in overlay_list:
            if overlay_item_vertices_key is not None:
                item['overlay_item_vertices_key'] = overlay_item_vertices_key
                
            r = self.image_widget.addOverlayItem(**item)
            if r != 0:
                ret = r

        return ret
            

    def setImageOverlay(self, overlay_image):
        """Set up an informational overlay of another image on top
        of the main image.
        """
        #self.image_widget.setImageOverlay(overlay)
        
        
    def clearOverlay(self):
        """Close/clear any overlays.
        """
        self.image_widget.clearOverlayItems()


    def addDisplayItem(self, label: str, value: str, tooltip: str = None):
        """Add an item to the display panel.  This is just an informational
        item.
        """
        self.user_input_widget.addDisplayItem(label=label,
                                              value=value,
                                              tooltip=tooltip)
        
    
    def setSavedInputs(self, saved_user_inputs_list, saved_label_items_list):
        """Set the previously saved user inputs and image
        labels.
        """
        
        self.image_widget.setLabelItems(saved_label_items_list)
        self.user_input_widget.setAllInputs(saved_user_inputs_list)
    
    
    def getInputs(self,
                  get_label_item_pixels: bool = False,
                  get_label_item_brect: bool = False):
        user_inputs = self.user_input_widget.getInputs()
        label_items = self.image_widget.getLabelItems(get_label_item_pixels,
                                                      get_label_item_brect)
        
        for i in range(len(user_inputs)):
            user_inputs[i].update(label_items[i])
        
        return user_inputs


    def getCoveredPixels(self):
        user_inputs = self.user_input_widget.getInputs()
        label_item_pixels = self.image_widget.getLabelItemPixels()

        for i in range(len(user_inputs)):
            user_inputs[i].update(label_item_pixels[i])
        
        return user_inputs
        #return label_item_pixels
    
    
    def showUUIDs(self, showbool=True):
        self.user_input_widget.showUUIDs(showbool)


    def showOverlay(self, showbool: bool):
        self.image_widget.showOverlay(showbool)
    
    
    def clearInputs(self):
        """Clear the multi-input-panel inputs.
        """
        self.user_input_widget.clearWidgets()
    
    
    def clearDisplayItems(self):
        """Clear the display items in the multi-input-panel.
        """
        self.user_input_widget.clearDisplayItems()


    def removeDisplayItem(self, label: str):
        """Remove the given display item from the 
        multi-input-panel.
        """
        self.user_input_widget.removeDisplayItem(label)
    
    
    def clearLabelItems(self):
        """Clear the image label widget items.
        """
        self.image_widget.clearLabelItems()
        
    
    def setLabelItemStyleOptions(self, label_item_options: dict):
        self.image_widget.setLabelItemStyleOptions(label_item_options)
        
    
    def addPolygon(self):
        """Add a polygon.
        This includes adding a row to the MultiInputPanel widget
        and adding a polygon item to the scene.
        """
        cmd = commandAddPolygon(self.user_input_widget, self.image_widget)
        self.command_added.emit(cmd)
    
    
    def startSeriesMode(self, filelist: list):
        """Starts up the series mode of SILT by adding a
        QListWidget file selection panel.
        """
        # Add the series selection widget to the layout
        self.series_selection_widget = QListWidget(self)
        self.series_selection_widget.addItems(filelist)
        self.splitter.addWidget(self.series_selection_widget)
        self.setLayout(self.layout)
        
    
    def quitSeriesMode(self):
        """Stops the series mode of SILT.
        """
        self.series_selection_widget.blockSignals(True)
        self.series_selection_widget.clear()
        #self.splitter.removeWidget(self.series_selection_widget)
        self.series_selection_widget.setParent(None)
        del(self.series_selection_widget)
        
        self.setLayout(self.layout)
    
    
    #########
    # SLOTS #
    #########
    
    def onDeleteItemRequested(self, index: int):
        cmd = commandDeleteItem(self.user_input_widget, self.image_widget, index)
        self.command_added.emit(cmd)
    
    def _onCommandAdded(self, cmd: QUndoCommand):
        self.command_added.emit(cmd)
    

class commandAddPolygon(QUndoCommand):
    """Class to control undo/redo of adding
    a polygon to the scene.
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.
    """
    
    def __init__(self, user_input_widget, image_widget, text="Add polygon", parent=None):
        super(commandAddPolygon, self).__init__(text, parent)
        self.user_input_widget = user_input_widget
        self.image_widget = image_widget
        self.polygon_item = None
        self.input_row = None
        self.item_ind = None
        
    def redo(self):
        # Add the polygon
        # If it was created, un-done, then re-done, we want
        # to add it back to the original spot with its
        # original uuid
        if self.polygon_item is not None and self.input_row is not None:
            self.image_widget.addLabelGraphicsItem(self.polygon_item, 
                                                   index=self.item_ind)
            #self.user_input_widget.addInputRowWidget(self.input_row, 
            #                                         index=self.item_ind)
            self.user_input_widget.insertRowWidget(self.input_row, 
                                                   index=self.item_ind)
        
        # Otherwise we're just making a new polygon
        else:
            self.image_widget.addPolygon()
            items = self.image_widget.getLabelItems()
            self.item_ind = len(items) - 1
            uuid = items[self.item_ind]['label_item_uuid']
            self.user_input_widget.addNewRowWidget(uuid = uuid)
            
    
    def undo(self):
        
        # Delete the polygon from the scene
        self.polygon_item = self.image_widget.removeItem(self.item_ind)
        self.input_row = self.user_input_widget.removeWidget(self.item_ind)



class commandDeleteItem(QUndoCommand):
    """Class to control undo/redo of deleting
    a polygon from the scene.
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.
    """
    
    def __init__(self, user_input_widget, image_widget, index, text=None, parent=None):
        
        if text is None:
            text = 'Delete {}'.format(image_widget.getLabelItems()[index]['label_item_type'])
        
        super(commandDeleteItem, self).__init__(text, parent)
        self.user_input_widget = user_input_widget
        self.image_widget = image_widget
        self.index = index
        self.del_item = None
        self.del_input_row = None
    
    def redo(self):
        # Get the overlay item information
        self.del_item = self.image_widget.removeItem(self.index)
        
        # Get the MultiInputPanel row info
        self.del_input_row = self.user_input_widget.removeWidget(self.index)
    
    def undo(self):
        # Stick the overlay item and input row back into
        # their widgets
        self.image_widget.addLabelGraphicsItem(self.del_item, index=self.index)
        #self.user_input_widget.addInputRowWidget(self.del_input_row, index=self.index)
        self.user_input_widget.insertRowWidget(self.del_input_row, index=self.index)

