from PyQt5.QtWidgets import (QComboBox, QApplication, QStyledItemDelegate, QStyleOptionViewItem)
from PyQt5.QtCore import (Qt, pyqtSignal)
from PyQt5.QtGui import (QStandardItemModel, QStandardItem)
import sys

class CheckableComboBox(QComboBox):
    
    item_toggled = pyqtSignal(int, Qt.CheckState)
    
    def __init__(self, parent=None):
        super(CheckableComboBox, self).__init__(parent)
        
        delegate = QStyledItemDelegate(self)
        self.setItemDelegate(delegate)
        
        self.view().pressed.connect(self._onItemPressed)
        
    def _onItemPressed(self, index):
        #self.setFocus()
        item = self.model().itemFromIndex(index)
        if item.checkState() == Qt.Checked:
            #print ("Item {} now uncheched.".format(index))
            item.setCheckState(Qt.Unchecked)
            #self.item_toggled.emit(item.row(), Qt.Unchecked)
        else:
            #print ("Item {} now checked.".format(index))
            item.setCheckState(Qt.Checked)
            #self.item_toggled.emit(item.row(), Qt.Checked)
    
    
    def setAllCheckable(self):
        """Make all items in the list checkable.
        """
        for i in range(self.count()):
            #self.model().item(i, 0).setCheckable(True)
            
            self.model().item(i, 0).setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            self.model().item(i, 0).setData(Qt.Unchecked, Qt.CheckStateRole)
    
    def setAllUnchecked(self):
        """Set all items as unchecked.
        """
        for i in range(self.count()):
            self.setUnchecked(i)
    
    def setAllChecked(self):
        """Set all items as checked.
        """
        for i in range(self.count()):
            self.setChecked(i)
    
    def setChecked(self, index):
        """Check the item at the given index.
        """
        item = self.model().item(index, 0)
        item.setCheckState(Qt.Checked)
    
    def setUnchecked(self, index):
        """Uncheck the item at the given index.
        """
        item = self.model().item(index, 0)
        item.setCheckState(Qt.Unchecked)

    def setItemCheckstate(self, index, checkstate):
        """Check or uncheck the item at the given index according
        to checkstate.
        """
        item = self.model().item(index, 0)
        item.setCheckState(checkstate)
    
    def isChecked(self, index):
        """Check whether the item at the given index is checked.
        """
        item = self.model().item(index, 0)
        if item.checkState() == Qt.Checked:
            return True
        else:
            return False
    
    def getText(self, index) -> str:
        """Get the text at the given index.
        """
        item = self.model().item(index, 0)
        return item.text()
    
    def getCheckedItems(self) -> list:
        """Get the list of strings for all checked items.
        """
        checked = []
        for i in range(self.count()):
            if self.isChecked(i):
                checked.append(self.getText(i))

        return checked

    def getCheckedUncheckedDict(self) -> dict:
        """Fill a dictionary with all the strings in the list
        as keys and the corresponding checked/unchecked state
        set to true/false as the values.
        """
        checked_dict = {}
        for i in range(self.count()):
            if self.isChecked(i):
                checked_dict[self.getText(i)] = "true"
            else:
                checked_dict[self.getText(i)] = "false"
        
        return checked_dict


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = CheckableComboBox()
    ex.addItems(['one', 'two'])
    ex.show()
    ex.setAllCheckable()
    app.exec_()
    app.quit()
