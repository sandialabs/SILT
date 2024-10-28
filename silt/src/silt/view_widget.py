#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Class definitions for ViewWidget and
# BaseImageGraphicsItem.  The QUndo commands for all of the
# overlay items are controlled via the ViewWidget by
# watching the mouse events and checking the appropriate
# overlay items for changes.
#################################################################

from PyQt5.QtWidgets import (QGraphicsView, QGraphicsScene, 
                             QGraphicsItem, QUndoCommand,
                             QGraphicsLineItem)
from PyQt5.QtGui import (QImage, QPixmap, QPolygonF,
                         QPen, QColor)
from PyQt5.QtCore import (Qt, QPointF, QPoint, QRectF, pyqtSignal)
import h5py
from .interactive_polygon_item import InteractivePolygon
import numpy as np
import sys
from typing import Union
import logging
from . import utils

logging.basicConfig(level=logging.INFO)


#####################################################
# Widget for viewing and interacting with the image #
#####################################################
class ViewWidget(QGraphicsView):
    """
    Base class for viewing the image and its overlays
    
    Signals
    -------
    label_item_selection_changed -> int
    delete_item_request -> int 
    command_added -> QUndoCommand
    slider_released -> 
    
    Attributes
    ----------
    previous_item_selected: bool
    label_item_line_width: float
    label_item_vertex_diameter: float
    label_item_line_color: RGBA list of 8bit uint
    label_item_vertex_color: RGBA list of 8bit uint
    base_image_item: BaseImageGraphicsItem
    label_items: list
    overlay_items: list
    scene: QGraphicsScene
    """
    
    label_item_selection_changed = pyqtSignal(int)
    #overlay_item_deleted = pyqtSignal(int)
    delete_item_request = pyqtSignal(int)
    command_added = pyqtSignal(QUndoCommand)
    previous_item_selected = None
    label_item_line_width = 1.0
    label_item_vertex_diameter = 3.0
    label_item_line_color = [255, 0, 255, 150]
    label_item_vertex_color = [0, 0, 255, 255]
    
    def __init__(self, 
                 image_file: str=None,
                 label_items: list=None,
                 overlay_items: list=None,
                 label_item_style_options=None,
                 parent=None):
        
        super(ViewWidget, self).__init__(parent)
        
        self.base_image_item = None
        
        if label_items:
            self.label_items = label_items
        else:
            self.label_items = []
        
        if overlay_items:
            self.overlay_items = overlay_items
        else:
            self.overlay_items = []
        
        self.poly_assist_configs = {'method':None,'options':None}     
        self._initScene()
        
        if image_file is not None:
            self.setImage(image_file)
            if label_items != []:
                self.setLabelItems(label_items)
        
        if label_item_style_options is not None:
            self.setLabelItemStyleOptions(label_item_style_options)
        
        self.scene.update(self.scene.sceneRect())

        # Anchor zoom to mouse
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Make connections with central widget
        self.verticalScrollBar().sliderReleased.connect(self._onSliderReleased)
        self.horizontalScrollBar().sliderReleased.connect(self._onSliderReleased)

        # Define buffer around scene window
        self.scene_buffer = 10

        # Define zoom factor
        self.zoom_factor = 2.0
        
        # Init segmenters for polygon assist
        #self.activeContourSegmenter = active_contours_segmenter()
        #self.samSegmenter = sam_segmenter()
    
    ##########################################################
    # PRIVATE
    ##########################################################
    
    def _initScene(self):
        """Initialize the UI for the image view.
        """
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setDragMode(QGraphicsView.ScrollHandDrag)
    
    ##########################################################
    # PUBLIC
    ##########################################################
    
    def initLabelItems(self, label_items):
        """If there were items that were saved over this
        image, initialize them.  Otherwise, initialize an
        empty list.
        """
        
        if label_items is None:
            self.label_items = []
        
        else:
            self.label_items = label_items
            self.setLabelItems(self.label_items)
    
    def setLabelItemStyleOptions(self, label_item_style_options: dict):
        """Set up the style of the overlay items.
        """
        if 'line_width' in label_item_style_options.keys():
            self.label_item_line_width = label_item_style_options['line_width']
        if 'vertex_diameter' in label_item_style_options.keys():
            self.label_item_vertex_diameter = label_item_style_options['vertex_diameter']
        if 'line_color' in label_item_style_options.keys():
            self.label_item_line_color = label_item_style_options['line_color']
        if 'vertex_color' in label_item_style_options.keys():
            self.label_item_vertex_color = label_item_style_options['vertex_color']
        
        for item in self.label_items:
            item.setLineWidth(self.label_item_line_width)
            item.setVertexDiameter(self.label_item_vertex_diameter)
            item.setLineColor(self.label_item_line_color)
            item.setVertexColor(self.label_item_vertex_color)
        
        self.scene.update(self.scene.sceneRect())
    
    
    def wheelEvent(self, event):
        """Swallow mouse wheel for image view scaling
        """
        pt = event.angleDelta()
        self._update_zoom(pt) 


    def _update_zoom(self, pt: QPoint):
        # Zoom in
        if pt.y() > 0:
            if self.base_image_item is not None:
                bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
                # If view bounds are smaller than a pixel, stop zoom
                if (bounds.height() < 1 or
                    bounds.width() < 1):
                    return
            self.scale(self.zoom_factor, self.zoom_factor)
            self.current_zoom_level -= 1
        # Zoom out
        elif pt.y() < 0:
            if self.base_image_item is not None:
                bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
                # If view bounds are larger than the size of the image, stop zoom
                if (((bounds.width()) > self.scene.width() and
                    (bounds.height()) > self.scene.height())):
                    return
            self.scale((1/self.zoom_factor), (1/self.zoom_factor))
            self.current_zoom_level += 1

        bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
        if self.base_image_item is not None:
            self.base_image_item.update_image_window(new_coordinates=bounds, 
                                                     new_zoom_level=self.current_zoom_level,
                                                     zoom_factor=self.zoom_factor)

        self.update_vertex_diameters(self.current_zoom_level)


    def setImage(self, 
                 image_file: str, 
                 original_image_key: str, 
                 shadow: int, 
                 mid: int,
                 highlight: int,
                 no_pyramid: bool):
        """
        Set up the QGraphicsItem that manages the image.

        image_file: str - the path to the H5 image file
        original_image_key - the key to the original image in the H5 file
        shadow - min image value currently set, used for syncing UI with image
        mid - mid image value currently set, used for syncing UI with image
        highlight - max image value currently set, used for syncing UI with image
        no_pyramid - False if pyramid isn't being used, won't dynamically load tiles
        """
        self.clearImage()
        if image_file is not None:
            with h5py.File(image_file, "r") as image_data:
                x_bound = image_data[original_image_key].shape[1]
                y_bound = image_data[original_image_key].shape[0]

            self.scene.setSceneRect(0 - (self.scene_buffer), 
                                    0 - (self.scene_buffer), 
                                    x_bound + (self.scene_buffer), 
                                    y_bound + (self.scene_buffer))

            self.setAlignment(Qt.AlignLeft | Qt.AlignTop)

            self.base_image_item = BaseImageGraphicsItem(
                image_file, 
                original_image_key, 
                shadow, 
                mid, 
                highlight, 
                no_pyramid
            )
            
            self.base_image_item.setPos(0, 0)

            self.current_zoom_level = self.base_image_item.get_zoom_level()

            self.fitInView(self.base_image_item, Qt.KeepAspectRatio)
            self.verticalScrollBar().setSliderPosition(0)
            self.horizontalScrollBar().setSliderPosition(0)

            bounds = self.mapToScene(self.viewport().geometry()).boundingRect()

            self.base_image_item.update_image_window(new_coordinates=bounds, 
                                                     new_zoom_level=self.current_zoom_level,
                                                     zoom_factor=self.zoom_factor)
            
            # Create "grid" item for polygons
            self.base_grid = BaseGrid(x_bound, y_bound)
            self.base_grid.setPos(0,0)
            
            self.scene.addItem(self.base_image_item)
            self.scene.addItem(self.base_grid)

        self.scene.update(self.scene.sceneRect())
    
    
    def setLabelItems(self, label_items: list):
        """Set up the previously saved overlay items, like
        polygons, rectangles, etc.
        
        Parameters
        ----------
        label_items: list of dict
            Each dictionary has two entries.  One is
            'label_item_type', which describes the type of
            item (accepted values: 'polygon'), and the other
            is 'label_item_vertices', which is a list of 
            tuples of (x, y) pixel locations of item vertices.
        """
        
        for item in label_items:
            if item['label_item_type'].lower() == 'polygon':
                self.addPolygon(pts=item['label_item_vertices'], 
                                uuid=item['label_item_uuid'])

        # Set view center to the first item on the list
        self.centerOn(self.label_items[0])
    
    
    def getLabelItems(self,
                        get_label_item_pixels: bool = False,
                        get_label_item_brect: bool = False):
        """Public function to collect the info from the overlay 
        items.
        """
        items = []
        for item in self.label_items:
            it_dict = {'label_item_type': item.item_type,
                       'label_item_vertices': item.getVertices(),
                       'label_item_uuid': item.getUUID()}
            
            if get_label_item_pixels:
                it_dict['label_item_pixels'] = item.getCoveredPixels()
            if get_label_item_brect:
                it_dict['label_item_bounding_rect'] = item.getBoundingRect()
            items.append(it_dict)
        return items


    def getLabelItemPixels(self):
        """Public function to get the list of covered pixels for
        every overlay item in the scene.
        """
        items = []
        for item in self.label_items:
            items.append({'label_item_pixels': item.getCoveredPixels()})

        return items
    
    
    #def addOverlayItem(self, overlay_item: dict, index=None):
    #    """NOT CURRENTLY USED
    #    Add an overlay item to the scene.
    #    
    #    Parameters
    #    ----------
    #    overlay_item: dict
    #        Has 3 required entries and 1 optional.
    #        Required entries:
    #          - 'label_item_type': describes the type of item
    #          - 'label_item_vertices': the vertex pixel locations
    #          - 'label_item_uuid': unique identifier for the item
    #        Optional entry:
    #          - 'label_item_pixels': the pixels that are bounded
    #            by the overlay item
    #    """
    #    if overlay_item['label_item_type'].lower() == 'polygon':
    #        self.addPolygon(pts=overlay_item['label_item_vertices'], 
    #                        uuid=overlay_item['label_item_uuid'],
    #                        index=index)
    
    
    def addLabelGraphicsItem(self, label_item, index=None):
        """Add a label item to the scene.
        
        Parameters
        ----------
        label_item: QGraphicsItem
            Custom QGraphicsItem which has several required 
            functions and parameters.
        index: int (optional)
        """
        if index is None:
            self.label_items.append(label_item)
            self.label_items[-1].setParentItem(self.base_grid)
        else:
            self.label_items.insert(index, label_item)
            self.label_items[index].setParentItem(self.base_grid)
        
        self.scene.update(self.scene.sceneRect())
        
    
    def clearImage(self):
        """Clear the view of the current image.
        """
        # Note: if parent/children set correctly, probably
        # unnecessary to clear items as removing the
        # base image item will clear all children items.
        if self.base_image_item is not None:
            self.clearLabelItems()
            self.scene.removeItem(self.base_image_item)
            self.scene.update(self.scene.sceneRect())
            self.base_image_item = None
    
    
    def clearLabelItems(self):
        """Clear the view of the current label items.
        """
        if (self.label_items is not None and
            self.label_items != []):
            for _ in range(len(self.label_items)):
                it = self.removeItem(0)
                del(it)
                #item.setParentItem(None)
                #self.scene.update(self.scene.sceneRect())
            self.label_items = []
    
    def addPolygon(self, pts=None, uuid=None, index=None, poly: QPolygonF=None):
        """Add a polygon to the scene.
        """
        if not poly:
            # If no starting points are input, create a triangle about 1/5
            # the size of the viewport.
            if pts is None:
                viewport = self.viewport().rect()
                #view_center = self.mapToScene(self.viewport().rect().center())
                view_center = self.mapToScene(viewport.center())
                view_height = (self.mapToScene(viewport.bottomLeft()).y() - 
                            self.mapToScene(viewport.topLeft()).y())
                view_width = (self.mapToScene(viewport.topRight()).x() - 
                            self.mapToScene(viewport.topLeft()).x())
                pts = [QPointF(view_center.x(), view_center.y()),
                    QPointF(view_center.x(), view_center.y()+(view_height/5.0)),
                    QPointF(view_center.x()+(view_width/5.0), view_center.y())]
            else:
                pts = [QPointF(pt[0], pt[1]) for pt in pts]
            
            # Set up the new polygon
            poly = QPolygonF(pts)
        
        if index is None:
            self.label_items.append(InteractivePolygon(poly, self.base_grid))
            index = -1
        
        else:
            self.label_items.insert(index, InteractivePolygon(poly, self.base_grid))
        self.label_items[index].setUUID(uuid)
        
        # Apply the style options to the new polygon
        self.label_items[index].setLineWidth(self.label_item_line_width)
        self.label_items[index].setVertexDiameter(
            self.label_item_vertex_diameter * (self.zoom_factor ** (self.current_zoom_level + 1))
        )
        self.label_items[index].setLineColor(self.label_item_line_color)
        self.label_items[index].setVertexColor(self.label_item_vertex_color)
        
        # Set the "height" of the label item, i.e. which is drawn on top
        # All label items are siblings and they are children of
        # the base image item.  I believe, in terms of layering, they are
        # ordered based on the order they are drawn, so the most recently-
        # drawn item will be on top.
        self.label_items[index].setZValue(1.0)
        
        # Schedule redraw of area of scene
        self.scene.update(self.scene.sceneRect())
    
    def removeItem(self, index: int):
        """Removes an item from the scene and returns it.
        
        Parameters
        ----------
        index: int
            The index of the item to remove
        
        Returns
        -------
        QGraphicsItem subclass
        
        Notes
        -----
        This function simply removes the item from the scene,
        but the item remains in memory.  To truly delete the
        item you must delete the object returned by this
        function.
        """
        del_item = self.label_items.pop(index)
        self.scene.removeItem(del_item)
        return (del_item)


    def addOverlayItem(self, vertices: list = None,
                       overlay_item_vertices: list = None,
                       color: list = [255, 0, 255, 255],
                       style: str = 'solid',
                       line_width: int = None,
                       **kwargs):
        """Add an item for display purposes only.  It cannot be
        interactively moved, resized, etc.  It is drawn under the
        label items.
        
        The only required input is a list of vertices which are 
        used to draw the overlay item.  The vertices are 
        connected with lines defined by the optional `color`, 
        `style`, and `line_width` inputs.  The list of vertices
        may be input via the `vertices`, `overlay_item_vertices`,
        or a custom parameter given by 
        `overlay_item_vertices_key`.
        
        Parameters
        ----------
        vertices : list of tuples, optional
            The list of overlay item vertices in the form of 
            (x, y) tuples.  If the overlay item is meant to be a
            closed polygon, then the last vertex must equal the
            first vertex.
        overlay_item_vertices : list of tuples, optional
            A synonymous input for `vertices`; you only need to
            input one or the other.  If both are inputted, then
            this function defaults to using the list in 
            `vertices`.
        color : list of int, default=[255, 0, 255, 255]
            A length-4 integer list defining RGBA values.  Values
            must be between 0 and 255, inclusive.
        style : {'solid', 'dashed', 'dotted'}, default='solid'
            A string for the line style.
        line_width : int, optional
            The line width of each line segment which connects
            overlay vertices.  Defaults to the same line width
            as the label items, which can be set in the template
            file.
        overlay_item_vertices_key : str, optional
            If input, this is the key that is used to pull the
            vertices out of the kwargs dictionary.  This is only
            used if both `vertices` and `overlay_item_vertices`
            inputs are None.
        """
        # See if there's a specific vertices key to look for:
        ovk = None
        if 'overlay_item_vertices_key' in kwargs.keys():
            ovk = kwargs['overlay_item_vertices_key']
        
        # Don't crash if required key is missing; just return
        if (vertices is None and
            overlay_item_vertices is None and
            ovk is None):
            return -1
        
        # Either vertices or overlay_item_vertices is required
        if vertices is None:
            if overlay_item_vertices is not None:
                vertices = overlay_item_vertices
            elif ovk is not None:
                vertices = kwargs[ovk]
        
        # Set up the line style
        if style.lower() == 'solid':
            qstyle = Qt.SolidLine
        elif style.lower() == 'dashed':
            qstyle = Qt.DashLine
        elif style.lower() == 'dotted':
            qstyle = Qt.DotLine
        else:
            qstyle = Qt.SolidLine
        
        # Set up the line width
        if line_width is None:
            line_width = self.label_item_line_width
        
        i = 1
        overlay_item = []
        while i < len(vertices):
            overlay_item.append(QGraphicsLineItem(vertices[i-1][0],
                                                  vertices[i-1][1],
                                                  vertices[i][0],
                                                  vertices[i][1],
                                                  self.base_grid))
            overlay_item[-1].setPen(QPen(QColor(*color),
                                         line_width,
                                         qstyle,
                                         Qt.RoundCap,
                                         Qt.RoundJoin))
            i += 1
        self.overlay_items.append(overlay_item)
        #self.scene.update(self.scene.sceneRect())
        
        return 0
    

    def removeOverlayItem(self, index):
        """Removes an overlay item from the scene and returns it.
        
        Parameters
        ----------
        index: int
            The index of the item to remove
        
        Returns
        -------
        QGraphicsItem subclass
        
        Notes
        -----
        This function simply removes the item from the scene,
        but the item remains in memory.  To truly delete the
        item you must delete the object returned by this
        function.
        """
        del_items = self.overlay_items.pop(index)
        for del_item in del_items:
            self.scene.removeItem(del_item)
        return (del_items)
    
    
    def clearOverlayItems(self):
        """Delete/free all overlay items.
        """
        if (self.overlay_items is not None and
            self.overlay_items != []):
            for i in range(len(self.overlay_items)):
                it = self.removeOverlayItem(0)
                del(it)
                #item.setParentItem(None)
                #self.scene.update(self.scene.sceneRect())
            self.overlay_items = []


    def showOverlay(self, showbool: bool):
        """Show or hide the overlay.
        """
        if showbool:
            for overlay_item in self.overlay_items:
                for segment in overlay_item:
                    segment.show()
        else:
            for overlay_item in self.overlay_items:
                for segment in overlay_item:
                    segment.hide()

    
    def update_vertex_diameters(self, zoom_level):
        """
        When zooming in/out, update the dimater of the polygon vertices to make them easier to grab.
        """
        for label_item in self.label_items:
            new_diameter = self.label_item_vertex_diameter * (self.zoom_factor ** (zoom_level + 1))
            label_item.setVertexDiameter(new_diameter)

        self.scene.update(self.scene.sceneRect())
        
        
    ##########################################################
    # PUBLIC SLOTS
    ##########################################################
    def labelItemSelected(self):
        """ NOT USED """
        print("ITEM SELECTED")
        for i in range(len(self.label_items)):
            if self.label_items[i].isSelected():
                print ("ITEM {} IS SELECTED.".format(i))
       
    def onOpenImage(self, raw_image):
        """ NOT USED """
        # Clear the previous image if there is one
        self.clearImage()
            
        # Set up the new image
        self.setImage(raw_image)

    def clearLabelItemSelection(self):
        """Clears the selection overlay item.
        """
        for it in self.label_items:
            it.setSelected(False)

    def setLabelItemSelected(self, index):
        """Sets the overlay item at index as selected
        """
        self.clearLabelItemSelection()
        self.label_items[index].setSelected(True)
    
    def onOpenSavedLabels(self, label_items):
        
        # Clear the previous items if there are any
        self.clearLabelItems()
        
        # Set up the new items
        self.initLabelItems(self, label_items)

    def setImageLevels(self, shadow: int, mid: int, highlight: int):
        if self.base_image_item is not None:
            self.base_image_item.update_image_window(new_shadow=shadow, 
                                                    new_mid=mid, 
                                                    new_highlight=highlight)

    def autoSetImageLevelsInBounds(self):
        shadow, mid, highlight = self.base_image_item.autoSetImageLevelsInBounds()
        return (shadow, mid, highlight)

    def resetImageLevels(self):
        self.base_image_item.resetImageLevels()
        
    def refinePoly(self):
        # make sure assist method is set
        self.setPolyAssistMethod(self.poly_assist_configs['method'])
        
        # Get active polygon id
        touseid = None
        for i in range(len(self.label_items)):
            if self.label_items[i].isSelected():
                touseid = i
                break
                
        if touseid is not None:    
            # taking viewport and mapping to scene coordinates, then get bound rectangle
            coordinates_in_scene_coord = self.mapToScene(self.viewport().geometry()).boundingRect()
            
            # Then, convert scene coordinates to base grid coordinates, which correspond to original image
            coordinates_in_baseGrid = self.base_grid.mapRectFromScene(coordinates_in_scene_coord)
            
            # Get image chip associated with baseGrid (full resolution) based on user's current viewport
            img_chip = self.base_image_item.get_image_chip(coordinates_in_baseGrid)
            
            # Scene coordinates of item to grid coordinates          
            vertices_in_scene_coord = self.label_items[touseid].getVertices()
            vertices_in_grid_coord: list[QPointF] = [self.base_grid.mapFromScene(pt[0],pt[1]) for pt in vertices_in_scene_coord]
            
            # Get top left point of chip in scene coordinates
            chip_top = int(coordinates_in_baseGrid.top())
            chip_left = int(coordinates_in_baseGrid.left())
            
            # calculated vertices of polygon in chip based on chip coordinate
            poly_vertices_in_chip = [(pt.x()-chip_left,pt.y()-chip_top) for pt in vertices_in_grid_coord]
            
            logging.info(self.poly_assist_configs['method'])
            
            # Not assuming algorithms no what QT objects are, let's just pass a list of the vertices.
            #input_pts=poly_vertices_in_chip.getVertices()
            newPolyVerts = poly_assistant.refine_polygon(img_chip,
                                                         poly_vertices_in_chip,
                                                         self.poly_assist_configs['options'])
            
            # Work backwards to SCENE coordinates
            # calculated vertices of polygon in chip based on chip coordinate
            new_poly_vertices_in_scene_coords = [self.base_grid.mapToScene(pt[0] + chip_left, pt[1] + chip_top) for pt in newPolyVerts]
            
            # Remove old polygon from list and memory
            # NOTE: in future, if we want to preserve the original polygon (in case the user doesn't like the new one),
            # we can just hang on to old_polygon
            old_polygon = self.removeItem(touseid)
            del old_polygon

            # Add new polygon object
            self.addPolygon(poly=QPolygonF(new_poly_vertices_in_scene_coords), index = touseid)
        
    def setPolyAssistMethod(self, method):
        self.poly_assist_configs['method'] = method
        #Instantiate assist method
        global poly_assistant 
        poly_assistant = utils.get_poly_assist(self.poly_assist_configs['method'])
        
    def setPolyAssistParamaters(self,options):
        self.poly_assist_configs['options'] = options

        
    ##########################################################
    # Reimplementations
    ##########################################################
    def mouseReleaseEvent(self, mouseEvent):
        """Reimplement mouseReleaseEvent to keep track of handle
        and overlay item movements.
        """
        selected_flag = False
        for i in range(len(self.label_items)):
            if self.label_items[i].isSelected():
                selected_flag = True
                if i != self.previous_item_selected:
                    self.previous_item_selected = i
                    self.label_item_selection_changed.emit(i)
                
                # If the handle was moved, add the move to the 
                # undo stack
                if self.label_items[i].handle_moved_flag:
                    cmd = commandMoveHandle(self.label_items[i],
                                            self.label_items[i].handle_selected,
                                            self.label_items[i].mouse_press_pos,
                                            self.label_items[i].mouse_move_pos)
                    self.command_added.emit(cmd)
                # If a handle was added, add the addition to the 
                # undo stack
                elif self.label_items[i].insert_handle_flag:
                    cmd = commandInsertHandle(self.label_items[i],
                                              self.label_items[i].mouse_press_pos)
                    self.command_added.emit(cmd)
                # If a handle was deleted, add the deletion to the
                # undo stack
                elif self.label_items[i].delete_handle_flag:
                    if (self.label_items[i].handle_selected is not None and
                        len(self.label_items[i].handles) > 3):
                        cmd = commandDeleteHandle(self.label_items[i],
                                                  self.label_items[i].handle_selected)
                        self.command_added.emit(cmd)

                # If the item was moved, add the movement to the undo stack
                elif self.label_items[i].item_moved_flag:
                    cmd = commandMoveItem(self.label_items[i],
                                          self.label_items[i].item_press_pos)
                    self.command_added.emit(cmd)
        
        if not selected_flag:
            if self.previous_item_selected is not None:
                self.previous_item_selected = None
                self.label_item_selection_changed.emit(-1)

        # Update image based on new window
        bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
        if self.base_image_item is not None:
            self.base_image_item.update_image_window(new_coordinates=bounds)
        
        super().mouseReleaseEvent(mouseEvent)
    
    def keyPressEvent(self, keyEvent):
        """Reimplement keyPressEvent to handle overlay item
        deletions.
        """
        if keyEvent.key() == Qt.Key_Delete:
            del_ind = -1
            for i in range(len(self.label_items)):
                if self.label_items[i].isSelected():
                    del_ind = i
                    break
            if del_ind != -1:
                self.delete_item_request.emit(del_ind)
        
        super().keyPressEvent(keyEvent)

        if keyEvent.key() == Qt.Key_Up or \
            keyEvent.key() == Qt.Key_Down or \
            keyEvent.key() == Qt.Key_Left or \
            keyEvent.key() == Qt.Key_Right:
            # Update image based on new window
            bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
            if self.base_image_item is not None:
                self.base_image_item.update_image_window(new_coordinates=bounds)
            
        
    ##########################################################
    # PRIVATE SLOTS
    ##########################################################
    def _onCommandAdded(self, cmd: QUndoCommand):
        self.command_added.emit(cmd)

    def _onSliderReleased(self):
        # Update image based on new window
        bounds = self.mapToScene(self.viewport().geometry()).boundingRect()
        self.base_image_item.update_image_window(new_coordinates=bounds)

