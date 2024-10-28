import pytest

from PyQt5.QtCore import Qt

from silt import checkable_combobox_widget


class TestCheckableComboboxWidget:

    @pytest.fixture()
    def checkableComboBox(self, qtbot):
        widget = checkable_combobox_widget.CheckableComboBox()
        widget.addItems(["one", "two"])
        qtbot.addWidget(widget)
        return widget

    @pytest.mark.parametrize("index", [0, 1])
    def test_onItemPressed(self, checkableComboBox, index):
        """
        Directly test checkbox press, as if being pressed by user
        """
        # Press box at index 0
        checkableComboBox._onItemPressed(
            checkableComboBox.model().item(index, 0).index()
        )

        # Ensure item 0 is checked now
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Checked

        # Press box at index 0 again
        checkableComboBox._onItemPressed(
            checkableComboBox.model().item(index, 0).index()
        )

        # Ensure item 0 is not checked
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Unchecked

    def test_setAllCheckable(self, checkableComboBox):
        """
        Test if all items are checkable when setAllCheckable() is called
        """
        checkableComboBox.setAllCheckable()

        # Assert that items in the list are checkable
        assert checkableComboBox.model().item(0, 0).isCheckable()
        assert checkableComboBox.model().item(1, 0).isCheckable()

        # Assert items are enabled
        assert checkableComboBox.model().item(0, 0).isEnabled()
        assert checkableComboBox.model().item(1, 0).isEnabled()

        # Assert items are unchecked
        assert checkableComboBox.model().item(0, 0).checkState() == Qt.Unchecked
        assert checkableComboBox.model().item(1, 0).checkState() == Qt.Unchecked

    @pytest.mark.parametrize("index", [0, 1])
    def test_setAllUnchecked(self, checkableComboBox, index):
        """
        Test if all items are unchecked when setAllUnchecked() is called
        """
        checkableComboBox.setAllUnchecked()

        # Assert that all items are unchecked
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Unchecked

    @pytest.mark.parametrize("index", [0, 1])
    def test_setAllChecked(self, checkableComboBox, index):
        """
        Test if all items are checked when setAllChecked() is called
        """
        checkableComboBox.setAllChecked()

        # Assert that all items are checked
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Checked

    @pytest.mark.parametrize("index", [0, 1])
    def test_setChecked(self, checkableComboBox, index):
        """
        Test if the item at the given index is checked
        """
        # Check item at index
        checkableComboBox.setChecked(index)

        # Assert item at index is checked
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Checked

    @pytest.mark.parametrize("index", [0, 1])
    def test_setUnchecked(self, checkableComboBox, index):
        """
        Test if the item at the given index is unchecked
        """
        # Uncheck item at index
        checkableComboBox.setUnchecked(index)

        # Assert item at index is checked
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Unchecked

    @pytest.mark.parametrize("index", [0, 1])
    def test_setItemCheckstate(self, checkableComboBox, index):
        """
        Test if the item at the given index is checked or unchecked according to check state
        """
        # Check item at index
        checkableComboBox.setItemCheckstate(index, Qt.Checked)
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Checked

        # Uncheck item at index
        checkableComboBox.setItemCheckstate(index, Qt.Unchecked)
        assert checkableComboBox.model().item(index, 0).checkState() == Qt.Unchecked

    @pytest.mark.parametrize("index", [0, 1])
    def test_isChecked(self, checkableComboBox, index):
        """
        Test if the item at the given index is checked
        """
        # Test if index is checked
        assert checkableComboBox.isChecked(index) == False

        # Check index
        checkableComboBox.model().item(index, 0).setCheckState(Qt.Checked)
        assert checkableComboBox.isChecked(index) == True

    @pytest.mark.parametrize("index, value", [(0, "one"), (1, "two")])
    def test_getText(self, checkableComboBox, index, value):
        """
        Test if the text at the given index is correct
        """
        # Get text at index
        text = checkableComboBox.getText(index)

        assert text == value

    @pytest.mark.parametrize("index, value", [(0, "one"), (1, "two")])
    def test_getCheckedItems(self, checkableComboBox, index, value):
        """
        Test if the list of strings for all checked items is correct
        """
        # Check item
        checkableComboBox.model().item(index, 0).setCheckState(Qt.Checked)

        # Get list of strings
        checked_items = checkableComboBox.getCheckedItems()

        # Assert the length is 1 and the item is equal to value
        assert len(checked_items) == 1
        assert checked_items[0] == value

    def test_getCheckedUncheckedDict(self, checkableComboBox):
        """
        Test if created dictionary has correct keys/values
        """
        # Check item 1
        checkableComboBox.model().item(1, 0).setCheckState(Qt.Checked)

        # Get dictionary
        checked_dict = checkableComboBox.getCheckedUncheckedDict()

        # Assert dict contains correct items
        keys = list(checked_dict.keys())
        values = list(checked_dict.values())
        assert keys[0] == "one"
        assert keys[1] == "two"
        assert values[0] == "false"
        assert values[1] == "true"
