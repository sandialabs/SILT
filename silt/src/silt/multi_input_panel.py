#################################################################
# Sandia National Labs
# Date: 11-08-2021
# Author: Kelsie Larson
# Department: 06321
# Contact: kmlarso@sandia.gov
#
# Class definitions for MultiInputPanel, InputRow, and
# DisplayItem
#################################################################

import sys
from PyQt5.QtWidgets import (QWidget, QScrollArea, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QSplitter,
                             QLabel, QLineEdit,
                             QComboBox, QGroupBox, QUndoCommand)
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from .checkable_combobox_widget import CheckableComboBox


class MultiInputPanel(QScrollArea):
    """This is the widget that is affected by the chosen template.
    It controls user inputs.
    """
    
    current_widget = -1
    command_added = pyqtSignal(QUndoCommand)
    multi_input_panel_selection_changed = pyqtSignal(int)
    
    def __init__(self, template_list=None, parent=None):
        """Initialize the template/user input area.
        """
        
        super(MultiInputPanel, self).__init__(parent)
        self.template_list = template_list
        self.rows = []
        self.display_items = []
        self.show_uuids_flag = True
        self._initUI()
    
    def _initUI(self):
        """Initialize the UI.
        """
        # Set up the layout.
        # We want the MultiPanelInput object to be a QWidget
        # with a QScrollArea inside it; thus we need a 
        # top-level layout to contain the QScrollArea.
        self.major_layout = QVBoxLayout(self)
        splitter = QSplitter(Qt.Vertical, self)

        # Set up display area to show info like template file and
        # image info
        display_scroll = QScrollArea(self)
        display_scroll.setWidgetResizable(True)
        
        self.display_info_gb = QGroupBox("File Information", self)
        self.display_info_layout = QVBoxLayout(self.display_info_gb)
        self.display_info_layout.insertStretch(-1)
        self.display_info_gb.setLayout(self.display_info_layout)

        display_scroll.setWidget(self.display_info_gb)

        # We want the MultiPanelInput object to be a QWidget
        # with a QScrollArea inside it.
        # We need a widget for the QScrollArea to act on
        # and to manage all the input rows.
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        
        self.row_manager_gb = QGroupBox("User Inputs", self)
        self.row_manager_layout = QVBoxLayout(self.row_manager_gb)
        self.row_manager_layout.insertStretch(-1)
        self.row_manager_gb.setLayout(self.row_manager_layout)
        
        self.scroll.setWidget(self.row_manager_gb)

        # Add the groupboxes to the major layout
        #self.major_layout.addWidget(display_scroll)
        #self.major_layout.addWidget(self.scroll)
        splitter.addWidget(display_scroll)
        splitter.addWidget(self.scroll)
        splitter.setSizes([200, 800])
        
        self.major_layout.addWidget(splitter)
        self.setLayout(self.major_layout)
        
    def setTemplate(self, template_list: list):
        """Sets the global template for the panel.
        """
        self.template_list = template_list

    def addDisplayItem(self, label: str, value: str, tooltip: str = None):
        """Adds a label/value pair to the display area.  This is 
        for info like displaying template filename and image 
        metadata.
        """
        new_item = DisplayItem(label=label, value=value,
                               tooltip=tooltip,
                               parent=self.display_info_gb)
        index = len(self.display_items)
        self.display_items.append(new_item)
        self.display_info_layout.insertWidget(index, new_item)
        self.display_info_gb.setLayout(self.display_info_layout)
    
    
    def count(self) -> int:
        """Counts the number of items in the list.
        """
        return len(self.rows)


    def addNewRowWidget(self,
                        index: int = None,
                        entry: dict = None,
                        uuid: str  = ''):
        new_row = self.createNewRowWidget(entry, uuid)
        self.insertRowWidget(new_row, index)
        
        
    def createNewRowWidget(self,
                           entry: dict = None,
                           uuid: str = ''):
        # If the template isn't set, just return
        if self.template_list is None:
            print ("You don't have a template yet...")
            return
        
        # Create the new row with the set template
        new_row = InputRow(template_list=self.template_list,
                           inputs_dict = entry,
                           uuid=uuid,
                           show_uuid_flag=self.show_uuids_flag,
                           parent=self)
        
        # Connect the new_row widget to the command_added signal
        new_row.command_added.connect(self._onCommandAdded)
        
        # Connect the row to the selection slot
        new_row.is_selected.connect(self._onWidgetSelected)
        
        return new_row
        
    
    def insertRowWidget(self, row_item, index=None):
        """Insert input row widget at the given index.
        
        Parameters
        ----------
        row_item: InputRow
        index: int (optional)
        """
        
        if index is None:
            index = self.count()
            self.rows.append(row_item)
        else:
            self.rows.insert(index, row_item)
        
        self.rows[index].setParent(self.row_manager_gb)
        if self.show_uuids_flag:
            self.rows[index].showUUID()
        else:
            self.rows[index].hideUUID()
        
        # Add the new row to the row_manager
        self.row_manager_layout.insertWidget(index, row_item)
        self.row_manager_gb.setLayout(self.row_manager_layout)
        
    
    def removeWidget(self, index: int):
        """Delete row from the layout.
        """
        row = self.rows.pop(index)
        self.row_manager_layout.removeWidget(row)
        row.setParent(None)
        
        self.row_manager_gb.setLayout(self.row_manager_layout)
        self.current_widget = -1
        
        return row
    
    def getInputs(self):
        """Get the user inputs based on the template.
        
        Returns
        -------
        list
            A list of dictionaries - one list entry for each 
            input widget
        
        """
        # Iterate through the widget rows, collecting the user inputs
        # into a lit of dictionaries
        user_inputs = []
        for row in self.rows:
            user_inputs.append(row.getInputs())
        
        return user_inputs
    
    
    def setAllInputs(self, inputs_list):
        """Sets the user inputs for the entire image.
        
        Parameters
        ----------
        inputs_list: list of dict
            The list of dictionary inputs, one dictionary
            per input widget row.
        
        Notes
        -----
        This function should be used to load a previously 
        saved annotated image.
        """
        for entry in inputs_list:
            #self.addWidget()
            self.addNewRowWidget(index=None,
                                 entry=entry,
                                 uuid=entry['label_item_uuid'])
            #self.setWidgetInputs(index=-1, entry=entry)

    """
    def setWidgetInputs(self, index: int, entry: dict):
        #Sets the inputs for the row at the given index
        #to the values in entry.
        
        k = 0
        for tmpl in self.template_list:
            if tmpl['label'] in entry.keys():
                if tmpl['type'].lower() == 'lineedit':
                    self.rows[index].input_widgets[k].setText(
                        str(entry[tmpl['label']]))
                elif tmpl['type'].lower() == 'combobox':
                    ind = self.rows[index].input_widgets[k].findText(
                        entry[tmpl['label']], Qt.MatchFixedString)
                    self.rows[index].input_widgets[k].setCurrentIndex(ind)
            k += 1

        self.rows[index].setUUID(entry['label_item_uuid'])
    """ 
    
    def currentWidget(self) -> int:
        """Returns the index of the current active row widget.
        """
        for i in range(len(self.rows)):
            if self.rows[i].hasFocus():
                return (i)
        
        return -1
    
    def setCurrentWidget(self, index: int):
        """Sets the row widget at the index to have focus.
        """
        if index == -1:
            for row in self.rows:
                #row.clearFocus()
                row.clearHighlightedStyle()
                
        else:
            if self.current_widget != -1:
                self.rows[self.current_widget].clearHighlightedStyle()
            #self.rows[index].setFocus()
            self.rows[index].setHighlightedStyle()
            
            self.scroll.ensureWidgetVisible(self.rows[index])
        
        self.current_widget = index
        
    def clearWidgets(self):
        """Clear all of the input row widgets.
        """
        for i in range(self.count()):
            self.removeWidget(0)


    def clearDisplayItems(self):
        """Clear all display items.
        """
        for i in range(len(self.display_items)):
            display_item = self.display_items.pop(0)
            self.display_info_layout.removeWidget(display_item)
            display_item.setParent(None)

        self.display_info_gb.setLayout(self.display_info_layout)


    def removeDisplayItem(self, label: str):
        """Remove a display item.
        """
        index = 0
        for it in self.display_items:
            if it.label == label:
                break
            index += 1

        if index >= len(self.display_items):
            return

        display_item = self.display_items.pop(index)
        self.display_info_layout.removeWidget(display_item)
        display_item.setParent(None)

        self.display_info_gb.setLayout(self.display_info_layout)

    
    def showUUIDs(self, showbool=True):
        """Toggle the UUID display for each row
        """
        # Update the flag
        self.show_uuids_flag = showbool

        # Update all of the existing rows
        for i in range(len(self.rows)):
            if showbool:
                self.rows[i].showUUID()
            else:
                self.rows[i].hideUUID()
    
    
    #########
    # SLOTS #
    #########
    def _onCommandAdded(self, cmd):
        self.command_added.emit(cmd)

    def _onWidgetSelected(self):
        """When the selected row widget changes, emit a signal
        to tell which row is now selected.
        """
        index = -1
        for i in range(len(self.rows)):
            if self.rows[i].is_selected_flag:
                index = i
                self.rows[i].is_selected_flag = False
                
        if index != self.current_widget:
            self.setCurrentWidget(index)
            self.multi_input_panel_selection_changed.emit(index)
    
    
