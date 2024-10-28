#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Code for SILT main application window, including menu and
# tool bars.  Also home to the undo/redo stack.
#################################################################

import copy
import h5py
import importlib
import json
import numpy as np
import os
from pathlib import Path


from PyQt5.QtWidgets import (QApplication, QMainWindow,
                             QAction, QMenu, QFileDialog,
                             QMessageBox, QUndoStack,
                             QUndoCommand, qApp, QDockWidget, QProgressBar)
from PyQt5.QtGui import (QIcon, QKeySequence, QBrush, QColor)
from PyQt5.QtCore import (QItemSelectionModel, Qt, QThreadPool, 
                          QRunnable, pyqtSignal, QObject, pyqtSlot)
from . import utils
from .mainwidget import MainWidget
from .levels_slider_widget import LevelsSliderWidget
from .pyramid_preprocessing import generate_pyramid
from .poly_assist_widget import PolyAssistWidget


def run(argv):
    app = QApplication(argv)
    ex = MainWindow()
    app.exec_()
    app.quit()

class MainWindow(QMainWindow):
    """Central window; base application.  Contains file menus and the
    main interactive widget.
    
    Attributes
    ----------
    central_widget: mainwidget.MainWidget
        Subclass of PyQt5.QtWidgets.QWidget; the main interactive widget.
        Controls communications between the MainWindow object (menus
        and toolbars) and the subwidgets contained within itself.
    open_image_act: PyQt5.QtWidgets.QAction
        Located in the File menu; opens an image
    open_overlay_act: PyQt5.QtWidgets.QAction
        Located in the File menu; opens an overlay file
    open_saved_labels_act: PyQt5.QtWidgets.QAction
        Located in the File menu; opens a saved labels file
    save_mask_act: PyQt5.QtWidgets.QAction
        Located in the File menu; saves an image mask
    save_act: PyQt5.QtWidgets.QAction
        Located in the File menu; saves the labels to an automatically-
        named labels file.
    saveas_act: PyQt5.QtWidgets.QAction
        Located in the File menu; saves the labels to a user-chosen
        labels file.
    edit_menu: PyQt5.QtWidgets.QMenu
        Edit menu in the menubar
    items_toolbar: PyQt5.QtWidgets.QToolBar
        Toolbar for adding/editing overlay items (the items like polygons
        which lay over the image)
    
    template_flag: bool
        Flag to indicate whether a template is open
    image_flag: bool
        Flag to indicate whether an image is open
    save_path: str
        The path to which the labels should be saved when the user 
        chooses File -> Save.  This is set automatically as the path 
        to where the image is stored unless the user chooses 
        File -> Save As.
    image_size: tuple of ints
        Used to create the image mask, if the user chooses to save
        one.  Set in `_openImageAction`.
    image_file: str
        The path and filename of the opened image file.  Set in 
        `_openImageAction` and outputted to the labels file when the
        user choose File -> Save.
    
    template_list: list
        The list of input template options which the user should
        have specified in the template file.
    image_info_dict: dict
        The dictionary of required/optional image information 
        options which the user should have specified in the
        template file.
    outputs_options_dict: dict
        The dictionary of optional output options which the
        user should have specified in the template file.
    
    """
    
    source_directory = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    
    def __init__(self, parent=None):
        """Initialize the main window.
        """
        super(MainWindow, self).__init__(parent)
        
        self.central_widget = None
        self.template_flag = False
        self.image_flag = False
        self.save_path = None
        self.undo_stack = QUndoStack(self)
        self.undo_stack_index = self.undo_stack.index()
        self.series_mode = False
        self.geo_transform = None
        self.image_file = None
        self.no_pyramid = False
        self.progress = QProgressBar()
        self.threadpool = QThreadPool()
        self._initUI()
    
    def _initUI(self):
        """Set up the main UI.
        
        Notes
        -----
        Initializes the menu bar, tool bar, central widget, and
        the system window (including size and title)
        """
        
        # Set up the status bar and menus
        self.statusBar().showMessage('Welcome')
        self._initFileMenu()
        self._initEditMenu()
        self._initViewMenu()
        self._initToolbar()
        
        # Set up the center widget and layout
        self.central_widget = MainWidget(self)
        self.setCentralWidget(self.central_widget)
        self._initDockWidgets()
        
        # Make connections with central widget
        self.central_widget.command_added.connect(self._undoStackPush)
        
        # Set up the title and show the widget
        self.setWindowTitle('Sandia Image Labeling Tool')
        self.setWindowIcon(QIcon(self.source_directory + '/silt/thumbs/slogo2c.png'))
        self.resize(1280, 720)
        self.show()
        
        # Read in the config file
        self._initConfigOptions()
    
    def _initFileMenu(self):
        """Set up the file menu.
        
        Notes
        -----
        Sets up the File menu in the menu bar.  The File menu
        contains actions to open a template, open an image,
        open a saved labels file, and save a labels file.
        """
        
        file_menu = self.menuBar().addMenu('&File')
        
        # Template options
        open_template_act = QAction('Open Template', self)
        open_template_act.triggered.connect(self._openTemplateAction)
        file_menu.addAction(open_template_act)
        
        file_menu.addSeparator()
        
        # Image options
        self.open_image_act = QAction('&Open Image', self)
        self.open_image_act.setShortcut('Ctrl+O')
        self.open_image_act.triggered.connect(self._openImageAction)
        file_menu.addAction(self.open_image_act)
        self.open_image_act.setEnabled(False)
        
        self.open_series_act = QAction('Open Series', self)
        self.open_series_act.triggered.connect(self._openSeriesAction)
        file_menu.addAction(self.open_series_act)
        self.open_series_act.setEnabled(False)

        # Open overlay options
        self.open_overlay_act = QAction('Open Overlay', self)
        self.open_overlay_act.triggered.connect(self._openOverlayAction)
        file_menu.addAction(self.open_overlay_act)
        self.open_overlay_act.setEnabled(False)

        # Open labels
        self.open_saved_labels_act = QAction('Open Saved Labels', self)
        self.open_saved_labels_act.triggered.connect(
                self._openSavedLabelsAction)
        file_menu.addAction(self.open_saved_labels_act)
        self.open_saved_labels_act.setEnabled(False)
        
        file_menu.addSeparator()
        
        self.save_mask_act = QAction('Save mask', self)
        self.save_mask_act.triggered.connect(self._saveMask)
        file_menu.addAction(self.save_mask_act)
        self.save_mask_act.setEnabled(False)
        
        # Label/Annotations options
        self.save_act = QAction('&Save', self)
        self.save_act.setShortcut('Ctrl+S')
        self.save_act.triggered.connect(self._save)
        file_menu.addAction(self.save_act)
        self.save_act.setEnabled(False)
        
        self.saveas_act = QAction('Save as...', self)
        self.saveas_act.setShortcut('Ctrl+Shift+S')
        self.saveas_act.triggered.connect(self._saveasAction)
        file_menu.addAction(self.saveas_act)
        self.saveas_act.setEnabled(False)

        file_menu.addSeparator()
        
        # Close options
        self.close_image_act = QAction('Close Image', self)
        self.close_image_act.triggered.connect(self._closeImageAction)
        file_menu.addAction(self.close_image_act)
        self.close_image_act.setEnabled(False)
        
        self.close_series_act = QAction('Close Series', self)
        self.close_series_act.triggered.connect(self._closeSeriesAction)
        file_menu.addAction(self.close_series_act)
        self.close_series_act.setEnabled(False)

        # Close overlay
        self.close_overlay_act = QAction('Close Overlay', self)
        self.close_overlay_act.triggered.connect(self._closeOverlayAction)
        file_menu.addAction(self.close_overlay_act)
        self.close_overlay_act.setEnabled(False)
        
        file_menu.addSeparator()

        # Exit option
        exit_act = QAction('&Exit', self)
        exit_act.setShortcut('Ctrl+Q')
        #exit_act.triggered.connect(qApp.quit)
        exit_act.triggered.connect(self._exitAction)
        file_menu.addAction(exit_act)
    
    def _initEditMenu(self):
        """Set up edit menu.
        
        Notes
        -----
        Sets up the edit menu in the menu bar.  The edit menu contains
        actions to add various overlay items to the image (as well as
        add their corresponding user input fields to the side panel).
        """
        
        self.edit_menu = self.menuBar().addMenu('&Edit')
        
        # Undo and redo actions
        self.undo_act = self.undo_stack.createUndoAction(self, 'Undo')
        self.undo_act.setShortcut(QKeySequence.Undo)
        self.edit_menu.addAction(self.undo_act)
        #self.undo_act.triggered.connect(self._onUndoAct)
        
        self.redo_act = self.undo_stack.createRedoAction(self, 'Redo')
        self.redo_act.setShortcut(QKeySequence.Redo)
        self.edit_menu.addAction(self.redo_act)
        
        # Submenu for adding labels to the image
        self.edit_menu.addSeparator()
        add_menu = QMenu('Add', self)
        
        #add_point_act = QAction('Add point', self)
        #add_menu.addAction(add_point_act)
        
        add_polygon_act = QAction('Add polygon', self)
        add_menu.addAction(add_polygon_act)
        add_polygon_act.triggered.connect(self._onAddPolygonAct)
        
        #add_rectangle_act = QAction('Add rectangle', self)
        #add_menu.addAction(add_rectangle_act)
        
        #add_bbox_act = QAction('Add bounding box', self)
        #add_menu.addAction(add_bbox_act)
        
        self.edit_menu.addMenu(add_menu)

        # Add the copy actions
        self.copy_label_items_from_previous_act = QAction('Copy Label Items From Previous', self)
        self.copy_label_items_from_previous_act.triggered.connect(self._copyLabelItemsFromPreviousAction)
        self.edit_menu.addAction(self.copy_label_items_from_previous_act)
        self.copy_label_items_from_previous_act.setShortcut('Ctrl+J')
        self.copy_label_items_from_previous_act.setEnabled(False)
        
        self.copy_label_items_act = QAction('Copy Label Items From...', self)
        self.copy_label_items_act.triggered.connect(self._copyLabelItemsAction)
        self.edit_menu.addAction(self.copy_label_items_act)
        
        # Delete all labels from the image
        self.edit_menu.addSeparator()
        clear_all_act = QAction('Delete all labels', self)
        self.edit_menu.addAction(clear_all_act)
        clear_all_act.setEnabled(False)
        
        self.edit_menu.setEnabled(False)
        
        
    def _initViewMenu(self):
        """Set up view menu.
        
        Notes
        -----
        Sets up the view menu in the menu bar.  The view menu contains
        actions to show or display various information.
        """
        self.view_menu = self.menuBar().addMenu('&View')
        self.show_uuids_act = QAction('Show UUIDs', self)
        self.show_uuids_act.setCheckable(True)
        self.show_uuids_act.triggered.connect(self._showUUIDsAction)
        self.show_uuids_act.setChecked(True)
        self.view_menu.addAction(self.show_uuids_act)

        self.show_overlay_act = QAction('Show Overlay', self)
        self.show_overlay_act.setCheckable(True)
        self.show_overlay_act.triggered.connect(self._showOverlayAction)
        self.show_overlay_act.setChecked(False)
        self.view_menu.addAction(self.show_overlay_act)
        self.show_overlay_act.setEnabled(False)

        self.view_menu.setEnabled(False)
        
        
    def _initToolbar(self):
        """Set up toolbar.
        
        Notes
        -----
        The items toolbar contains icons for adding various
        label items to the image.  Options for adding these
        items also exist in the Edit menu in the menu bar.
        """
        
        self.items_toolbar = self.addToolBar('Image Labeling')
        add_polygon_act = QAction(QIcon(self.source_directory + '/silt/thumbs/poly.png'), 'Add polygon', self)
        add_polygon_act.triggered.connect(self._onAddPolygonAct)
        self.items_toolbar.addAction(add_polygon_act)
        self.items_toolbar.hide()

    
        
    def _initDockWidgets(self):
        """Set up the dock widgets
        """
        # Levels slider for contrast adjustment
        self.levels_widget = LevelsSliderWidget(parent=self)
        levels_dockwidget = QDockWidget("Image Levels", self)
        levels_dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        levels_dockwidget.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        levels_dockwidget.setWidget(self.levels_widget)
        self.levels_widget.levels_updated.connect(self.central_widget.setImageLevels)
        self.levels_widget.auto_range.connect(self._onAutoRangePressed)
        self.levels_widget.reset.connect(self.central_widget.resetImageLevels)
        self.addDockWidget(Qt.RightDockWidgetArea, levels_dockwidget)

        # Add to view menu
        self.view_menu.addAction(levels_dockwidget.toggleViewAction())
        levels_dockwidget.hide()
        
        # Polygon Assist Top Widget - TODO: Feature is disabled until plugins are completed (10/3/2024)
        '''
        self.polyassist_widget = PolyAssistWidget(parent=self)
        self.polyassist_widget.refine_poly.connect(self.central_widget.refinePolyPressed)

        polyassit_dockwidget = QDockWidget("Polygon Assist", self)
        polyassit_dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        polyassit_dockwidget.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        polyassit_dockwidget.setWidget(self.polyassist_widget) 
        self.addDockWidget(Qt.RightDockWidgetArea, polyassit_dockwidget)
        
        # Add to view menu 
        self.view_menu.addAction(polyassit_dockwidget.toggleViewAction())
        polyassit_dockwidget.hide()
        
        # Polygon Assist Options Widget
        self.polyassitOptions_dockwidget = QDockWidget("Polygon Assist Options", self)
        self.polyassitOptions_dockwidget.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.polyassitOptions_dockwidget.setFeatures(QDockWidget.DockWidgetClosable | QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        
        # when the method changes, update GUI
        self.polyassist_widget.alg_method_changed.connect(self.updatePolyAssist)
        self.updatePolyAssist(assistexist=False)
        '''
    def updatePolyAssist(self, method:str='Fake Shift (TEST)',assistexist=True):        
        # Remove old UI if it exists
        print('Are we there yet?!')
        if assistexist:
            print('Lets remove!')
            self.polyassistOptions_widget.removeGUI()
            
        # Set up new UI
        polygon_assistant_GUI = utils.get_poly_assist_GUI(method)
        self.polyassistOptions_widget = polygon_assistant_GUI(parent=self)
        assistexist=True
        self.polyassitOptions_dockwidget.setWidget(self.polyassistOptions_widget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.polyassitOptions_dockwidget)
        self.polyassitOptions_dockwidget.setVisible(True)
        self.polyassistOptions_widget.setOptions()
        #self.polyassitOptions_dockwidget.hide()
        
        # Update options in view widget where alg will be called.
        self.central_widget.updatePolyAssistMethod(method)
        self.polyassistOptions_widget.alg_options_changed.connect(self.central_widget.updatePolyAssistOptions)
                
    def _initConfigOptions(self):
        """Open the config file (if there is one) and set up
        the config options.
        
        Notes
        -----
        The config file will be used to set default options,
        e.g. If the user wants the same template to automatically
        open every time they run the program in the near future,
        they would set the default template in the config file.
        The config file sits in the same directory as __setup__.py
        and must be called siltconfig.json.
        """
        config_file = self.source_directory + "/siltconfig.json"
        if not os.path.exists(config_file):
            return
        
        with open(config_file, 'r') as fid:
            config_options = json.load(fid)
        
        if 'default_template_file' in config_options.keys():
            default_template_file = config_options['default_template_file']
            if os.path.exists(default_template_file):
                self._openTemplate(default_template_file)
    
    
    #################################
    # SLOTS                         #
    #################################

    # ***************************************** #
    # TEMPLATE I/O
    # ***************************************** #
    def _openTemplateAction(self):
        """Menu action to open a template.
        
        Notes
        -----
        Opens a file open dialog for the user to browse.
        """
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, 'Open Template', "", 
            "Template files (*.silttemplate.json)", options=options)[0]
        if filename == '':
            return
        
        self._openTemplate(filename)
        
    def _openTemplate(self, filename):
        """Open a template.
        """
        self.updateStatusBar("Opening template {}...".format(filename))
        template_deprecated = False
        
        with open(filename, 'r') as fid:
            tmp_dict = json.load(fid)

        # Make sure the template has the required keys
        if ('template_info' not in tmp_dict.keys() or
            'image_info' not in tmp_dict.keys()):
            infostr = ("Please make sure your template file includes "
                       "both the \'template_info\' and \'image_info\' "
                       "keys.")
            ret = self._showDialogBox(title = "Error: Template",
                                       message = "Template file missing required keys.",
                                       more_info = infostr)
            
            self.updateStatusBar("Aborted.")
            return

        # Get each dictionary from the template file
        if 'template_info' in tmp_dict.keys():
            template_list = tmp_dict['template_info']
            self.central_widget.clearDisplayItems()
            self.central_widget.setTemplate(template_list,
                                            template_file=filename)
            self.template_flag = True
            self.open_image_act.setEnabled(True)
            self.open_series_act.setEnabled(True)
            self.template_list = template_list
        
        if 'image_info' in tmp_dict.keys():
            image_info_dict = tmp_dict['image_info']
            self.image_info_dict = image_info_dict
            if 'geo_transform' not in self.image_info_dict.keys():
                self.image_info_dict['geo_transform'] = 'geo_transform'

        if 'overlay_item_options' in tmp_dict.keys():
            # TODO pop up warning box to update template
            template_decprecated = True
            
            label_item_options_dict = tmp_dict['overlay_item_options']
            self.central_widget.setLabelItemStyleOptions(label_item_options_dict)
            
        if 'label_item_options' in tmp_dict.keys():
            label_item_options_dict = tmp_dict['label_item_options']
            self.central_widget.setLabelItemStyleOptions(label_item_options_dict)
        
        if 'outputs_options' in tmp_dict.keys():
            self.outputs_options_dict = tmp_dict['outputs_options']

            # If there are still old keys in there, add the new ones
            # in the global variable dict 
            if ("default_output_keys" in self.outputs_options_dict.keys()):
                if ("overlay_item_vertices" in
                    self.outputs_options_dict["default_output_keys"].keys()):
                    template_deprecated = True
                    self.outputs_options_dict["default_output_keys"]["label_item_vertices"] = \
                        self.outputs_options_dict["default_output_keys"]["overlay_item_vertices"]
                if ("overlay_item_uuid" in
                    self.outputs_options_dict["default_output_keys"].keys()):
                    template_deprecated = True
                    self.outputs_options_dict["default_output_keys"]["label_item_uuid"] = \
                        self.outputs_options_dict["default_output_keys"]["overlay_item_uuid"]
        else:
            self.outputs_options_dict = None

        if template_deprecated:
            infostr = ("It looks like this template contains some old "
                       "keys which will be deprecated in a future version. "
                       "Any labels generated or updated using this "
                       "template with this version of SILT will have "
                       "updated default keys (i.e. any \'overlay_item*\' "
                       "keys are now \'label_item*\'). "
                       "Please replace \'overlay_item_options\', "
                       "\'overlay_item_vertices\', and/or "
                       "\'overlay_item_uuid\' with \'label_item_options\', "
                       "\'label_item_vertices\', and/or "
                       "\'label_item_uuid\', as necessary.")
            ret = self._showDialogBox(title = "Warning: SILT Template",
                                       message = "Deprecation warning.",
                                       more_info = infostr)
        
        # Update the status bar that the template was opened successfully
        self.updateStatusBar("Opened template {}.".format(filename))

    
    # ***************************************** #
    # IMAGE I/O
    # ***************************************** #
    def _openImageAction(self):
        """Menu action to open an image.
        """
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, 'Open Image', "",
            "Image files (*.h5)", options=options)[0]
        if filename == '':
            return
        
        ret = self._openImage(filename)
        if ret == -1:
            return
        
        # Disable the series options
        self.open_series_act.setEnabled(False)
        self.close_series_act.setEnabled(False)
        self.copy_label_items_from_previous_act.setEnabled(False)
    
    
    def _openImage(self, filename: str):
        """
        Open an image. Manages dialog for loading pyramid, and creates thread is
        user chooses to generate pyramid.
        """
        ret = self._closeImageAction()
        if ret == -1:
            self.updateStatusBar("Canceled.")
            return -1
        
        self.image_file = str(os.path.abspath(filename))

        self.updateStatusBar("Opening image...")

        ret = self._showDialogBox(title="Pyramid Generation",
                                  message="Generate image pyramid? Recommended for very large images.",
                                  more_info="This will save memory usage by not loading the entire image at once.",
                                  box_type="choice")

        if ret == QMessageBox.Yes:
            self.no_pyramid = False
            self.updateStatusBar("Generating image pyramid...")
        elif ret == QMessageBox.No:
            self.no_pyramid = True
            self.updateStatusBar("Loading image...")

        self.statusBar().repaint() # Ensure it displays before starting generation

        # Create progress bar for loading
        self.progress = QProgressBar()

        self.statusBar().addPermanentWidget(self.progress)
        self.statusBar().repaint()

        worker = Worker(fn=generate_pyramid, 
                        file_path=filename, 
                        image_key=self.image_info_dict["data_path"],
                        no_pyramid=self.no_pyramid)
        
        worker.signals.progress.connect(self._update_progress)
        worker.signals.finished.connect(self._load_image)

        self.threadpool.start(worker)
    
        
    def _update_progress(self, progress):
        index, total = progress
        self.progress.setRange(0, total)
        self.progress.setValue(index)
        self.statusBar().repaint()


    def _load_image(self, image_file: str = None):
        """
        Load image into view widget, and configure UI accordingly.
        """
        if image_file is not None:
            self.image_file = image_file

        self.updateStatusBar("Loading image...this may take a while.")
        self.progress.setRange(0, 0)
        self.statusBar().repaint()

        with h5py.File(self.image_file, "r") as image_data:
            # If the geo transform exists in the image file, get it
            geo_transform = image_data.get(self.image_info_dict["geo_transform"])
            if geo_transform is not None:
                self.geo_transform = np.array(geo_transform)

            # Set initial image levels
            self.image_min = int(image_data.attrs["image_min"])
            self.image_max = int(image_data.attrs["image_max"])
            self.image_mid = int((self.image_max - self.image_min)/2) + self.image_min

            self.image_size = image_data.get(self.image_info_dict["data_path"]).shape[:2]
        
        self.central_widget.setImage(self.image_file, 
                                    self.image_info_dict["data_path"],
                                    self.image_min,
                                    self.image_mid,
                                    self.image_max,
                                    self.no_pyramid)
        
        # Set the levels dockwidget with the min and max values
        self.levels_widget.setImageMinimum(self.image_min,
                                           reset_slider_pos = True)
        self.levels_widget.setImageMaximum(self.image_max,
                                           reset_slider_pos = True)
        self.levels_widget.setImageMidpoint(self.image_mid)
        
        # Clear the undo stack
        #self.undo_stack.clear()
        
        self.image_flag = True
        
        self.edit_menu.setEnabled(True)
        self.view_menu.setEnabled(True)
        self.items_toolbar.show()
        
        self.save_path = os.path.splitext(self.image_file)[0] + ".json"
        if self.outputs_options_dict is not None:
            if "default_labels_extension" in self.outputs_options_dict.keys():
                self.save_path = (os.path.splitext(self.image_file)[0]
                                  + self.outputs_options_dict["default_labels_extension"])
                
        if os.path.exists(self.save_path):
            self._openSavedLabels(self.save_path)
        
        self.save_mask_act.setEnabled(True)
        self.save_act.setEnabled(True)
        self.saveas_act.setEnabled(True)
        self.open_overlay_act.setEnabled(True)
        self.open_saved_labels_act.setEnabled(True)
        self.close_image_act.setEnabled(True)
        
        self.updateStatusBar("Opened image {}".format(self.image_file))

        if self.progress != None:
            self.statusBar().removeWidget(self.progress)

        return 0

    
    def _closeImageAction(self):
        """Menu action to close an image.
        """
        # Check to see if there are unsaved changes
        if self.undo_stack.index() != self.undo_stack_index:
            err_box = QMessageBox()
            err_box.setIcon(QMessageBox.Warning)
            err_box.setText("There are unsaved changes to this image.")
            err_box.setInformativeText("Please choose whether to save "
                                       "or continue without saving.")
            err_box.setWindowTitle("Unsaved Changes")
            err_box.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel | QMessageBox.Discard)
            err_box.setDefaultButton(QMessageBox.Cancel)
            ret = err_box.exec_()
            
            if ret == QMessageBox.Save:
                self._save()
            elif ret == QMessageBox.Cancel:
                return -1
        
        # Close any overlays
        self._closeOverlay()
        
        # Clear the image and user inputs
        self.central_widget.clearImage()
        self.central_widget.clearInputs()

        # Clear the undo stack
        self.undo_stack.clear()
        self.undo_stack_index = 0
        
        # Clear the image flag
        self.image_flag = False
        
        # Disable the edit_menu and toolbar
        self.edit_menu.setEnabled(False)
        self.view_menu.setEnabled(False)
        self.items_toolbar.hide()
        
        # Disable other menu options
        self.save_mask_act.setEnabled(False)
        self.save_act.setEnabled(False)
        self.saveas_act.setEnabled(False)
        self.open_overlay_act.setEnabled(False)
        self.open_saved_labels_act.setEnabled(False)
        self.close_image_act.setEnabled(False)
        self.open_series_act.setEnabled(True)

        # Clear image data
        self.image_file = None
        
        self.updateStatusBar("Closed image.")
        
        return 0
    
    
    # ***************************************** #
    # SERIES I/O
    # ***************************************** #
    def _openSeriesAction(self):
        """Menu action to open an image series.
        """
        options = QFileDialog.Options(QFileDialog.ShowDirsOnly)
        search_dir = QFileDialog.getExistingDirectory(
            self, 'Open Series', "",
            options=options)
        
        if search_dir == '':
            return
        
        search_dir = Path(search_dir)
        filenames = [str(p) for p in sorted(search_dir.glob("**/*.h5"))]
        
        if filenames == []:
            return
        
        self._openSeries(filenames)
        
        # Disable single image options
        self.open_image_act.setEnabled(False)
        self.close_image_act.setEnabled(False)

        # Enable series-only options
        self.copy_label_items_from_previous_act.setEnabled(True)
    
    
    def _openSeries(self, filenames):
        """Open a series of images.
        """
        
        # Close the current series if there is one
        if self.series_mode:
            self._closeSeriesAction()
        
        # Close the current image
        #self._closeImageAction()
        ret = self._closeImageAction()
        if ret == -1:
            return
        
        # Update the status bar
        self.updateStatusBar("Opening series...")

        # Check the h5 files for the appropriate path
        checked_filenames = []
        siltlabels_exists = []
        tot = float(len(filenames))
        i = 0.0
        for fn in filenames:
            with h5py.File(fn, 'r') as fid:
                if self.image_info_dict['data_path'] in fid.keys():
                    checked_filenames.append(fn)
                    save_path = os.path.splitext(os.path.abspath(fn))[0] + ".siltlabels.json"
                    if os.path.exists(save_path):
                        siltlabels_exists.append(True)
                    else:
                        siltlabels_exists.append(False)
            i += 1
            self.updateStatusBar("Opening series {}%".format(int(100*i/tot)))
        
        # Pop up the series selection panel
        self.central_widget.startSeriesMode(checked_filenames)

        # Update the colors of the items in the series selection panel
        for i in range(len(siltlabels_exists)):
            it = self.central_widget.series_selection_widget.item(i)
            if siltlabels_exists[i]:
                it.setBackground(QBrush(QColor(205, 240, 205, 255)))
            else:
                it.setBackground(QBrush(QColor(255, 255, 255, 255)))
        
        # Connect changes in file selection to the open image slot
        #self.central_widget.series_selection_changed.connect(self._onSeriesSelectionChanged)
        self.central_widget.series_selection_widget.currentItemChanged.connect(self._onSeriesSelectionChanged)
        
        # Enable toolbar and other menu options
        self.close_series_act.setEnabled(True)
        
        # Set flag
        self.series_mode = True
        
        self.updateStatusBar("Opened series")
    
    
    def _onSeriesSelectionChanged(self, current_qlist_item, previous_qlist_item):
        """Slot to deal with a selection change in series mode.
        """
        # Try to open the current selection
        self._openImage(current_qlist_item.text())
        self.close_image_act.setEnabled(False)
        
        # If the user canceled, go back to the previous file
        if previous_qlist_item is not None:
            if self.image_file == os.path.abspath(previous_qlist_item.text()):
                row = self.central_widget.series_selection_widget.row(previous_qlist_item)
                
                self.central_widget.series_selection_widget.blockSignals(True)
                self.central_widget.series_selection_widget.setCurrentItem(previous_qlist_item, QItemSelectionModel.Select)
                previous_qlist_item.setSelected(True)
                self.central_widget.series_selection_widget.blockSignals(False)
    
    
    def _closeSeriesAction(self):
        """Menu action to close an image series.
        """
        ret = self._closeImageAction()
        if ret == -1:
            return
        self.central_widget.quitSeriesMode()
        self.close_series_act.setEnabled(False)
        self.open_image_act.setEnabled(True)
        self.copy_label_items_from_previous_act.setEnabled(False)

        self.series_mode = False
        
        self.updateStatusBar("Closed series.")
    
    
    # ***************************************** #
    # LABELS I/O
    # ***************************************** #
    def _openSavedLabelsAction(self):
        """Menu action to open a saved labels file.
        """
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, 'Open Labels', "",
            "Label files (*.json)", options=options)[0]
        if filename == '':
            return

        # Clear the undo stack
        self.undo_stack.clear()

        # Load the saved labels file
        self._openSavedLabels(filename)

        # Reset the save path
        self.save_path = filename
        
        
    def _openSavedLabels(self, filename: str):
        """Open saved labels.
        """
        with open(filename, 'r') as fid:
            label_list = json.load(fid)

        # Clear the multi-input panel (if there are any inputs)
        self.central_widget.clearInputs()
        
        # Clear the image of label items (if there are any)
        self.central_widget.clearLabelItems()
        
        # Parse the labels and load them in the main widget
        self._parseLabelList(label_list)
        

    def _parseLabelList(self, label_list: list):
        """Parse the list of labels
        """
        # Get the first label in the label_list to check the silt
        # version and set the appropriate default key names
        if len(label_list) > 0:
            if 'silt_version' in label_list[0].keys():
                label_item_uuid_key = 'label_item_uuid'
                label_item_vertices_key = 'label_item_vertices'
                label_item_pixels_key = 'label_item_pixels'
                label_item_bounding_rect_key = 'label_item_bounding_rect'
                label_item_type_key = 'label_item_type'
            else:
                # TODO popup warning that some of the keys will be
                # updated.
                infostr = ("It looks like this labels file contains some "
                           "old keys which will be deprecated in a future "
                           "version. If you continue with this version of "
                           "SILT, some of the labels file keys will be "
                           "overwritten, i.e. any default \'overlay_item*\' "
                           "keys will become \'label_item*\'. You may "
                           "preserve the old keys by overriding the new "
                           "default keys in the template file.")
                ret = self._showDialogBox(title = "Warning: SILT Labels",
                                           message = "Deprecation warning.",
                                           more_info = infostr)
                label_item_uuid_key = 'overlay_item_uuid'
                label_item_vertices_key = 'overlay_item_vertices'
                label_item_pixels_key = 'overlay_item_pixels'
                label_item_bounding_rect_key = 'overlay_item_bounding_rect'
                label_item_type_key = 'overlay_item_type'
                
        else:
            return
        
        # If the user opted to override the other default keys,
        # read and set those keys appropriately
        image_filename_key = 'image_filename'
        geo_transform_key = 'geo_transform'
        geo_vertices_key = 'geo_vertices'
        if self.outputs_options_dict is not None:
            if ('default_output_keys' in self.outputs_options_dict.keys()):
                if ('label_item_uuid' in self.outputs_options_dict['default_output_keys'].keys()):
                    label_item_uuid_key = self.outputs_options_dict['default_output_keys']['label_item_uuid']
                if ('label_item_vertices' in self.outputs_options_dict['default_output_keys'].keys()):
                    label_item_vertices_key = self.outputs_options_dict['default_output_keys']['label_item_vertices']
                if ('image_filename' in self.outputs_options_dict['default_output_keys'].keys()):
                    image_filename_key = self.outputs_options_dict['default_output_keys']['image_filename']
                if ('geo_transform' in self.outputs_options_dict['default_output_keys'].keys()):
                    geo_transform_key = (self.outputs_options_dict['default_output_keys']['geo_transform'])
                if ('geo_vertices' in self.outputs_options_dict['default_output_keys'].keys()):
                    geo_vertices_key = (self.outputs_options_dict['default_output_keys']['geo_vertices'])
        
        # Get the label items
        if len(label_list) > 0:
            # Check if the label_item default keys are correct
            if (label_item_vertices_key not in label_list[0].keys() or
                label_item_uuid_key not in label_list[0].keys() or
                image_filename_key not in label_list[0].keys()):
                infostr = ("The siltlabels file does not match the current "
                           "template and cannot be loaded. If you continue "
                           "with this template your siltlabels file may be "
                           "overwritten.")
                ret = self._showDialogBox(title = "Error: Siltlabels",
                                           message = "Error loading siltlabels file.",
                                           more_info = infostr)
                return
            
            # Delete the overlay items, leaving just the user inputs
            # and the things that need to be kept static, like the
            # uuid
            user_inputs_list = copy.deepcopy(label_list)
            for l in user_inputs_list:
                # Keep the uuid, but change the key to default
                if label_item_uuid_key != 'label_item_uuid':
                    l['label_item_uuid'] = l[label_item_uuid_key]
                    del(l[label_item_uuid_key])

                # Delete the label item stuff
                if label_item_pixels_key in l.keys():
                    del(l[label_item_pixels_key])
                if label_item_bounding_rect_key in l.keys():
                    del(l[label_item_bounding_rect_key])
                del(l[label_item_type_key])
                del(l[label_item_vertices_key])

                # Delete geotransform stuff if it's there
                if geo_transform_key in l.keys():
                    del(l[geo_transform_key])
                if geo_vertices_key in l.keys():
                    del(l[geo_vertices_key])

                # Delete the SILT version number if it's there
                if 'silt_version' in l.keys():
                    del(l['silt_version'])
            
            # Check if the user inputs agrees with the template
            #user_inputs_list = copy.deepcopy(label_list)
            user_inputs_ok = True
            template_labels = [tmpl['label'] for tmpl in self.template_list]
            inputs_labels = list(user_inputs_list[0].keys())
            inputs_labels.remove(image_filename_key)
            inputs_labels.remove('label_item_uuid')
            for l in inputs_labels:
                if l not in template_labels:
                    #print ("{} not in template labels.".format(l))
                    user_inputs_ok = False
            if not user_inputs_ok:
                infostr = ("The siltlabels file contains "
                           "at least one field that is "
                           "not in the template file. If "
                           "you continue with this "
                           "template those fields may be "
                           "overwritten.")
                ret = self._showDialogBox(title = "Warning: Siltlabels",
                                           message = "Extra fields in siltlabels file.",
                                           more_info = infostr)
                
            # Check if the labels types match the template, e.g. if 
            # you're loading a combobox, then the siltlabels should
            # have a list of 'options'.  If it has a string instead,
            # the type is wrong.
            user_inputs_ok = True
            for tmpl in self.template_list:
                if tmpl['label'] in inputs_labels:
                    if tmpl['type'].lower() == 'lineedit':
                        if type(user_inputs_list[0][tmpl['label']]) is not str:
                            #print ("{} type doesn't match.".format(tmpl['label']))
                            user_inputs_ok = False
                            
                    elif (tmpl['type'].lower() == 'combobox'):
                        if type(user_inputs_list[0][tmpl['label']]) is not str:
                            #print ("{} type doesn't match.".format(tmpl['label']))
                            user_inputs_ok = False
                        
                    elif (tmpl['type'].lower() == 'checklist'):
                        if type(user_inputs_list[0][tmpl['label']]) is not dict:
                            user_inputs_ok = False
                            
            if not user_inputs_ok:
                infostr = ("The siltlabels file does not match the "
                           "current template and cannot be loaded. "
                           "If you continue with this template your "
                           "file may be overwritten.")
                ret = self._showDialogBox(title = "Error: Siltlabels",
                                           message = "Error loading siltlabels file.",
                                           more_info = infostr)
                return
            
            # Get the list of overlay items from the saved siltlabels file
            saved_label_items_list = [
                {'label_item_type': l[label_item_type_key], 
                 'label_item_vertices': l[label_item_vertices_key],
                 'label_item_uuid': l[label_item_uuid_key]}
                for l in label_list]
                
            # Set up the previous inputs
            self.central_widget.setSavedInputs(user_inputs_list, saved_label_items_list)
    
    
    def _save(self):
        # Get all of the user inputs from the multi-input
        # panel
        self.updateStatusBar("Saving...")
        
        # Check template file to see if we want to save the
        # overlay item fill pixels or bounding rect
        get_label_item_pixels = False
        get_label_item_brect = False
        if self.outputs_options_dict is not None:
            if ('include_mask' in self.outputs_options_dict.keys() and
                self.outputs_options_dict['include_mask'] == 'true'):
                get_label_item_pixels = True
            if ('include_bounding_rect' in self.outputs_options_dict.keys() and
                self.outputs_options_dict['include_bounding_rect'] == 'true'):
                get_label_item_brect = True
        
        # Get the full outputs dictionary
        outputs_dict = self._getOutputDict(get_label_item_pixels=get_label_item_pixels,
                                           get_label_item_brect=get_label_item_brect)
        
        with open(self.save_path, 'w') as fid:
            json.dump(outputs_dict, fid, indent=2)
        
        self.undo_stack_index = self.undo_stack.index()
        
        self.updateStatusBar("Saved labels to {}".format(self.save_path))

        # If we're in series mode, update the background color
        # of the list item
        if self.series_mode:
            it = self.central_widget.series_selection_widget.findItems(
                self.image_file, Qt.MatchFixedString)[0]
            it.setBackground(QBrush(QColor(205, 240, 205, 255)))
        
    
    def _saveasAction(self):
        """Menu action to save a file.
        """
        options = QFileDialog.Options()
        filename = QFileDialog.getSaveFileName(self, 'Save file', "", 
                                               "siltlabels files (*siltlabels.json)", 
                                               options=options)[0]
        if filename == '':
            return

        if not filename.endswith('.siltlabels.json'):
            filename += ".siltlabels.json"
        
        self.save_path = filename
        self._save()
    
    
    def _getOutputDict(self,
                       get_label_item_pixels: bool = False,
                       get_label_item_brect: bool = False):

        # Get all of the inputs from the side panels and from
        # the overlay widget
        all_inputs_list = self.central_widget.getInputs(
            get_label_item_pixels=get_label_item_pixels,
            get_label_item_brect=get_label_item_brect)

        # Add the silt_version key AND
        # round the vertex locations to the nearest 100th
        for label_item in all_inputs_list:
            label_item['silt_version'] = importlib.metadata.version("silt")
            
            verts = []
            for i in range(len(label_item['label_item_vertices'])):
                verts.append(
                    [round(vert, 2) for vert in label_item['label_item_vertices'][i]])
            label_item['label_item_vertices'] = verts

        # If there's geo info included in the image, then convert
        # the pixel vertex locations to lon, lat
        if self.geo_transform is not None:
            geo_transform_key = 'geo_transform'
            geo_vertices_key = 'geo_vertices'
            if self.outputs_options_dict is not None:
                if ('geo_transform' in
                    self.outputs_options_dict['default_output_keys'].keys()):
                    geo_transform_key = (self.outputs_options_dict[
                        'default_output_keys']['geo_transform'])
                if ('geo_vertices' in
                    self.outputs_options_dict['default_output_keys'].keys()):
                    geo_vertices_key = (self.outputs_options_dict[
                        'default_output_keys']['geo_vertices'])
                    
            for label_item in all_inputs_list:
                verts = np.array(label_item['label_item_vertices'])
                tmp = np.concatenate((verts+0.5, np.ones((verts.shape[0], 1))), axis=1)
                lonlats = np.matmul(self.geo_transform, tmp.transpose())
                lonlatlist = lonlats.transpose()[:, :2].tolist()
                label_item[geo_transform_key] = self.geo_transform.tolist()
                label_item[geo_vertices_key] = lonlatlist
                
        
        # If the user opted to override the default keys for
        # 'label_item_vertices' and/or 'label_item_uuid,'
        # then replace those keys appropriately
        if self.outputs_options_dict is not None:
            if ('default_output_keys' in self.outputs_options_dict.keys()):
                # Switch out label_item_uuid for custom key
                if ('label_item_uuid' in self.outputs_options_dict['default_output_keys'].keys()):
                    newkey = self.outputs_options_dict['default_output_keys']['label_item_uuid']
                    for label_item in all_inputs_list:
                        label_item[newkey] = label_item.pop('label_item_uuid')
                
                # Swap out label_item_vertices for custom key
                if ('label_item_vertices' in self.outputs_options_dict['default_output_keys'].keys()):
                    newkey = self.outputs_options_dict['default_output_keys']['label_item_vertices']
                    for label_item in all_inputs_list:
                        label_item[newkey] = label_item.pop('label_item_vertices')
        
        # Add the image_filename to the output dict
        outputs_dict = self._addImageInfoToOutputDict(all_inputs_list)
        
        return outputs_dict
    
    
    def _addImageInfoToOutputDict(self, inputs_list):
        
        image_filename_key = 'image_filename'
        if self.outputs_options_dict is not None:
            if ('default_output_keys' in self.outputs_options_dict.keys()):
                if ('image_filename' in self.outputs_options_dict['default_output_keys'].keys()):
                    image_filename_key = self.outputs_options_dict['default_output_keys']['image_filename']
        
        for inp in inputs_list:
            inp[image_filename_key] = os.path.basename(self.image_file)
        
        return(inputs_list)
    
        
    def _saveMask(self):
        
        self.updateStatusBar("Generating image mask...")
        
        # ADD THE FULL IMAGE MASK if it was asked for in the template
        keys = [t['label'] for t in self.template_list]
        
        # If the value for the mask label isn't in the template...
        if not self.outputs_options_dict['mask_label'] in keys:
            infostr = ("Please make sure your "
                       "template file includes the \'mask_label\' key, "
                       "which determines which labels to assign to the "
                       "mask.")
            ret = self._showDialogBox(title = "Error: Template",
                                       message = ("Template file missing "
                                                  "the mask_label key."),
                                       more_info = infostr)
            """
            err_box = QMessageBox()
            err_box.setIcon(QMessageBox.Warning)
            err_box.setText("Template file missing the mask_label key.")
            err_box.setInformativeText("Please make sure your \
            template file includes the \'mask_label\' key, which \
            determines which labels to assign to the mask.")
            err_box.setWindowTitle("Error")
            err_box.setStandardButtons(QMessageBox.Ok)
            err_box.exec_()
            """
            return
        
        # Get the index of the input in the template list
        mask_label = self.outputs_options_dict['mask_label']
        ind = keys.index(mask_label)
        
        # Can only work with comboboxes for now - sorry!
        if self.template_list[ind]['type'] != 'combobox':
            return
        
        opts = self.template_list[ind]['options']
        
        # Create dictionary for converting options to integers
        opts_to_ints = dict()
        for i in range(len(opts)):
            opts_to_ints[opts[i]] = int(i)
        
        # Create the mask for the whole image
        mask = np.ones(self.image_size[:2])*(-1)
        
        # Get the covered pixels
        inputs_list = self.central_widget.getCoveredPixels()
        
        # Go through the inputs, adding the integer opts to the mask
        for inp in inputs_list:
            xs = np.array([i[0] for i in inp['label_item_pixels']])
            ys = np.array([i[1] for i in inp['label_item_pixels']])
            mask[ys, xs] = opts_to_ints[inp[mask_label]]
            
        
        # Open file and save mask
        mask_file = os.path.splitext(os.path.splitext(self.save_path)[0])[0] + ".siltmask.csv"
        np.savetxt(mask_file, mask.astype(int), delimiter=',')
        
        self.updateStatusBar('')
    
    
    # ***************************************** #
    # OVERLAY I/O
    # ***************************************** #
    def _openOverlayAction(self):
        """Menu action to open an overlay file.
        """
        # Update status bar message
        self.updateStatusBar("Opening overlay...")
        
        # Show the file dialog
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, 'Open Overlay', "",
            "Overlay files (*.json)", options=options)[0]
        if filename == '':
            return
        
        # Actually open the overlay file
        ret = self._openOverlay(filename)
        if ret == -1:
            return
        
        # Update status bar message
        self.updateStatusBar("Opened overlay {}".format(filename))
    
    
    def _openOverlay(self, filename):
        """Open an overlay file.
        
        Overlay files are json files.  They contain a list of
        dictionaries.  Each dictionary must have the following
        entry:
            ``vertices``
                A list of (x, y) vertex coordinates
        
        Each dictionary may also optionally set the following
        formatting options:
            ``color``
                A length-4 integer list defining RGBA values.
                Values must be between 0 and 255, inclusive.
            ``style``
                A string for the line style.  Options are
                {'solid', 'dashed', 'dotted'}.
            ``line_width``
                An integer which sets the width of the line
                segment overlay, in pixels.
        """
        
        # Read the overlay json file
        overlay_list = None
        with open(filename, 'r') as fid:
            overlay_list = json.load(fid)
        
        # Show warning box for read errors
        if overlay_list is None or overlay_list == []:
            infostr = "Cannot read overlay file. Please check format."
            ret = self._showDialogBox(title = "Error: Overlay",
                                       message = "Error loading overlay file.",
                                       more_info = infostr)
            return
        
        # Close the previous overlay
        ret = self._closeOverlay()
        if ret == -1:
            infostr = "Cannot close previous overlay."
            ret = self._showDialogBox(title = "Error: Overlay",
                                       message = "Error closing overlay.",
                                       more_info = infostr)
            return
        
        # Set the overlay
        label_item_vertices_key = None
        if self.outputs_options_dict is not None:
            if ('default_output_keys' in self.outputs_options_dict.keys()):
                if ('label_item_vertices' in self.outputs_options_dict['default_output_keys'].keys()):
                    label_item_vertices_key = self.outputs_options_dict['default_output_keys']['label_item_vertices']
        
        ret = self.central_widget.setListOverlay(overlay_list,
                                                 label_item_vertices_key)
        if ret == -1:
            infostr = ("One or more overlay items missing required "
                       "'vertices' or 'overlay_item_vertices' key.")
            ret = self._showDialogBox(title = "Warning: Overlay",
                                       message = "Missing required key",
                                       more_info = infostr)
        
        # Enable the close overlay option
        self.close_overlay_act.setEnabled(True)
        
        # Enable the hide/show overlay option
        self.show_overlay_act.setChecked(True)
        self.show_overlay_act.setEnabled(True)
        
        # Add the filename of the overlay to the side panel
        self.central_widget.addDisplayItem(label = "Overlay:",
                                           value = os.path.basename(filename),
                                           tooltip = os.path.abspath(filename))
        
        return 0
    
    
    def _closeOverlayAction(self):
        """Menu action to remove an overlay.
        """
        # Close the overlay
        ret = self._closeOverlay()
        if ret == -1:
            self.updateStatusBar("Cannot close overlay.")
            return
        
        # Update status bar
        self.updateStatusBar("Closed overlay.")
    
    
    def _closeOverlay(self):
        """Remove an overlay.
        """
        # Close the overlay
        #print ("Code to remove overlay goes here...")
        self.central_widget.clearOverlay()

        # Remove the overlay item from the side panel
        self.central_widget.removeDisplayItem("Overlay:")

        # Disable the close overlay option in the File menu
        self.close_overlay_act.setEnabled(False)

        # Disable the hide/show overlay option
        self.show_overlay_act.setEnabled(False)
        self.show_overlay_act.setChecked(False)

        return 0
    
    
    # ***************************************** #
    # OTHER MENU ACTIONS
    # ***************************************** #
    def _copyLabelItemsFromPreviousAction(self):
        """Edit menu action to copy all the overlay items 
        from the previous image in a series.
        """
        # Get the index of the current and previous files in the list
        current_ind = self.central_widget.series_selection_widget.currentRow()
        previous_ind = current_ind - 1
        #if previous_ind < 0:
        #    return
        
        # Iterate until you find the closest previous labels file
        while previous_ind >= 0:
            previous_img_file = str(self.central_widget.series_selection_widget.item(previous_ind).text())
            previous_labels_file = os.path.splitext(previous_img_file)[0]
            previous_labels_file += ".siltlabels.json"
            if os.path.isfile(previous_labels_file):
                break
            
            previous_ind -= 1
        
        if previous_ind < 0:
            return
        
        # Get the current output dictionary
        current_output_dict = self._getOutputDict(get_label_item_pixels=False,
                                                  get_label_item_brect=False)
        
        # Run the command to copy the overlay items
        cmd = commandCopyLabelItems(self, current_output_dict, previous_labels_file)
        self._undoStackPush(cmd)


    def _copyLabelItemsAction(self):
        """Edit menu action to copy all the overlay items
        from another image.
        """
        options = QFileDialog.Options()
        filename = QFileDialog.getOpenFileName(
            self, 'Copy Labels From...', os.path.dirname(self.save_path),
            "Label files (*.siltlabels.json)", options=options)[0]
        if filename == '':
            return
        
        # Get the current output dictionary
        current_output_dict = self._getOutputDict(get_label_item_pixels=False,
                                                  get_label_item_brect=False)
        cmd = commandCopyLabelItems(self, current_output_dict, filename)
        self._undoStackPush(cmd)
        
        
    def _showUUIDsAction(self, checked: bool):
        """Menu action to toggle whether or not the UUIDs
        are shown.
        """
        if checked:
            self.central_widget.showUUIDs(True)
        else:
            self.central_widget.showUUIDs(False)


    def _showOverlayAction(self, checked: bool):
        """Menu action to toggle whether or not the overlay is
        shown.
        """
        if checked:
            self.central_widget.showOverlay(True)
        else:
            self.central_widget.showOverlay(False)
        
    
    def _onAddPolygonAct(self):
        """Menu action to add a polygon.
        """
        self.central_widget.addPolygon()
    
    def _undoStackPush(self, command: QUndoCommand):
        """Push a command to the QUndoStack.
        """
        self.undo_stack.push(command)

    def _onAutoRangePressed(self):
        shadow, mid, highlight = self.central_widget.autoSetImageLevelsInBounds()
        self.levels_widget.setSliders(shadow, mid, highlight)
        
    def _exitAction(self):
        ret = self._closeImageAction()
        if ret == -1:
            return
        
        qApp.quit()
        
        
    def updateStatusBar(self, message: str):
        self.statusBar().showMessage(message)


    def _showDialogBox(self,
                        title: str,
                        message: str,
                        more_info: str = None,
                        box_type: str = "error"):
        dialog_box = QMessageBox()
        dialog_box.setWindowTitle(title)
        dialog_box.setText(message)
        
        if box_type == "error":
            dialog_box.setStandardButtons(QMessageBox.Ok)
            dialog_box.setDefaultButton(QMessageBox.Ok)
            dialog_box.setIcon(QMessageBox.Warning)
        elif box_type == "choice":
            dialog_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            dialog_box.setDefaultButton(QMessageBox.Yes)
            dialog_box.setIcon(QMessageBox.Question)

        if more_info is not None:
            dialog_box.setInformativeText(more_info)

        ret = dialog_box.exec_()

        return ret
    


class commandCopyLabelItems(QUndoCommand):
    """Class to control undo/redo of copying overlay items
    from another file.
    """

    def __init__(self, mainwindow, current_labels_list, filename, text="Copy overlay items", parent=None):
        super(commandCopyLabelItems, self).__init__(text, parent)
        self.mainwindow = mainwindow
        self.current_labels_list = current_labels_list
        self.filename = filename

    def redo(self):
        # Open the file containing the new labels
        # This function takes care of clearing the multi-input panel
        # and the image overlay items
        self.mainwindow._openSavedLabels(self.filename)

    def undo(self):
        # Clear the multi-input panel (if there are any inputs)
        self.mainwindow.central_widget.clearInputs()
        
        # Clear the image of overlay items (if there are any)
        self.mainwindow.central_widget.clearLabelItems()
        
        # Parse the labels and load them in the main widget
        self.mainwindow._parseLabelList(self.current_labels_list)


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    progress
        tuple(int,int) indicating progress index and total.

    finished
        No data

    '''
    progress = pyqtSignal(tuple)
    finished = pyqtSignal()


class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            self.fn(*self.args, **self.kwargs)
        except:
            raise ChildProcessError("Pyramid preprocessing failed")
        finally:
            self.signals.finished.emit()  # Done
