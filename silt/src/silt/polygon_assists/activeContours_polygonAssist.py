import logging
import math
import time

import numpy as np
import scipy
import skimage

from .polygonAssist import (PolygonAssist,PolygonAssistGUI)
from PyQt5.QtWidgets import (QWidget, QSlider, QGridLayout, QLabel,
                             QPushButton,QComboBox, QSizePolicy, QApplication)
from PyQt5.QtCore import (Qt, QTimer, pyqtSignal)

# LOGGING
logger = logging.getLogger(__name__)
logging.basicConfig(filename='act_cont.log', level=logging.INFO)

class ActiveContourAssistGUI(QWidget):
    
    alg_options_changed = pyqtSignal(dict)
    
    def __init__(self,
                 parent = None):
        # Call parent class's constructor (__init__ function)
        super(ActiveContourAssistGUI,self).__init__(parent)
        
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
        
        
        # Slider for beta parameter
        self.beta_label = QLabel('Beta', self)
        self.GUIparts.append(self.beta_label)
        self.beta_slider = QSlider(Qt.Horizontal, self)
        self.GUIparts.append(self.beta_slider)
        self.beta_slider.setMinimum(paramater_min)
        self.beta_slider.setMaximum(paramater_max)
        self.beta_slider.setTracking(True)
                
        # Slider for gamma parameter
        self.gamma_label = QLabel('Gamma', self)
        self.GUIparts.append(self.gamma_label)
        self.gamma_slider = QSlider(Qt.Horizontal, self)
        self.GUIparts.append(self.gamma_slider)
        self.gamma_slider.setMinimum(paramater_min)
        self.gamma_slider.setMaximum(paramater_max)
        self.gamma_slider.setTracking(True)
        
        self.setOptions()
        
        self.alpha_slider.valueChanged.connect(self._onAlphaSliderMoved)
        self.alpha_slider.setToolTip(str(self.alpha_slider.value()))
        self.beta_slider.valueChanged.connect(self._onBetaSliderMoved)
        self.beta_slider.setToolTip(str(self.beta_slider.value()))
        self.gamma_slider.valueChanged.connect(self._onGammaSliderMoved)
        self.gamma_slider.setToolTip(str(self.gamma_slider.value()))
        
        
        self.layout.addWidget(self, 3, 1, 1, 3)
        self.layout.addWidget(self.alpha_label, 5, 1, 1, 1)
        self.layout.addWidget(self.alpha_slider, 5, 2, 1, 2)
        self.layout.addWidget(self.beta_label, 6, 1, 1, 1)
        self.layout.addWidget(self.beta_slider, 6, 2, 1, 2)
        self.layout.addWidget(self.gamma_label, 7, 1, 1, 1)
        self.layout.addWidget(self.gamma_slider, 7, 2, 1, 2)
        
        self.setLayout(self.layout)
        # Update the size policy
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        print('update alg op tions')
        self._onUpdateAlgOptions()
        
    def _onUpdateAlgOptions(self):
        self.alg_options_changed.emit(self.getAlgOptions())
             
    def setOptions(self,
                   alpha: int = 1,
                   beta: int = 1,
                   gamma: int = 1 ):
       
        # Set the slider positions
        # Make sure signals are blocked for this
        self.alpha_slider.blockSignals(True)
        self.alpha_slider.setValue(alpha)
        self.alpha_slider.setToolTip(str(self.alpha_slider.value()))
        self.alpha_slider.blockSignals(False)
        
        self.beta_slider.blockSignals(True)
        self.beta_slider.setValue(beta)
        self.beta_slider.setToolTip(str(self.beta_slider.value()))
        self.beta_slider.blockSignals(False)
        
        self.gamma_slider.blockSignals(True)
        self.gamma_slider.setValue(gamma)
        self.gamma_slider.setToolTip(str(self.gamma_slider.value()))
        self.gamma_slider.blockSignals(False)
        
    def removeGUI(self):
        for GUIpart in self.GUIparts:
            self.layout.removeWidget(GUIpart)
            GUIpart.deleteLater()
            del GUIpart
            
    def getAlgOptions(self):
        alg_options = {
            'alpha':self.alpha_slider.value(),
            'beta':self.beta_slider.value(),
            'gamma':self.gamma_slider.value()
            }
        return alg_options
        
    def _onAlphaSliderMoved(self,pos):
        """
        """
        self.alpha_slider.setToolTip(str(self.alpha_slider.value())) 
        self.update_timer.start()
        
    
    def _onBetaSliderMoved(self,pos):
        """"
        """
        self.beta_slider.setToolTip(str(self.beta_slider.value()))
        self.update_timer.start()
  
    def _onGammaSliderMoved(self,pos):
        """and emits the 
        alg_options_changed signal.
        """
        
        self.gamma_slider.setToolTip(str(self.gamma_slider.value()))
        self.update_timer.start()
        
