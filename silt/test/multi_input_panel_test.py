import pytest

from PyQt5.QtWidgets import QLabel, QLineEdit, QComboBox
from PyQt5.QtCore import Qt

from silt import multi_input_panel, checkable_combobox_widget


class TestInputRow:

    @pytest.fixture()
    def inputRow(self, qtbot):
        widget = multi_input_panel.InputRow()
        qtbot.addWidget(widget)
        return widget

    @pytest.fixture()
    def template_list(self):
        """
        Test data for template
        """
        list_dict = [
            {
                "type": "combobox",
                "label": "Class",
                "options": ["Building", "Park", "Road"],
            },
            {
                "type": "checklist",
                "label": "Subclass",
                "options": ["Residential", "Commercial", "Public", "Private"],
                "tooltip": "Select all that apply.",
            },
            {"type": "lineedit", "label": "Notes"},
        ]

        return list_dict

    @pytest.fixture()
    def input_dicts(self):
        """
        input_dicts test data, corresponds to template_list
        """
        input_dicts = {
            "Class": "Building",
            "Subclass": {
                "Commercial": "false",
                "Private": "false",
                "Public": "false",
                "Residential": "false",
            },
            "Notes": "",
        }
        return input_dicts

    def test_setTemplate(self, inputRow, mocker):
        """
        Test that a given template is set properly.
        """
        mocker.patch(
            "silt.multi_input_panel.InputRow.parseTemplateList",
            return_value=(
                [QLabel("label_1"), QLabel("label_2"), QLabel("label_3")],
                [QComboBox(), QComboBox(), QLineEdit()],
                [],
            ),
        )

        dummy_template_list = {}

        inputRow.setTemplate(dummy_template_list)

        # Assert that the correct number of columns are present
        assert inputRow.layout.columnCount() == 3

        # Assert that the widgets contain the correct labels and widgets
        assert isinstance(inputRow.layout.itemAtPosition(1, 0).widget(), QLabel)
        assert isinstance(inputRow.layout.itemAtPosition(2, 0).widget(), QComboBox)
        assert isinstance(inputRow.layout.itemAtPosition(1, 1).widget(), QLabel)
        assert isinstance(inputRow.layout.itemAtPosition(2, 1).widget(), QComboBox)
        assert isinstance(inputRow.layout.itemAtPosition(1, 2).widget(), QLabel)
        assert isinstance(inputRow.layout.itemAtPosition(2, 2).widget(), QLineEdit)

        assert inputRow.layout.itemAtPosition(1, 0).widget().text() == "label_1"
        assert inputRow.layout.itemAtPosition(1, 1).widget().text() == "label_2"
        assert inputRow.layout.itemAtPosition(1, 2).widget().text() == "label_3"

    def test_parseTemplateList(self, inputRow, template_list, input_dicts):
        """
        Test that the template dictionary is correctly parsed
        """
        input_labels, input_widgets, current_inputs = inputRow.parseTemplateList(
            template_list
        )

        assert len(input_labels) == len(input_widgets) == len(current_inputs) == 3

        keys = [*input_dicts]
        for i in range(len(keys)):
            # Assert labels and current inputs correspond to template
            assert input_labels[i].text() == keys[i]

            assert current_inputs[i] == input_dicts[keys[i]]

        # Assert widget types are correct
        assert isinstance(input_widgets[0], QComboBox)
        assert isinstance(input_widgets[1], checkable_combobox_widget.CheckableComboBox)
        assert isinstance(input_widgets[2], QLineEdit)

    def test_setInputs(self, inputRow, template_list, input_dicts):
        """
        test that input defaults are correctly setup
        """
        # Set to true to make things interesting
        input_dicts["Subclass"]["Private"] = "true"

        # setInputs depends on setTemplate having been called first
        inputRow.setTemplate(template_list)
        inputRow.setInputs(input_dicts)

        # test that combobox widget input is correct
        assert inputRow.input_widgets[0].currentIndex() == 0

        # test that checklist widgets inputs are correct
        commercial_ind = inputRow.input_widgets[1].findText(
            "Commercial", Qt.MatchFixedString
        )
        private_ind = inputRow.input_widgets[1].findText("Private", Qt.MatchFixedString)
        public_ind = inputRow.input_widgets[1].findText("Public", Qt.MatchFixedString)
        residential_ind = inputRow.input_widgets[1].findText(
            "Residential", Qt.MatchFixedString
        )

        assert (
            inputRow.input_widgets[1].model().item(commercial_ind, 0).checkState()
            == Qt.Unchecked
        )
        assert (
            inputRow.input_widgets[1].model().item(private_ind, 0).checkState()
            == Qt.Checked
        )
        assert (
            inputRow.input_widgets[1].model().item(public_ind, 0).checkState()
            == Qt.Unchecked
        )
        assert (
            inputRow.input_widgets[1].model().item(residential_ind, 0).checkState()
            == Qt.Unchecked
        )

        # test that lineedit widget input is correct
        assert inputRow.input_widgets[2].text() == ""

    def test_getInputs(self, inputRow, template_list, input_dicts):
        """
        Test that the user inputs are retrieved correctly
        """
        # Depends on setTemplate having been called first
        inputRow.setTemplate(template_list)

        user_inputs = inputRow.getInputs()

        assert user_inputs == input_dicts