###################
# INPUT ROW CLASS #
###################
class InputRow(QWidget):
    """This is the widget that contains a single row of user 
    input widgets in the multi-input panel.
    """
    command_added = pyqtSignal(QUndoCommand)
    is_selected = pyqtSignal()
    
    def __init__(self,
                 template_list=None,
                 inputs_dict=None,
                 uuid='',
                 show_uuid_flag=False,
                 parent=None):
        """Initialize the input row.
        """
        
        super(InputRow, self).__init__(parent)
        self.template_list = template_list
        self.inputs_dict = inputs_dict
        self.uuid = uuid
        self.uuid_label = None
        self.show_uuid_flag = show_uuid_flag
        self.input_labels = None
        self.input_widgets = None
        self.is_selected_flag = False
        self._initUI()
    
    def _initUI(self):
        """Initialize the UI.
        """
        
        # Set the template for the widget
        if self.template_list is not None:
            self.setTemplate(self.template_list)

        if self.inputs_dict is not None:
            self.setInputs(self.inputs_dict)

        if self.show_uuid_flag:
            self.showUUID()
        
    
    def setTemplate(self, template_list):
        """Set the template.
        """
        self.input_labels, self.input_widgets, self.current_inputs = self.parseTemplateList(template_list)
        self.template_list = template_list
        
        self.layout = QGridLayout(self)
        l = 0
        k = 0
        widgets_per_row = 5
        while k < len(self.input_labels):
            if k > 0 and k%widgets_per_row == 0:
                l += 1
            
            self.layout.addWidget(self.input_labels[k], 1+(2*l), k%widgets_per_row, 1, 1)
            self.layout.addWidget(self.input_widgets[k], 2+(2*l), k%widgets_per_row, 1, 1)
            k += 1
            
            #if k%widgets_per_row == 0:
            #    l += 1

        self.next_row = 3+(2*l)
        self.num_cols = k
        self.setLayout(self.layout)
        
        #self.setFocusProxy(self.input_widgets[0])
        
    
    def parseTemplateList(self, template_list):
        """Parse the template dictionary into a series of
        input widgets.
        """
        
        if template_list is None or template_list == []:
            sys.exit("Attempted to parse empty template list.")
        
        input_widgets = []
        input_labels = []
        current_inputs = []
        
        # Prepare the input widgets using the template list
        for val in template_list:
            if str(val['type']).lower() == 'lineedit':
                input_widgets.append(QLineEdit(self))
                input_labels.append(QLabel(val['label'], self))
                
                # Store the current text (which should be empty)
                current_inputs.append(input_widgets[-1].text())
                
                # Connect the widget to tell when text is edited
                input_widgets[-1].textEdited.connect(self.onTextEdited)
                input_widgets[-1].installEventFilter(self)
                
            elif str(val['type']).lower() == 'combobox':
                
                input_widgets.append(QComboBox(self))
                
                input_widgets[-1].addItems(val['options'])
                input_labels.append(QLabel(val['label'], self))
                
                # Store the current selection
                current_inputs.append(input_widgets[-1].currentText())
                
                # Connect the widget to tell when the row selection changes
                input_widgets[-1].currentTextChanged.connect(self.onComboBoxChanged)
                input_widgets[-1].installEventFilter(self)

            elif str(val['type']).lower() == 'checklist':
                # Set up the checkable combobox widget and label
                input_widgets.append(CheckableComboBox(self))
                input_widgets[-1].addItems(val['options'])
                
                input_widgets[-1].setAllCheckable()
                
                input_widgets[-1].setAllUnchecked()
                input_widgets[-1].item_toggled.connect(self.onCheckableComboBoxChanged)
                input_labels.append(QLabel(val['label'], self))
                
                # Store the current inputs
                current_inputs.append(input_widgets[-1].getCheckedUncheckedDict())
                
                # Connect the widget to tell when the row
                # selection changes
                input_widgets[-1].installEventFilter(self)
            
            else:
                print ("WARNING: Unrecognized input in template list:\n{}".format(val['type']))
                continue
                
            if 'tooltip' in list(val.keys()):
                input_widgets[-1].setToolTip(val['tooltip'])
            
        return (input_labels, input_widgets, current_inputs)


    def setInputs(self, 
                  inputs_dict: dict):
        for k, tmpl in enumerate(self.template_list):
            if tmpl['label'] in inputs_dict.keys():
                if tmpl['type'].lower() == 'lineedit':
                    self.input_widgets[k].setText(
                        str(inputs_dict[tmpl['label']]))
                elif tmpl['type'].lower() == 'combobox':
                    ind = self.input_widgets[k].findText(
                        inputs_dict[tmpl['label']], Qt.MatchFixedString)
                    self.input_widgets[k].setCurrentIndex(ind)
                elif tmpl['type'].lower() == 'checklist':
                    dt = inputs_dict[tmpl['label']]
                    for key in dt.keys():
                        ind = self.input_widgets[k].findText(key, Qt.MatchFixedString)
                        if dt[key] == 'true':
                            self.input_widgets[k].setChecked(ind)
                        else:
                            self.input_widgets[k].setUnchecked(ind)
                            
                    #checked_inds = [self.input_widgets[k].findText(
                    #    j, Qt.MatchFixedString) for j in inputs_dict[tmpl['label']]]
                    #for i in checked_inds:
                    #    self.input_widgets[k].setChecked(i)

    
    def setUUID(self, uuid: str):
        """Sets the UUID for this row widget and updates the 
        QLabel if necessary.
        """
        self.uuid = uuid
        if self.show_uuid_flag:
            self.updateUUIDLabel()
    

    def showUUID(self):
        """Shows the UUID by adding a QLabel widget to the next
        row in the layout.
        """
        self.show_uuid_flag = True
        if self.uuid_label is None:
            self.uuid_label = QLabel(self.uuid, self)
            self.uuid_label.setToolTip('The UUID (unique identifier) for this annotation.')
            self.uuid_label.setStyleSheet("QLabel { color: gray }")
            self.layout.addWidget(self.uuid_label, self.next_row, 0, 1, self.num_cols)
            self.setLayout(self.layout)


    def updateUUIDLabel(self):
        """Updates the UUID QLabel.
        """
        self.uuid_label.setText(self.uuid)
        self.setLayout(self.layout)
    
    
    def hideUUID(self):
        """Removes the UUID QLabel from the layout if it exists.
        """
        self.show_uuid_flag = False
        if self.uuid_label is not None:
            self.uuid_label.setParent(None)
            self.uuid_label = None
            self.setLayout(self.layout)
    
    
    def getInputs(self):
        """Public function to get the user inputs.
        """
        
        if self.input_widgets is None:
            sys.exit("Attempt to read input before template is set.")
        
        user_inputs = dict()
        i = -1
        for val in self.template_list:
            i += 1
            if str(val['type']).lower() == 'lineedit':
                user_inputs[str(val['label'])] = str(self.input_widgets[i].text())
            elif str(val['type']).lower() == 'combobox':
                user_inputs[str(val['label'])] = str(self.input_widgets[i].currentText())
            elif str(val['type']).lower() == 'checklist':
                user_inputs[str(val['label'])] = self.input_widgets[i].getCheckedUncheckedDict()
            else:
                continue
        
        return user_inputs
    
    
    def setHighlightedStyle(self):
        """Function to set the style when selected.
        """
        self.setStyleSheet("QLineEdit { background-color: #C3DBFF } \
        QComboBox { background-color: #C3DBFF } \
        QLabel { font-weight: bold }")
    
    def clearHighlightedStyle(self):
        """Function to clear the selected style.
        """
        self.setStyleSheet("QWidget { }")
    
    
    def onTextEdited(self, new_text):
        for i in range(len(self.input_widgets)):
            if self.input_widgets[i].hasFocus():
                
                # Get the previous text
                prev_text = self.current_inputs[i]
                
                # Create the undo command & push to stack
                cmd = commandTextChanged(self.input_widgets[i], prev_text, new_text)
                self.command_added.emit(cmd)
                
                # Update the previous text to be the new text
                self.current_inputs[i] = new_text
                break
    
    
    def onComboBoxChanged(self, new_text):
        for i in range(len(self.input_widgets)):
            if self.input_widgets[i].hasFocus():
                
                # Get the previous text
                prev_text = self.current_inputs[i]
                
                # Create the undo command & push to stack
                cmd = commandComboBoxChanged(self.input_widgets[i], prev_text, new_text)
                self.command_added.emit(cmd)
                
                # Update the previous selection to be the current selection
                self.current_inputs[i] = new_text
                break
    
    
    def onCheckableComboBoxChanged(self, index, new_checkstate):
        for i in range(len(self.input_widgets)):
            if self.input_widgets[i].hasFocus():
                # Get the previous checkstate
                if new_checkstate == Qt.Unchecked:
                    self.current_inputs[i][self.input_widgets[i].getText(index)] = "false"
                    prev_checkstate = Qt.Checked
                else:
                    self.current_inputs[i][self.input_widgets[i].getText(index)] = "true"
                    prev_checkstate = Qt.Unchecked

                # Create undo command and push to stack
                cmd = commandCheckableComboBoxChanged(
                    self.input_widgets[i], index, prev_checkstate, new_checkstate)
                self.command_added.emit(cmd)

                break
    
    def mousePressEvent(self, mouse_event):
        """Reimplement mousePressEvent to track which widget is selected.
        """
        self.mouse_press_flag = True
        super().mousePressEvent(mouse_event)
        
    def mouseReleaseEvent(self, mouse_event):
        """Reimplement mouseReleaseEvent to track which widget is
        selected.
        """
        if self.mouse_press_flag:
            self.is_selected_flag = True
            self.is_selected.emit()
        self.mouse_press_flag = False
        super().mouseReleaseEvent(mouse_event)
        
    def eventFilter(self, obj, event):
        """Filter for mouse clicks and releases on the combobox
        and lineedit user inputs so that we can change selection
        based on these interactions.
        """
        if event.type() == QEvent.MouseButtonPress:
            self.is_selected_flag = True
            self.is_selected.emit()
            
        # Allow the mouse events to continue to the application
        return False

    