class BaseImageGraphicsItem(QGraphicsItem):
    """Base class for the image graphics item.
    
    Signals
    -------
    error_signal -> str
    
    Attributes
    ----------
    image_file: str
        Path to H5 file. Composed of original image at ["original_image_key"], and image 
        pyramid in the ["pyramid"] group Images must be in shape [h, w] for single-channel or
        [h, w, c] for multi-channel.
    original_image_key: str
        Defined in the template file; the key to the original image in the h5 file.
    original_shadow: int
        Original shadow value of the image.
    original_mid: int
        Original mid value of the image.
    original_highlight: int
        Original highlight value of the image.
    current_shadow: int
        Current shadow value of the image.
    current_mid: int
        Current mid value of the image.
    current_highlight: int
        Current highlight value of the image.
    max_zoom: int
        Max zoom level of the image, used for the zooming logic.
    original_image_length: int
        Original length of the image.
    original_image_height: int
        Original height of the image.
    current_crop_list: dict[(int,int) -> numpy.array]
        Dictionary of tile indexes -> crops. Essentially, the tile cache. 
        Tiles are added and removed as the user navigates the image.
    current_coordinates: QRectF
        Coordinates representing the position of the viewport in the scene.
    current_zoom_level: int
        Current zoom level of the image. Initialized at the max zoom.
    current_crop: np.array
        Current crop of image, based on coordinates and zoom level.
    processing_tile_size: int
        Size (length and width) of the tiles used for processing/dynamic loading.
    display_tile_size: int
        Size (length and width) of the tiles used for display. Only necessary when 
        viewing large images without dynamic loading.
    """

    error_signal = pyqtSignal(str)
    
    def __init__(self, 
                 image_file: str,
                 original_image_key: str,
                 shadow: int,
                 mid: int,
                 highlight: int,
                 no_pyramid: bool = False,
                 parent = None):
        
        super(BaseImageGraphicsItem, self).__init__(parent)

        self.original_image_key = original_image_key

        # Maintain original values for resetting
        self.original_shadow = shadow
        self.original_mid = mid
        self.original_highlight = highlight

        # Initialize current image values
        self.current_shadow = self.original_shadow
        self.current_mid = self.original_mid
        self.current_highlight = self.original_highlight

        # Add image pointer as class member
        self.set_image_file(image_file)

        # Get image metadata
        with h5py.File(self.image_file, "r") as image_data:
            self.max_zoom = image_data.attrs["max_level"]
            self.original_image_length = image_data.get(self.original_image_key).shape[1]
            self.original_image_height = image_data.get(self.original_image_key).shape[0]

        # Initialize tile list
        self.current_crop_list = {}

        # Set current zoom level based on resolution
        self.current_zoom_level = self.get_max_zoom()

        # Set tile size if pyramid is being used. Otherwise, the entire image is one tile.
        if no_pyramid:
            max_dim = max(self.original_image_length, self.original_image_height)
            self.processing_tile_size = max_dim + (int(max_dim * 0.1))# add a buffer to be safe
        else:
            self.processing_tile_size = 512

        self.display_tile_size = 20000
    
    ##########################################################
    # PUBLIC
    ##########################################################
    def get_image_chip(self, coordinates: QRectF = None):
    
        with h5py.File(self.image_file, "r") as image_data:
            # TODO: Use this logic to get correct zoom level (pyramid level) for desired resolution of image chip
            """
            # Zoom < 0, use original image
            if new_zoom_level <= 0:
                pyramid_level = image_data[self.original_image_key]
            # Zoom > max, use max image
            elif new_zoom_level > self.get_max_zoom():
                # If zooming out, but only one zoom level exists, use original
                if self.get_max_zoom() == 0:
                    pyramid_level = image_data[self.original_image_key]
                else:
                    pyramid_level = image_data["pyramid"][str(self.get_max_zoom())]
            else:
                pyramid_level = image_data["pyramid"][str(new_zoom_level)]

            """
            # This is our unzoomed image
            pyramid_level = image_data[self.original_image_key]
              
            # 
            window_crop = pyramid_level[int(coordinates.top()) : int(coordinates.bottom()),
                                        int(coordinates.left()) : int(coordinates.right())]  
            
            return window_crop

    def set_image_file(self, image_file):
        """
        Set raw image, or the object representing the image on disc (not yet in memory)
        """
        self.image_file = image_file


    def update_image_window(self, 
                    new_coordinates: QRectF = None, 
                    new_zoom_level: Union[int, None] = None,
                    zoom_factor: Union[float, None] = 2.0,
                    new_shadow: Union[int, None] = None,
                    new_mid: Union[int, None] = None,
                    new_highlight: Union[int, None] = None,
                    autoset_levels: bool = False):
        """
        Rerender the image, depending on new coordinates of the viewport, 
        a new zoom level, and new image levels. This public function is the main function
        for any viewport movement and color adjustment.

        This item is scaled depending on the resolution being used at the
        current zoom level. If zooming into the lowest pyramid level (below 0),
        and zooming out of the highest level (above the max zoom), no scaling occurs 
        because resolution isn't changing.

        Parameters
        ----------
        new_coordinates: QRectF
            The new coordinates, in scene coordinates. Typically, the coordinates of the viewport.
        new_zoom_level: int | None
            The new zoom level.
        zoom_factor: float | None
            The zoom factor to use for scaling. 2 by default. 
            This should correspond with the zoom factor being used by the view widget.
        new_shadow: float
            Desired black point.
        new_mid: float
            Desired midtone point.
        new_highlight: float
            Desired white point.
        autosetLevels: bool
            Whether to autoset the color levels, based on the image contained within the new_coordinates.
        
        Returns
        -------
        None if the crop was not possible. Otherwise, updates image window.
        """
        # Check if new coordinates
        if new_coordinates:
            self.current_coordinates = new_coordinates
        else:
            new_coordinates = self.current_coordinates

        # Check if new zoom level
        if new_zoom_level != None:
            # Only scale if the zoom is within the range of the pyramid
            # Also, never scale if there is only one zoom level(0)
            if (new_zoom_level >= 0) and (new_zoom_level <= self.get_max_zoom()) and self.get_max_zoom() != 0:
                self.prepareGeometryChange()
                # Scale the item coordinate system to match the scene
                scale_factor = zoom_factor ** float(abs(new_zoom_level)) if new_zoom_level != 0 else 1
                self.setScale(scale_factor)
                
                # Throw away all of our cached tiles, because we need to load a different resolution
                self.current_crop_list = {}

            self.current_zoom_level = new_zoom_level
        else:
            new_zoom_level = self.current_zoom_level

        # Check if new zoom levels
        if not autoset_levels:
            if not new_shadow:
                new_shadow = self.current_shadow
            if not new_mid:
                new_mid = self.current_mid
            if not new_highlight:
                new_highlight = self.current_highlight

        crop = self._calculate_crop(new_coordinates=new_coordinates, 
                                   new_zoom_level=new_zoom_level,
                                   shadow=new_shadow,
                                   mid=new_mid,
                                   highlight=new_highlight,
                                   autoset_levels=autoset_levels)

        if crop is not None: 
            self.current_crop = crop

            display_tiles = self._make_display_tiles(crop)
            # Set the tiles to view
            self._set_pixmaps(display_tiles)

            self.update()
        else:
            # If the crop isn't possible (outside of image coordinates), quit.
            # Only really happens if you zoom into the margins.
            return


    def autoSetImageLevelsInBounds(self):
        """Sets the blacks, mids, highlights automatically based
        on what's in the current crop.
        
        Returns
        -------
        shadow: int
            The minimum inside rectf; used as the shadow value
        mid: int
            The midpoint; used as the midpoint value
        highlight: int
            The maximum inside rectf; used as the highlight value
        
        """
        self.update_image_window(autoset_levels=True)
        # The updated current values are the auto values set.
        return (self.current_shadow, self.current_mid, self.current_highlight)
        

    def resetImageLevels(self):
        """
        Reset image levels to original levels.
        """
        self.update_image_window(new_shadow=self.original_shadow, 
                                new_mid=self.original_mid, 
                                new_highlight=self.original_highlight)


    def get_max_zoom(self):
        return self.max_zoom

    def get_zoom_level(self):
        return self.current_zoom_level
    
    ##########################################################
    # PRIVATE
    ##########################################################

    def _calculate_crop(self, 
                       new_coordinates: QRectF, 
                       new_zoom_level: int,
                       shadow: int,
                       mid: int,
                       highlight: int,
                       autoset_levels: bool):
        """
        Given coordinates, the zoom level, and desired image levels, grab the respective
        crop of the image, composed of tiles, and pull into memory. Image levels are then computed across
        all tiles together.

        Tiles are persistent. New tiles are added only when the coordinates would contain tiles not yet loaded,
        and old tiles are removed when outside of the coordinates. Image levels of all tiles are recalculated when
        new image levels are given

        Parameters
        ----------
        new_coordinates: QRectF
            The new coordinates, in scene coordinates. Typically, the coordinates of the viewport.
        new_zoom_level: int | None
            The new zoom level.
        shadow: float
            Desired black point.
        mid: float
            Desired midtone point.
        highlight: float
            Desired white point.
        autosetLevels: bool
            Whether to autoset the color levels, based on the image contained within the new_coordinates.
        
        Returns
        -------
        crop: np.array
            Computer crop, consisting of all loaded tiles stitched together, with image levels adjusted.
        """
        with h5py.File(self.image_file, "r") as image_data:
            # Get correct pyramid level
            # Zoom < 0, use original image
            if new_zoom_level <= 0:
                pyramid_level = image_data[self.original_image_key]
            # Zoom > max, use max image
            elif new_zoom_level > self.get_max_zoom():
                # If zooming out, but only one zoom level exists, use original
                if self.get_max_zoom() == 0:
                    pyramid_level = image_data[self.original_image_key]
                else:
                    pyramid_level = image_data["pyramid"][str(self.get_max_zoom())]
            else:
                pyramid_level = image_data["pyramid"][str(new_zoom_level)]

            # Determine the scene coordinates of the tiles to load in.
            x_tile_min_scene = max(int(new_coordinates.left()), 0) // self.processing_tile_size
            x_tile_max_scene = int(new_coordinates.right()) // self.processing_tile_size
            y_tile_min_scene = max(int(new_coordinates.top()), 0) // self.processing_tile_size
            y_tile_max_scene = int(new_coordinates.bottom()) // self.processing_tile_size

            # Translate the scene tile coordinates into item coordinates
            item_coordinates = self.mapRectFromScene(x_tile_min_scene * self.processing_tile_size, 
                                                     y_tile_min_scene * self.processing_tile_size,
                                                     (((x_tile_max_scene-x_tile_min_scene)+1) * self.processing_tile_size),
                                                     (((y_tile_max_scene-y_tile_min_scene)+1) * self.processing_tile_size))

            # Get the correct bounds of the edges of the tiles
            x_min_item = max(int(item_coordinates.left()), 0)
            x_max_item = min(int(item_coordinates.right()), pyramid_level.shape[1])
            y_min_item = max(int(item_coordinates.top()), 0)
            y_max_item = min(int(item_coordinates.bottom()), pyramid_level.shape[0])

            # Used to know where to paint in paint()
            self.paint_x_coord = x_min_item
            self.paint_y_coord = y_min_item
            
            # Check if the loaded tiles have changed. We need to assert that the exact same tiles are needed.
            new_tiles = False
            tiles_needed = []
            for x in range(x_tile_min_scene, x_tile_max_scene+1):
                for y in range(y_tile_min_scene, y_tile_max_scene+1):
                    tiles_needed.append((x,y))
                    if (x,y) not in self.current_crop_list:
                        new_tiles=True
            # If the current crop has tiles we no longer need, we will have to remove them
            if len(self.current_crop_list.keys()) != len(tiles_needed):
                new_tiles = True
                
            # Check if there are new image levels
            new_image_levels = False
            if (shadow != self.current_shadow) or \
                (mid != self.current_mid) or \
                (highlight != self.current_highlight):
                new_image_levels = True
            
            # If the viewport does not contain the image, return None, don't display anything
            if x_min_item >= x_max_item or y_min_item >= y_max_item:
                return None
            elif new_tiles or new_image_levels or autoset_levels:
                new_crop = self._collect_processing_tiles(pyramid_level, 
                                               x_tile_min_scene=x_tile_min_scene,
                                               x_tile_max_scene=x_tile_max_scene,
                                               y_tile_min_scene=y_tile_min_scene,
                                               y_tile_max_scene=y_tile_max_scene,)

                if autoset_levels:
                    # Grab crop of only the viewport
                    window_coordinates = self.mapRectFromScene(new_coordinates)
                    window_crop = pyramid_level[int(window_coordinates.top()) : int(window_coordinates.bottom()),
                                                int(window_coordinates.left()) : int(window_coordinates.right())]
                    # Calculate image levels based on viewport crop.
                    shadow, mid, highlight = self._calculate_auto_image_levels(window_crop)

                # Apply current image values to current crop
                new_crop = self._compute_new_image_levels(new_crop,
                                                    shadow, 
                                                    mid, 
                                                    highlight)
            else:
                new_crop = self.current_crop

            return new_crop
            
            
    def _collect_processing_tiles(self, 
                       pyramid_level: h5py.File, 
                       x_tile_min_scene: int, 
                       x_tile_max_scene: int, 
                       y_tile_min_scene: int, 
                       y_tile_max_scene: int):
        """
        Collect all necessary tiles into memory, stitching them all into a single
        numpy array.

        This function is distinct from _collect_processing_tiles().
        _collect_processing_tiles() is used for dynamically loading parts of the image
        into memory. _make_display_tiles() is for displaying very large image crops, 
        because QT has a size limit on the pixmaps.
        """
        # For each tile, load it in if it is not yet loaded
        # Remove all tiles from current crop that don't match
        new_crop_list = {}

        x_arrays = []
        for x in range(x_tile_min_scene, x_tile_max_scene+1):
            y_arrays = []
            for y in range(y_tile_min_scene, y_tile_max_scene+1):
                # If the tile is currently loaded, pop it from the current crop list and append it to the new one
                if (x,y) in self.current_crop_list:
                    crop = self.current_crop_list.pop((x,y))
                else:
                    # If the tile is not currently loaded, load it in
                    # Calculate crop for tile
                    crop_coordinates = self.mapRectFromScene(self.processing_tile_size*x, 
                                                            self.processing_tile_size*y,
                                                            self.processing_tile_size,
                                                            self.processing_tile_size)

                    # If the tile starts after the image, but the tile is still in the viewport, skip loading anything
                    if crop_coordinates.top() > pyramid_level.shape[0] or crop_coordinates.left() > pyramid_level.shape[1]:
                        continue

                    x_limit = min(crop_coordinates.right(), pyramid_level.shape[1])
                    y_limit = min(crop_coordinates.bottom(), pyramid_level.shape[0])
                    
                    # Pull the crop into memory
                    crop = pyramid_level[int(crop_coordinates.top()) : int(y_limit), 
                                        int(crop_coordinates.left()) : int(x_limit)]

                y_arrays.append(crop)
                new_crop_list[(x, y)] = crop
            if len(y_arrays) != 0:
                x_arrays.append(np.concatenate(y_arrays, axis=0))
        # Stitch together all the tiles.
        new_crop = np.concatenate(x_arrays, axis=1)

        self.current_crop_list = new_crop_list

        return new_crop

    
    def _compute_new_image_levels(self,
                                image: np.array,
                                shadow: int,
                                mid: int,
                                highlight: int):
        """
        Computes image levels on the given crop, image, by gamma correction, 
        rescaling to 8 bit, and adding necessary padding
        """
        if shadow:
            self.current_shadow = shadow
        if mid:
            self.current_mid = mid
        if highlight:
            self.current_highlight = highlight

        if image is None:
            image = self.current_crop.astype(float)
        else:
            image = image.astype(float)
        
        image_max = float(image.max())
        image_min = float(image.min())

        # If all one color, it doesn't make sense to adjust because there is no contrast
        if image_max - image_min != 0:
            # Rescale the image, and shadow, midtones, and highlights
            # values to be between 0 and 1
            image = (image-image_min)/(image_max-image_min)
            shadow = float(shadow-image_min)/float(image_max-image_min)
            mid = float(mid-image_min)/float(image_max-image_min)
            highlight = float(highlight-image_min)/float(image_max-image_min)
            
            image = self._gamma_correct(image, shadow, mid, highlight)

            if len(image.shape) > 3 or len(image.shape) < 2:
                sys.exit("Image not shaped properly.")
            
            image = self._rescale_to_8_bit(image)

            if len(image.shape) == 2:
                pad = self._get_pad(image)
                image = np.concatenate((image, pad), axis=1)

        return image


    def _gamma_correct(self,
                      image: np.ndarray,
                      shadow: float,
                      mid: float,
                      highlight: float):
        """Use shadow (black point), midtone, and highlight
        (white point) values to compute and apply gamma 
        correction to given image.
        
        Parameters
        ----------
        image: numpy.ndarray
            Must be a numpy.float-valued array with values 
            between 0 and 1.
        shadow: float
            Desired black point.  Must be between 0 and 1.
        mid: float
            Desired midtone point.  Must be between 0 and 1.
        highlight: float
            Desired white point.  Must be between 0 and 1.
        
        Returns
        -------
        numpy.ndarray
            The image with gamma correction applied.  Will be 
            type float with values between 0 and 1.
        """
        
        image_mid = 0.5
        gamma = 1
        
        # Compute gamma
        if mid < image_mid:
            mid_normal = mid*2
            gamma = 1 + (9*(1 - mid_normal))
            if gamma > 9.99:
                gamma = 9.99
        
        elif mid > image_mid:
            mid_normal = mid*2 - 1
            gamma = 1 - mid_normal
            if gamma < 0.01:
                gamma = 0.01
        
        gamma_correct = 1/gamma
        
        # Apply shadows and highlights
        image = (image - shadow)/(highlight - shadow)
        image [image < 0] = 0
        image [image > 1] = 1
        
        # Apply gamma
        if mid != image_mid:
            image = image**gamma_correct
        
        return image
    

    def _get_pad(self, image):
        """Get the zero-padding array to be concatenated.
        Greyscale images must be 32-bit aligned before converting to
        8-bit.
        """
        if len(image.shape) == 2:
            rem = image.shape[1]%4
            if rem > 0:
                pad_amt = 4-rem
            else:
                pad_amt = 0
            
            pad = np.zeros((image.shape[0], pad_amt), dtype=image.dtype)
        
        else:
            # @TODO: Shouldn't hit this ever because we check the
            # image shape prior to calling getPad
            sys.exit("Image not shaped properly.")
        
        return pad
    

    def _rescale_to_8_bit(self, image, mx=None, mn=None):
        """Converts the image to np.uint8 type and linearly
        rescales such that the entire 0-255 space is used, i.e. 
        the max value in the image is mapped to 255 and the min
        value is mapped to 0.
        """
        if mx is None:
            mx = image.max()
        
        if mn is None:
            mn = image.min()

        if mx == mn:
            # If the min and max of the image are the same, it's just one color, 
            # and we don't need to rescale
            # return image.astype(np.uint8)
            mx = 255
            mn = 0
            diff = mx-mn
        else:
            diff = mx-mn
        
        # Compute slope and offset
        m = 255.0/(diff)
        b = 255.0*mn/(diff)*(-1.0)
        
        # Apply slope and offset
        out_image = (image*m + b)
        out_image[out_image > 255] = 255
        out_image[out_image < 0] = 0
        out_image = out_image.astype(np.uint8)
        
        return out_image
    
    
    def _calculate_auto_image_levels(self,
                                     image: np.array):
        """
        Calculate the blacks, mids, and highlights automatically based
        on the given crop.
        
        Returns
        -------
        shadow: int
            The minimum inside rectf; used as the shadow value
        mid: int
            The midpoint; used as the midpoint value
        highlight: int
            The maximum inside rectf; used as the highlight value
        
        """
        shadow = image.min()
        highlight = image.max()
        mid = int((highlight-shadow)/2) + shadow

        if mid < shadow:
            mid = shadow
        elif mid > highlight:
            mid = highlight

        return (shadow, mid, highlight)
    
    def _make_display_tiles(self, image):
        """
        Breaks a processed image up into tiles.

        This function is only really used if the image pyramid is not being used,
        and the image being displayed is greater than 20000 pixels.
        
        If the inputted param:`image` is larger than param:`tilesize`
        in width and/or height, then `image` is broken into tiles.

        This function is distinct from _collect_processing_tiles().
        _collect_processing_tiles() is used for dynamically loading parts of the image
        into memory. _make_display_tiles() is for displaying very large image crops, 
        because QT has a size limit on the pixmaps.
        """
        
        tiles = []
        # Prepare to make tiles
        if image.shape[0] % self.display_tile_size == 0:
            self.num_tiles_h = int(image.shape[0]/self.display_tile_size)
        else:
            self.num_tiles_h = int(image.shape[0]/self.display_tile_size)+1
            
        if image.shape[1] % self.display_tile_size == 0:
            self.num_tiles_w = int(image.shape[1]/self.display_tile_size)
        else:
            self.num_tiles_w = int(image.shape[1]/self.display_tile_size)+1
        
        # Make all tiles except last row
        for j in range(self.num_tiles_h-1):
            new_row = []
            for i in range(self.num_tiles_w-1):
                new_row.append(image[self.display_tile_size*j : self.display_tile_size*(j+1),
                                     self.display_tile_size*i : self.display_tile_size*(i+1)])
            new_row.append(image[self.display_tile_size*j : self.display_tile_size*(j+1),
                                 self.display_tile_size*(self.num_tiles_w-1) :])
            tiles.append(new_row)
        
        # Make last row of tiles
        new_row = []
        for i in range(self.num_tiles_w-1):
            new_row.append(image[self.display_tile_size*(self.num_tiles_h-1) :,
                                 self.display_tile_size*i : self.display_tile_size*(i+1)])
        
        # Make bottom corner tile
        new_row.append(image[self.display_tile_size*(self.num_tiles_h-1) :,
                             self.display_tile_size*(self.num_tiles_w-1) :])
        tiles.append(new_row)
        
        return tiles

    def _set_pixmaps(self, tiles):
        """Convert the image to a pixmap for display.
        """
        self.pixmaps = []
        
        # Set up color image
        if len(tiles[0][0].shape) == 3:
            for j in range(self.num_tiles_h):
                new_row = []
                for i in range(self.num_tiles_w):
                    new_row.append(QPixmap.fromImage(QImage(tiles[j][i].tobytes(),
                                                            tiles[j][i].shape[1],
                                                            tiles[j][i].shape[0],
                                                            tiles[j][i].shape[1]*3,
                                                            QImage.Format_RGB888)))
                self.pixmaps.append(new_row)
        
        # Set up greyscale image
        else:
            for j in range(self.num_tiles_h):
                new_row = []
                for i in range(self.num_tiles_w):
                    new_row.append(QPixmap.fromImage(QImage(tiles[j][i].tobytes(),
                                                            tiles[j][i].shape[1],
                                                            tiles[j][i].shape[0],
                                                            QImage.Format_Grayscale8)))
                self.pixmaps.append(new_row)

    
    ##########################################################
    # REIMPLEMENTATIONS
    ##########################################################    
    def boundingRect(self):
        """Return the bounding rect
        
        Reimplementation of QGraphicsItem.boundingRect()
        """
        top_left = QPointF(0,0)
        bottom_right = QPointF(self.original_image_length,
                               self.original_image_height)
        return QRectF(top_left, bottom_right)
    

    def paint(self, painter, option, widget=None):
        """Paint the item
        
        Reimplementation of QGraphicsItem.paint(...)
        """
        x_start = max(self.paint_x_coord, 0)
        y_start = max(self.paint_y_coord, 0)

        for j in range(self.num_tiles_h):
            for i in range(self.num_tiles_w):
                painter.drawPixmap(x_start + (i*self.display_tile_size), 
                                   y_start + (j*self.display_tile_size), 
                                   self.pixmaps[j][i])
                
    
