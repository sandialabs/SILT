#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Class definition for InteractivePolygon, which is the
# 'polygon' type of overlay item.
#################################################################

from PyQt5.QtWidgets import (QGraphicsItem, QGraphicsPolygonItem)
from PyQt5.QtGui import (QPainter, QPen, QColor, QPolygonF, 
                         QBrush, QPainterPath)
from PyQt5.QtCore import (Qt, QPointF, QRectF)
from shapely.geometry import Polygon as ShapelyPolygon
import numpy as np
import uuid

"""
NOTE:
Every overlay item class must have the following parameters:
    item_type: str
        This is the item type descriptor; each image can
        contain multiple overlay item types.
    uuid: str
        This is the unique identifier for this particular overlay 
        item in the image.
    item_moved_flag: bool
        This is the flag that alerts the view_widget of a label
        item being shifted by the user.
    item_press_pos: QPointF
        This is the variable which stores the original location of
        an item before it is shifted by the user.
    handle_moved_flag: bool
        This is the flag that alerts the view_widget of a label 
        item vertex being shifted by the user.

Every overlay item class must have the following public functions:
    getVertices()
    getCoveredPixels()
    setLineWidth(int or float)
    setLineColor(triplet or quadruplet list of int)
    setVertexDiameter(int or float)
    setVertexColor(triplet or quadruplet list of int)
    setUUID(str)
    getUUID()
    getBoundingRect()

Note
    The getVertices() function must output closed polygons if 
    applicable; that is, the last point in the list of points 
    must equal the first.
"""