######################
# DISPLAY ITEM CLASS #
######################
class DisplayItem(QWidget):
    def __init__(self, label=None, value=None, tooltip=None, parent=None):
        """Initialize the row widget.
        """
        super(DisplayItem, self).__init__(parent)
        self.label = label
        self.value = value
        self.tooltip = tooltip
        self._initUI()
    
    def _initUI(self):
        """Initialize the UI.
        """
        layout = QHBoxLayout(self)
        label_widget = QLabel(self.label, self)
        value_widget = QLabel(self.value, self)
        if self.tooltip is not None:
            value_widget.setToolTip(self.tooltip)
        
        layout.addWidget(label_widget)
        layout.addWidget(value_widget)
        self.setLayout(layout)


############################################################
# QUndoCommand Subclasses
############################################################
class commandTextChanged(QUndoCommand):
    """Class to control undo/redo of text changing
    in a lineedit input.
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.
    """
    def __init__(self, input_widget, prev_text, new_text, text="Text input changed", parent=None):
        super(commandTextChanged, self).__init__(text, parent)
        self.input_widget = input_widget
        self.prev_text = prev_text
        self.new_text = new_text
        self.undone_flag = False
    
    def redo(self):
        if self.undone_flag:
            self.input_widget.setText(self.new_text)
        
    def undo(self):
        self.input_widget.setText(self.prev_text)
        self.undone_flag = True