class BaseGrid(QGraphicsItem):
    """
    Represents base grid to draw all polygon items on.
    """
    def __init__(self, 
                 width,
                 height,
                 parent=None):
        
        super(BaseGrid, self).__init__(parent)

        self.width = width
        self.height = height
    
    def boundingRect(self):
        """Return the bounding rect
        """
        top_left = QPointF(0,0)
        bottom_right = QPointF(self.width, self.height)
        return QRectF(top_left, bottom_right)

    def paint(self, painter, option, widget=None):
        pass # Don't need to paint anything, just need to have this defined

############################################################
# QUndoCommand Subclasses
############################################################

# NOTES
# The QUndoCommands are at this level (i.e. controlled by the
# image overlay widget) because the overlay items, which
# inherit QGraphicsItem, have no QObject support and
# therefore no signal/slot support...
# Thus the image overlay widget must watch its own mouse
# release events and use those events to check that any
# change occurred in the corresponding overlay item.
# 
# If change does occur in the overlay item, a QUndoCommand
# is created for that change.
class commandMoveHandle(QUndoCommand):
    """Class to control undo/redo of moving
    a polygon vertex (handle).
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.  Since the overlay item itself
    handles moving the vertex the first time, we avoid calling 
    the redo() function when this command is first pushed onto
    the stack using the 'undone_flag'.
    """
    def __init__(self, polygon_label_item, handle_ind, original_pos, new_pos, text="Move vertex", parent=None):
        super(commandMoveHandle, self).__init__(text, parent)
        self.label_item = polygon_label_item
        self.handle_ind = handle_ind
        self.original_pos = original_pos
        self.new_pos = new_pos
        self.undone_flag = False
        
    
    def redo(self):
        if self.undone_flag:
            self.label_item.moveHandle(self.handle_ind, self.new_pos)
    
    def undo(self):
        self.label_item.moveHandle(self.handle_ind, self.original_pos)
        self.undone_flag = True