class InteractivePolygon(QGraphicsPolygonItem):
    
    item_type = 'polygon'
    handle_size = +3.0
    grip_size = handle_size+2.0
    line_width = 1.0
    line_color = [255, 0, 255, 150]
    vertex_color = [0, 0, 255, 255]
    
    insert_handle_delta = 5
    
    handle_cursor = Qt.CrossCursor
    default_cursor = Qt.OpenHandCursor
    insert_handle_cursor = Qt.ArrowCursor
    
    insert_handle_modifier = Qt.ShiftModifier
    delete_handle_modifier = Qt.ControlModifier
    
    handle_moved_flag = False
    
    
    def __init__(self, *args):
        super(InteractivePolygon, self).__init__(*args)
        self.handles = []
        self.handle_grips = []
        self.handle_selected = None
        self.mouse_press_pos = None
        self.mouse_press_poly = None
        self.mouse_move_pos = None
        self.item_press_pos = None
        self.item_moved_flag = False
        self.insert_handle_flag = False
        self.delete_handle_flag = False
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        
        # Generate a UUID
        self.uuid = str(uuid.uuid4())
        
        # Check if the polygon is closed
        # The interactivity works only with non-closed polygons,
        # so if the polygon is closed, then remove the last
        # vertex to "open" it
        poly = self.polygon()
        if poly.isClosed():
            poly.remove(poly.count()-1)
            self.setPolygon(poly)

        # Initialize the handles
        num_handles = self.polygon().count()
        for i in range(num_handles):
            cent = self.polygon().value(i)
            self.handles.append(QRectF(cent.x()-self.handle_size/2, 
                                       cent.y()-self.handle_size/2,
                                       self.handle_size,
                                       self.handle_size))
            self.handle_grips.append(QRectF(cent.x()-self.grip_size/2, 
                                            cent.y()-self.grip_size/2,
                                            self.grip_size,
                                            self.grip_size))
        self.update()
        
    def handleAt(self, point):
        for i in range(len(self.handle_grips)):
            if self.handle_grips[i].contains(point):
                return i
        return None
        
    def hoverMoveEvent(self, moveEvent):
        if self.isSelected() == True:
            if (moveEvent.modifiers() == self.insert_handle_modifier or
                moveEvent.modifiers() == self.delete_handle_modifier):
                cursor = self.insert_handle_cursor
            
            #if not self.insert_handle_flag:
            else:
                handle = self.handleAt(moveEvent.pos())
                cursor = self.default_cursor if handle is None else self.handle_cursor
            self.setCursor(cursor)
        else:
            cursor = self.default_cursor
            self.setCursor(cursor)
            
        super().hoverMoveEvent(moveEvent)
        
    def hoverLeaveEvent(self, moveEvent):
        #if not self.insert_handle_flag:
        #    super().hoverLeaveEvent(moveEvent)
        super().hoverLeaveEvent(moveEvent)
        
    def mousePressEvent(self, mouseEvent):
        """Reimplement mousePressEvent to allow addition, deletion,
        and movement of vertex handles.
        """
        #if mouseEvent.modifiers() == Qt.NoModifier:
        #    print ("Modifiers: No modifiers.")

        self.item_press_pos = self.pos()
        
        if self.isSelected():
            if mouseEvent.modifiers() == self.insert_handle_modifier:
                self.insert_handle_flag = True
                self.mouse_press_pos = mouseEvent.pos()
                self.mouse_press_poly = self.polygon()
                #print ("Modifiers: insert handle modifier.")
            elif mouseEvent.modifiers() == self.delete_handle_modifier:
                self.delete_handle_flag = True
                self.handle_selected = self.handleAt(mouseEvent.pos())
                if self.handle_selected is not None:
                    self.mouse_press_pos = mouseEvent.pos()
                    self.mouse_press_poly = self.polygon()
                #print ("Modifiers: delete handle modifier.")
            
            else:
                self.handle_selected = self.handleAt(mouseEvent.pos())
                if self.handle_selected is not None:
                    #self.mouse_press_pos = mouseEvent.pos()
                    self.mouse_press_pos = \
                        self.mapToScene(self.handles[self.handle_selected].center())
                    self.mouse_press_poly = self.polygon()
                    # For debug:
                    #print ("You pressed handle {} at location {}".format(self.handle_selected, self.mapToScene(mouseEvent.pos())))
                    
        else:
            super().mousePressEvent(mouseEvent)
        
    def mouseMoveEvent(self, mouseEvent):
        """Reimplement mouseMoveEvent to allow movement of vertex handles
        """
        # If there's a handle selected, replace that handle with a handle at the
        # new mouse position and update the polygon
        if self.handle_selected is not None:
            p = mouseEvent.pos()
            self.mouse_press_poly.replace(self.handle_selected, p)
            self.setPolygon(self.mouse_press_poly)
            self.handles[self.handle_selected] = QRectF(p.x()-self.handle_size/2,
                                                        p.y()-self.handle_size/2,
                                                        self.handle_size,
                                                        self.handle_size)
            self.handle_grips[self.handle_selected] = QRectF(p.x()-self.grip_size/2,
                                                             p.y()-self.grip_size/2,
                                                             self.grip_size,
                                                             self.grip_size)
            self.handle_moved_flag = True
            self.mouse_move_pos = p
            self.update()
            
        else:
            if self.isSelected():
                self.item_moved_flag = True
            super().mouseMoveEvent(mouseEvent)
        
    def mouseReleaseEvent(self, mouseEvent):
        """Reimplement mouseReleaseEvent to allow addition, deletion,
        and movement of vertex handles.
        """
        if self.insert_handle_flag:
            ind, qpt = self.getInsertHandleIndex(self.mouse_press_pos)
            # For debug:
            #print ("Inserting handle at index {}".format(ind))
            if ind is not None:
                self.insertHandle(ind, qpt)
                
            self.insert_handle_flag = False
        
        elif self.delete_handle_flag:
            if self.handle_selected is not None and len(self.handles) > 3:
                self.deleteHandle(self.handle_selected)
            
            self.delete_handle_flag = False
        
        else:
            if self.item_moved_flag:
                self.item_moved_flag = False
            super().mouseReleaseEvent(mouseEvent)
        
        self.handle_selected = None
        self.handle_moved_flag = False
        self.mouse_press_pos = None
        self.mouse_press_poly = None
        self.mouse_move_pos = None
        self.item_press_pos = None
    
    """
    def keyPressEvent(self, keyEvent):
        if not (keyEvent.isAutoRepeat()):
            if keyEvent.key() == Qt.Key_I:
                self.insert_handle_flag = True
                self.setCursor(Qt.ArrowCursor)
            elif keyEvent.key() == Qt.Key_D:
                self.delete_handle_flag = True
                self.setCursor(Qt.ArrowCursor)
        super().keyPressEvent(keyEvent)
        
    def keyReleaseEvent(self, keyEvent):
        if not (keyEvent.isAutoRepeat()):
            if keyEvent.key() == Qt.Key_I:
                self.insert_handle_flag = False
                self.setCursor(self.default_cursor)
            elif keyEvent.key() == Qt.Key_D:
                self.delete_handle_flag = False
                self.setCursor(self.default_cursor)
    """
    
    
    def deleteHandle(self, handle_ind):
        """Delete the handle at handle_ind.
        """
        poly = self.polygon()
        poly.remove(handle_ind)
        self.setPolygon(poly)
        del(self.handles[handle_ind])
        del(self.handle_grips[handle_ind])
        self.update()
    
    
    def moveHandle(self, handle_ind, pos):
        """Move the handle at handle_ind to 
        position pos.
        
        Parameters
        ----------
        handle_ind: int
        pos: QPoint
        """
        poly = self.polygon()
        poly.replace(handle_ind, pos)
        self.setPolygon(poly)
        self.handles[handle_ind] = QRectF(pos.x()-self.handle_size/2,
                                          pos.y()-self.handle_size/2,
                                          self.handle_size,
                                          self.handle_size)
        self.handle_grips[handle_ind] = QRectF(pos.x()-self.grip_size/2,
                                               pos.y()-self.grip_size/2,
                                               self.grip_size,
                                               self.grip_size)
        self.update()
    
    
    def insertHandle(self, handle_ind, pos):
        """Insert a handle at the given handle_ind
        and position pos.
        
        Parameters
        ----------
        handle_ind: int
        pos: QPoint
        """
        poly = self.polygon()
        poly.insert(handle_ind, pos)
        self.setPolygon(poly)
        self.handles.insert(handle_ind, QRectF(pos.x()-self.handle_size/2,
                                               pos.y()-self.handle_size/2,
                                               self.handle_size,
                                               self.handle_size))
        self.handle_grips.insert(handle_ind, QRectF(pos.x()-self.grip_size/2,
                                                    pos.y()-self.grip_size/2,
                                                    self.grip_size,
                                                    self.grip_size))
        self.update()
    
    
    def getInsertHandleIndex(self, pos):
        # For debug:
        #print (self.handles)
        cents = [rect.center() for rect in self.handles]
        candidates = []
        for i in range(len(cents)-1):
            v = cents[i]
            w = cents[i+1]
            t = QPointF.dotProduct((w - v), (pos-v))/QPointF.dotProduct((w - v), (w - v))
            if t >= 0 and t <= 1:
                r = t*(w-v) + v
                d = np.sqrt(QPointF.dotProduct((r-pos), (r-pos)))
                if d <= self.insert_handle_delta:
                    candidates.append([d, i+1, pos])
        
        v = cents[-1]
        w = cents[0]
        t = QPointF.dotProduct((w - v), (pos-v))/QPointF.dotProduct((w - v), (w - v))
        if t >= 0 and t <= 1:
            r = t*(w-v) + v
            d = np.sqrt(QPointF.dotProduct((r-pos), (r-pos)))
            if d <= self.insert_handle_delta:
                candidates.append([d, 0, pos])
        
        if len(candidates) == 0:
            return (None, None)
        
        dist = [cand[0] for cand in candidates]
        candidate = dist.index(min(dist))
        return (candidates[candidate][1], candidates[candidate][2])
    
    
    def getVertices(self):
        """Get all the vertex centers.
        """
        
        # Get the vertices
        #verts = [(self.mapToScene(rect.center()).x(),
        #          self.mapToScene(rect.center()).y()) for rect in self.handles]

        # Make sure the last vertex equals the first to complete the polygon
        #if verts[-1] != verts[0]:
        #    verts.append(verts[0])

        poly = self.mapToScene(self.polygon())
        pts = [poly.value(i) for i in range(poly.count())]
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        verts = [(pt.x(), pt.y()) for pt in pts]
            
        return verts
    
    
    def getCoveredPixels(self):
        """Get the list of pixel coordinates that are covered by the polygon.
        """
        poly = self.mapToScene(self.polygon())
        rect = self.polygon().boundingRect()
        covered_px = []
        for y in range(int(self.mapToScene(rect.topLeft()).y()),
                       int(self.mapToScene(rect.bottomLeft()).y()) + 1):
            for x in range(int(self.mapToScene(rect.topLeft()).x()),
                           int(self.mapToScene(rect.topRight()).x()) + 1):
                if poly.containsPoint(QPointF(x, y), Qt.WindingFill):
                    covered_px.append((x, y))
        return covered_px
    
    
    def getUUID(self):
        """Get the uuid of the polygon.
        """
        return(self.uuid)
    
    
    def setUUID(self, uuid):
        """Set the uuid of the polygon.
        """
        if uuid is None:
            return
        
        self.uuid = uuid
    
    
    def setLineWidth(self, line_width):
        """Sets the width of the polygon lines.
        """
        self.line_width = line_width
    
    
    def setVertexDiameter(self, diameter):
        """Sets the diameter of the polygon vertices.
        """
        self.handle_size = diameter
        self.grip_size = diameter+2
        self.insert_handle_delta = self.grip_size
        
        for handle in self.handles:
            ht = handle.height()
            wd = handle.width()
            handle.setHeight(self.handle_size)
            handle.setWidth(self.handle_size)
            dx = (wd-self.handle_size)/2.0
            dy = (ht-self.handle_size)/2.0
            handle.translate(dx, dy)
        
        for grip in self.handle_grips:
            ht = grip.height()
            wd = grip.width()
            grip.setHeight(self.grip_size)
            grip.setWidth(self.grip_size)
            dx = (wd-self.grip_size)/2.0
            dy = (ht-self.grip_size)/2.0
            grip.translate(dx, dy)
        
    
    def setLineColor(self, rgba_list):
        """Sets the color of the polygon lines.
        """
        self.line_color = rgba_list
    
    
    def setVertexColor(self, rgba_list):
        """Sets the color of the polygon vertices.
        """
        self.vertex_color = rgba_list
    
    
    def bufferPolygon(self, polygon, buffer_size: int):
        """Set up the valid interaction buffer around the polygon
        """
        tmp = [polygon.value(i) for i in range(polygon.count())]
        vertices = [(t.x(), t.y()) for t in tmp]
        vertices.append(vertices[0])
        spoly = ShapelyPolygon(vertices)
        spoly_buff = spoly.buffer(buffer_size)
        
        buff_x, buff_y = spoly_buff.exterior.xy
        qpoly_pts = [QPointF(pt[0], pt[1]) for pt in zip(buff_x, buff_y)]
        qpoly_buff = QPolygonF(qpoly_pts)
        
        return qpoly_buff[:-1]


    def getBoundingRect(self):
        """Set up to return the bounding rect corners as a list
        """
        rect = self.polygon().boundingRect()
        corners = [(int(self.mapToScene(rect.topLeft()).x()),
                    int(self.mapToScene(rect.topLeft()).y())),
                   (int(np.ceil(self.mapToScene(rect.topRight()).x())),
                    int(self.mapToScene(rect.topRight()).y())),
                   (int(np.ceil(self.mapToScene(rect.bottomRight()).x())),
                    int(np.ceil(self.mapToScene(rect.bottomRight()).y()))),
                   (int(self.mapToScene(rect.bottomLeft()).x()),
                    int(np.ceil(self.mapToScene(rect.bottomLeft()).y())))]
        return corners

    
    def boundingRect(self):
        """Reimplement boundingRect() to define the bounding box
        for painting the polygon on the scene.
        """
        rect = self.polygon().boundingRect().adjusted(-self.grip_size/2, -self.grip_size/2, 
                                                      +self.grip_size/2, +self.grip_size/2)
        return rect
    
    
    def shape(self):
        """Reimplement shape to give the polygon a buffer for
        grabbing/moving it and adding vertices.
        """
        path = QPainterPath()
        path.setFillRule(Qt.WindingFill)
        
        poly = self.polygon()
        poly_buff = self.bufferPolygon(poly, (self.grip_size+self.handle_size))
        
        path.addPolygon(poly_buff)
        return path
        
    def paint(self, painter, option, widget=None):
        """Reimplement paint() for painting polygons in the scene
        every time the scene is updated.
        """
        # Draw the polygon
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))
        pen = QPen(QColor(*self.line_color), self.line_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        pen.setCosmetic(True)
        painter.setPen(pen)
        
        painter.drawPolygon(self.polygon())
        
        # Draw bounding box for debugging purposes
        #painter.setBrush(QBrush(QColor(255, 0, 0, 0)))
        #painter.setPen(QPen(QColor(255, 255, 255), 1, Qt.SolidLine))
        #painter.drawRect(self.boundingRect())
        #painter.drawPath(self.shape())
        
        # Draw the handles
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QBrush(QColor(*self.vertex_color)))
        pen = QPen(QColor(*self.vertex_color), 1.0, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        pen.setCosmetic(True)
        painter.setPen(pen)
        if self.isSelected():
            for handle in self.handles:
                painter.drawEllipse(handle)