class ActiveContour():
    def __init__(self):
        # Call parent class's constructor (__init__ function)
        super().__init__()
    
    def refine_polygon(self,image_chip,vertices,alg_options):
        # Start time for dev to see how long algorithm takes
        st = self._start_time()
        logger.info('Opening image as grayscale image')
        I_orig = np.asarray(self.processed_img) # TODO: need to test that self.processed_img is correctly formatted

        # I think this can be removed... TODO: Check
        logger.info('Image turned to grayscale')
        I_gray = self._image_to_grayscale(I_orig)

        # Blur image (gaussian). Using user defined value. TODO: Include this value as option in SILT?
        logger.info('Image blurred')
        # TODO: _blur_image is time expensive
        I_blur = self._blur_image(I_gray, self.img_blur)

        # Generate image differential (ie 1st derrivative)
        logger.info('Generating image differential')
        Img_Diff = self._diff_image(I_blur)

        # Blur differnce image (gaussian). Using user defined value. TODO: Include this value as option in SILT?
        logger.info('Image differential blurred')
        # TODO: _blur_image is time expensive
        dif_blur = self._blur_image(Img_Diff, self.dif_blur)

        # The contour must always be clockwise (because of the balloon force)
        logger.info('Normalizing contour')
        polygon=self._make_contour_clockwise(self.poly) # TODO: need to test that self.poly is correctly formatted

        # Make an uniform sampled contour
        logger.info('Interpolating contour points')
        polygon, _ =self._interpolate_contour_points(polygon, self.pix_dist_thresh)

        # logger.info('Calculating external energy')
        # external_energy = self._calc_external_energy(I_blur,dif_blur, self.w_line, self.w_edge)

        # Calculate refined snake (contour)
        logger.info('Calculating refined snake contour')
        snake_contour, quiver_frames = self._kass_snake(I_blur, dif_blur,polygon)

        self._end_time(st)
        
        return snake_contour.tolist() # TODO: check that returned format is correct

    def _kass_snake(self, image, edge_image, initial_contour):
        """
        Inputs:
            image:Array containing original image
            initial_contour: Dictionary containing "x" and "y" pixel values defining initial contour or polygon
            edge_image = The edge or gradient image that was calculated
        """
        quiver_frames = []
        
        self.max_iterations = int(self.max_iterations)
        if self.max_iterations <= 0:
            raise ValueError('max_iterations should be greater than 0.')

        convergence_order = 10

        image = skimage.img_as_float(image)

        # Calculate the external energy which is composed of the image intensity and ege intensity
        external_energy = self._calc_external_energy(image,edge_image,self.w_line,self.w_edge)

        # Take external energy array and perform interpolation over the 2D grid
        # If a fractional x or y is requested, then it will interpolate between the intensity values surrounding the point
        # This is an object that can be given an array of points repeatedly
        external_energy_interpolation = scipy.interpolate.RectBivariateSpline(np.arange(external_energy.shape[1]),
                                                                            np.arange(external_energy.shape[0]),
                                                                            external_energy.T, kx=2, ky=2, s=0)

        # Split initial contour into x's and y's
        x, y = np.array(initial_contour['x']), np.array(initial_contour['y'])

        # Create a matrix that will contain previous x/y values of the contour
        # Used to determine if contour has converged if the previous values are consistently smaller
        # than the convergence amount
        previousX = None
        previousY = None
        max_diff = []
        new_point_indices = []

        for i in range(self.max_iterations):
            # Build snake shape matrix for Euler equation
            # This matrix is used to calculate the internal energy in the snake
            # This matrix can be obtained from Equation 14 in Appendix A from Kass paper (1988)
            # r is the v_{i} components grouped together
            # q is the v_{i-1} components grouped together (and v_{i+1} components are the same)
            # p is the v_{i-2} components grouped together (and v_{i+2} components are the same)
            n = len(x)
            r = 2 * self.alpha + 6 * self.beta
            q = -self.alpha - 4 * self.beta
            p = self.beta

            A = r * np.eye(n) + \
                q * (np.roll(np.eye(n), -1, axis=0) + np.roll(np.eye(n), -1, axis=1)) + \
                p * (np.roll(np.eye(n), -2, axis=0) + np.roll(np.eye(n), -2, axis=1))

            # Invert matrix once since alpha, beta and gamma are constants
            # See equation 19 and 20 in Appendix A of Kass's paper
            AInv = scipy.linalg.inv(A + self.gamma * np.eye(n))
            # AInv = scipy.linalg.inv(self.gamma * A + np.eye(n))

            # TODO: This is the expensive part of this function
            # Calculate the gradient in the x/y direction of the external energy
            fx = external_energy_interpolation(x, y, dx=1, grid=False)
            fy = external_energy_interpolation(x, y, dy=1, grid=False)

            # Debug code for creating quiver plot:
            test=[]
            for v in fx:
                test.append(i/self.max_iterations)
            step=4
            test=test[::step]
            test[0] = 0
            test[1] = 1
            quiver_frames.append((x[::step], y[::step], fx[::step], fy[::step], test))

            # Compute new x and y contour
            # See Equation 19 and 20 in Appendix A of Kass's paper
            x_new = np.dot(AInv, self.gamma * x + fx)
            y_new = np.dot(AInv, self.gamma * y + fy)

            # Maximum pixel move sets a cap on the maximum amount of pixels that one step can take.
            # This is useful if one needs to prevent the snake from jumping past the location minimum one desires.
            # In many cases, it is better to leave it off to increase the speed of the algorithm

            # Calculated by getting the x and y delta from the new points to previous points
            # Then get the angle of change and apply max_pixel_move magnitude
            # Otherwise, if no maximum pixel move is set then set the x/y to be x_new/y_new
            # end time for algorithm
            if self.max_pixel_move:
                dx = self.max_pixel_move * (x_new - x)
                dx=dx.astype(int)
                dy = self.max_pixel_move * (y_new - y)
                dy=dy.astype(int)

                x += dx
                y += dy
            else:
                x = x_new
                y = y_new

            # j is variable that loops around from 0 to the convergence order. This is used to save the previous value
            # Convergence is reached when absolute value distance between previous values and current values is less
            # than convergence threshold
            # Note: Max on axis 1 and then min on the 0 axis for distance. Retrieves maximum distance from the contour
            # for each trial, and then gets the minimum of the 10 trials.
            j = i % (convergence_order)

            if (j+1) < convergence_order:
                if previousX is None and previousY is None:
                    previousX = x
                    previousY = y

                # Ensure x is the same size as previousX by ignoring new points in x
                x_reduced = np.delete(x, new_point_indices)
                y_reduced = np.delete(y, new_point_indices)

                # Find the biggest difference between points
                diff = np.max(np.abs(previousX - x_reduced) + np.abs(previousY - y_reduced))
                if diff != 0.0:
                    max_diff.append(diff)

                previousX = x
                previousY = y
            else:
                # Find the minimum of the max differences
                distance = np.min(max_diff)

                if distance < self.convergence:
                    break

                max_diff = []

            Pt={}
            Pt['x'] = x.tolist()
            Pt['y'] = y.tolist()
            
            initial_contour, new_point_indices = self._interpolate_contour_points(Pt, self.pix_dist_thresh)
            
            x, y = np.array(initial_contour['x']), np.array(initial_contour['y'])

        return np.array([x, y]).T, quiver_frames
            
    def _make_contour_clockwise(self, polygon):
        # Area inside contour
        O={}
        O['x'] = np.array(polygon['x']+ polygon['x'][0:2])
        O['y'] = np.array(polygon['y']+ polygon['y'][0:2])

        area = 0.5*sum(O['x'][1:len(polygon['x'])+1] * O['y'][2:len(polygon['x'])+2] - O['y'][0:len(polygon['x'])])
        
        # If the area inside  the contour is positive, change from counter-clockwise to 
        # clockwise
        if(area>0):
            polygon['x'].reverse()
            polygon['y'].reverse()

        return polygon

    def _sqrt_einsum_T(self, a, b):
        a_min_b = a - b
        return np.sqrt(np.einsum("ij,ij->j", a_min_b, a_min_b))

    def _calc_external_energy(self, I, edgeI, w_line, w_edge):
        external_energy = w_line * I + w_edge * edgeI
        return external_energy

    def _interpolate_contour_points(self, polygon: dict, pix_thresh: int):
        # list of (x,y) tuples
        x_y_pairs=list(zip(polygon['x'],polygon['y']))
        # Find distances between between neighboring points
        dists = [ math.sqrt((y[0]-x[0])**2 + (y[1]-x[1])**2) for x,y in zip(x_y_pairs, x_y_pairs[1:]) ]

        Pnew={}
        Pnew['x']=[]
        Pnew['y']=[]
        addep = False
        new_indexes = []
        # For each distance, check if it's above the pixel threshold
        for id, dist in enumerate(dists):
            if dist > pix_thresh:
                # Compute new interpolated points
                x_new_points = np.linspace(polygon['x'][id],polygon['x'][id+1],num=math.ceil(dist/pix_thresh),endpoint=addep).tolist()
                y_new_points = np.linspace(polygon['y'][id],polygon['y'][id+1],num=math.ceil(dist/pix_thresh),endpoint=addep).tolist()

                # Add new points to x and y coordinate lists
                Pnew['x']=Pnew['x'] + x_new_points
                Pnew['y']=Pnew['y'] + y_new_points

                # Calculate the indexes of the new points, used to omit the points when checking for convergence
                for index, _ in enumerate(x_new_points[1:]):
                    new_indexes.append(id+1 + index)
            else:
                # If not above threshold, simply add existing point to x and y coordinate lists
                Pnew['x']=Pnew['x']+[polygon['x'][id]]
                Pnew['y']=Pnew['y']+[polygon['y'][id]]
        
        # Wrap list by adding first point
        Pnew['x'].append(polygon['x'][0])
        Pnew['y'].append(polygon['y'][0])

        return Pnew, new_indexes
            
    def _image_to_grayscale(self, I):
        # If color image convert to grayscale
        if len(I.shape)>2:
            I=I; 
        return I

    def _blur_image(self, I, img_blur):
        bluredImage = scipy.ndimage.gaussian_filter(I, sigma=(img_blur, img_blur), order=0, truncate=1)
        bluredImage = bluredImage.astype('int32')
        return bluredImage

    def _diff_image(self, I):
        dx = scipy.ndimage.sobel(I, 0)  # horizontal derivative
        dy = scipy.ndimage.sobel(I, 1)  # vertical derivative
        mag = np.hypot(dx, dy)  # magnitude
        mag *= 255.0 / np.max(mag)  # normalize (Q&D)
        return mag

    def _start_time(self):
        st = time.time()
        return st

    def _end_time(self, st):
        et = time.time()
        elapsed_time = et - st
        #print('\n\nExecution time:', elapsed_time, 'seconds\n\n')