class commandComboBoxChanged(QUndoCommand):
    """Class to control undo/redo of combobox selection
    changing.
    
    Notes
    -----
    When the command is first pushed onto the undo stack,
    its redo() function is called.
    """
    def __init__(self, input_widget, prev_text, new_text, text="Drop-down input changed", parent=None):
        super(commandComboBoxChanged, self).__init__(text, parent)
        self.input_widget = input_widget
        self.prev_text = prev_text
        self.new_text = new_text
        self.undone_flag = False
    
    def redo(self):
        if self.undone_flag:
            self.input_widget.setCurrentText(self.new_text)
        
    def undo(self):
        self.input_widget.setCurrentText(self.prev_text)
        self.undone_flag = True


class commandCheckableComboBoxChanged(QUndoCommand):
    """Class to control undo/redo of checkable combobox selection.
    
    Notes
    -----
    When the command is first pushed onto the undo stack, its
    redo() function is called.
    """
    def __init__(self, input_widget, index, prev_checkstate, new_checkstate, text="Checklist item toggled", parent=None):
        super(commandCheckableComboBoxChanged, self).__init__(text, parent)
        self.input_widget = input_widget
        self.index = index
        self.prev_checkstate = prev_checkstate
        self.new_checkstate = new_checkstate
        self.undone_flag = False

    def redo(self):
        if self.undone_flag:
            self.input_widget.setItemCheckstate(self.index, self.new_checkstate)
            self.input_widget.setCurrentIndex(self.index)

    def undo(self):
        self.input_widget.setItemCheckstate(self.index, self.prev_checkstate)
        self.undone_flag = True
        