class commandInsertHandle(QUndoCommand):
    """Class to handle undo/redo of adding
    a polygon vertex (handle).
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.  Since the overlay item itself
    handles inserting the vertex the first time, we avoid calling
    the redo() function when this command is first pushed onto
    the stack using the 'undone_flag'.
    """
    def __init__(self, polygon_label_item, insert_pos, text="Insert vertex", parent=None):
        super(commandInsertHandle, self).__init__(text, parent)
        self.label_item = polygon_label_item
        self.insert_pos = insert_pos
        self.undone_flag = False
        self.handle_ind, _ = self.label_item.getInsertHandleIndex(self.insert_pos)
    
    def redo(self):
        if self.undone_flag:
            self.label_item.insertHandle(self.handle_ind, self.insert_pos)
    
    def undo(self):
        self.label_item.deleteHandle(self.handle_ind)
        self.undone_flag = True



class commandDeleteHandle(QUndoCommand):
    """Class to handle undo/redo of deleting
    a polygon vertex (handle).
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.  Since the overlay item itself
    handles deleting the vertex the first time, we avoid calling
    the redo() function when this command is first pushed onto
    the stack using the 'undone_flag'.
    """
    def __init__(self, polygon_label_item, handle_ind, text="Delete vertex", parent=None):
        super(commandDeleteHandle, self).__init__(text, parent)
        self.label_item = polygon_label_item
        self.handle_ind = handle_ind
        self.undone_flag = False
        
        pos = self.label_item.getVertices()[self.handle_ind]
        self.handle_pos = QPointF(pos[0], pos[1])
    
    def redo(self):
        if self.undone_flag:
            self.label_item.deleteHandle(self.handle_ind)
    
    def undo(self):
        self.label_item.insertHandle(self.handle_ind, self.handle_pos)
        self.undone_flag = True


class commandMoveItem(QUndoCommand):
    """Class to handle undo/redo of moving an item.
    """
    def __init__(self, label_item, original_pos, text="Move item", parent=None):
        super(commandMoveItem, self).__init__(text, parent)
        self.label_item = label_item
        self.original_pos = original_pos
        self.new_pos = label_item.pos()
        self.undone_flag = False

        # Get current position
        #self.item_pos = self.label_item.pos()

    def redo(self):
        if self.undone_flag:
            # Set the item's position
            self.label_item.setPos(self.new_pos)

    def undo(self):
        # Update position to the original
        self.label_item.setPos(self.original_pos)
        self.undone_flag = True
        
