
'''
A very simple GUI for the snutree program. Advanced features are available in
the CLI version of the program.
'''

import sys
import csv
import logging
from itertools import count
from contextlib import ExitStack
from io import StringIO
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QIntValidator,
    )
from PyQt5.QtWidgets import (
        QAbstractItemView,
        QApplication,
        QComboBox,
        QDesktopWidget,
        QErrorMessage,
        QFileDialog,
        QGridLayout,
        QLabel,
        QLineEdit,
        QPushButton,
        QWidget,
        QTableWidget,
        QTableWidgetItem,
        )
from . import api
from .logging import setup_logger
from .errors import SnutreeError

###############################################################################
###############################################################################
#### GUI Objects                                                          #####
###############################################################################
###############################################################################

class SchemaTable(QTableWidget):
    '''
    A subclass of QTableWidget that displays information on member format
    schemas. The first column consists of the expected field names for a given
    member format, and the second column consists of the corresponding
    field descriptions.
    '''

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        font_height = self.fontMetrics().height()
        self.setRowCount(2)
        self.setColumnCount(2)
        self.setShowGrid(False)
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.verticalHeader().hide()
        self.verticalHeader().setDefaultSectionSize(font_height * 1.2)
        self.setHorizontalHeaderLabels(['Header', 'Description'])
        self.horizontalHeader().setDefaultAlignment(Qt.AlignLeft)
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setMinimumWidth(40 * font_height)
        self.setMinimumHeight(10 * font_height)

    def show_module_schema(self, module_name):
        '''
        Update the table with schema information on the given module.
        '''

        try:
            module = api.get_schema_module(module_name)
        except SnutreeError as e:
            logging.error(e)
            SnutreeErrorMessage(e).exec_()
            return # Abort table update
        finally:
            # Clear the table before adding new information (or aborting)
            self.setRowCount(0)

        rows = sorted(module.description.items())
        for i, (fieldname, description) in enumerate(rows):

            self.insertRow(i)

            # Add field name
            fieldname_item = QTableWidgetItem(fieldname)
            self.setItem(i, 0, fieldname_item)

            # Add field description
            description_item = QTableWidgetItem(description)
            description_item.setToolTip(description) # For long descriptions
            self.setItem(i, 1, description_item)

        # Fill all horizontal space
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().stretchLastSection()

class SnutreeGUI(QWidget):

    ###########################################################################
    #### Initialization                                                    ####
    ###########################################################################

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        setup_logger(
                debug=False,
                verbose=True,
                quiet=False,
                log_path=None,
                )

        self.setLayout(QGridLayout())
        row_counter = count(start=0)

        # Get configuration files
        self.box_config = self.render_box_file(row_counter, 'Configuration File:',
                'Select configuration file', 'Supported filetypes (*.yaml);;All files (*)')

        # Get data sources (e.g., DOT, CSV, and SQL credential files)
        self.box_inputs = self.render_box_file(row_counter, 'Input Files:',
                'Select input files', 'Supported filetypes (*.csv *.sql *.dot);;All files (*)')

        # Member format dropdown, custom browse button, and schema information
        self.box_member_schema = self.render_box_member_schema(row_counter)

        # Get tree generation seed
        self.box_seed = self.render_box_seed(row_counter)

        # Generation button
        self.button_generate = self.render_button_generate(row_counter)

        self.center()
        self.show()

    ###########################################################################
    #### Main Widgets                                                      ####
    ###########################################################################

    def render_box_file(self, row_counter, label, caption, filter_):
        '''
        Render a file selector in the given row of the GUI's grid. The selector
        has a label, a caption (for the file selection dialog), and a filetypes
        filter.
        '''

        row = next(row_counter)

        textbox = QLineEdit()
        label = QLabel(label, alignment=Qt.AlignRight)
        button = QPushButton('Browse...')

        # Browse button action
        button.clicked.connect(lambda : self.fill_textbox(textbox, caption, '', filter_))

        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(textbox, row, 1)
        self.layout().addWidget(button, row, 2)

        return textbox

    def render_box_member_schema(self, row_counter):
        '''
        Render the member schema selector. Have the builtin member schemas
        already selectable from a drop-down, and allow the possibility for a
        custom Python module to be selected instead of the builtins.
        '''

        row = next(row_counter)

        combobox = QComboBox()
        label = QLabel('Member Format:', alignment=Qt.AlignRight)
        button = QPushButton('Browse...')
        table = SchemaTable()

        # Populate builtin member formats
        formats = api.BUILTIN_SCHEMAS
        for fmt in formats:
            combobox.addItem(fmt, fmt)

        # Browse button (for custom member modules)
        button.clicked.connect(lambda : self.fill_member_textbox(combobox, formats))

        # Update table whenever the selected format changes
        combobox.currentIndexChanged.connect(lambda index : table.show_module_schema(combobox.currentData()))
        table.show_module_schema(combobox.currentData()) # Show initial table

        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(combobox, row, 1)
        self.layout().addWidget(button, row, 2)
        self.layout().addWidget(table, next(row_counter), 1)

        return combobox

    def render_box_seed(self, row_counter):
        '''
        Render the textbox in which the seed is entered.
        '''

        row = next(row_counter)

        textbox = QLineEdit()
        label = QLabel('Seed:', alignment=Qt.AlignRight)

        textbox.setValidator(QIntValidator())

        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(textbox, row, 1)

        return textbox

    def render_button_generate(self, row_counter):
        '''
        Render the tree generation button in the next row.
        '''

        row = next(row_counter)

        button = QPushButton('Generate')

        button.clicked.connect(lambda checked : self.generate())

        self.layout().addWidget(button, row, 0)

        return button

    ###########################################################################
    #### The Meat                                                          ####
    ###########################################################################

    def generate(self):
        '''
        Run the snutree program by calling snutree.generate on the arguments
        that have already been provided by the user to the GUI.
        '''

        try:

            filenames = fancy_split(self.box_inputs.text())
            with ExitStack() as stack:

                input_files = [stack.enter_context(open(f)) for f in filenames]
                output_path = LazyPath(self, 'Select output file', '', 'PDF (*.pdf)', '.pdf')
                configs = [Path(s) for s in fancy_split(self.box_config.text())]
                member_schema = self.box_member_schema.currentData()
                seed = int(self.box_seed.text()) if self.box_seed.text() else 0

                api.generate(
                        input_files=input_files,
                        output_path=output_path,
                        config_paths=configs,
                        input_format=None,
                        schema=member_schema,
                        writer='dot',
                        output_format='pdf',
                        seed=seed,
                        )

        except Exception as e:
            logging.getLogger('snutree').error(e)
            SnutreeErrorMessage(e).exec_()

    ###########################################################################
    #### Tools                                                             ####
    ###########################################################################

    def fill_textbox(self, textbox, caption, dir_, filter_):
        '''
        Have the user select multiple files, and store the filenames in the
        textbox, delimited appropriately. The final arguments are arguments for
        the getOpenFileNames dialog.
        '''
        filenames, _filter = QFileDialog.getOpenFileNames(self, caption, dir_, filter_)
        if filenames:
            paths = [relative_path(f) for f in filenames]
            textbox.setText(fancy_join(paths))

    def fill_member_textbox(self, combobox, formats):
        '''
        Have the user select on file to use as the custom member plugin. Store
        the filename in the combobox (and remove any custom modules that were
        previously in the combobox, by checking the provided list of builtin
        formats).
        '''

        filename, _filter = QFileDialog.getOpenFileName(self, 'Select custom member format',
                '', 'Supported filetypes (*.py);;All files (*)')

        if filename:

            # Remove the last custom module selected, if applicable
            if len(formats) < combobox.count():
                combobox.removeItem(combobox.count() - 1)

            # Add the name and path of the custom module file to the combobox
            path = relative_path(filename)
            combobox.addItem(str(path.name), str(path))

            # Select the module
            combobox.setCurrentIndex(combobox.count() - 1)

    def center(self):
        '''
        Center this widget on the screen.
        '''
        geo = self.frameGeometry()
        center_point = QDesktopWidget().availableGeometry().center()
        geo.moveCenter(center_point)
        self.move(geo.topLeft())

class SnutreeErrorMessage(QErrorMessage):
    '''
    Error message for the Snutree GUI.
    '''

    def __init__(self, exc, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exception = exc
        self.init_ui()

    def init_ui(self):
        self.resize(700, 400)
        self.showMessage(str(self.exception).replace('\n', '<br>'))

###############################################################################
###############################################################################
#### Utilitites                                                           #####
###############################################################################
###############################################################################

def fancy_join(lst):
    '''
    Join the strings in the provided list in style of a CSV file (to avoid the
    hassle of escaping delimiters, etc.). Return the resulting string.
    '''
    stream = StringIO()
    csv.writer(stream).writerow(lst)
    return stream.getvalue().strip()

def fancy_split(string):
    '''
    Split the string as if it were a CSV file row. Return the resulting list.
    '''
    return next(csv.reader(StringIO(string))) if string != '' else ''

def relative_path(path):
    '''
    Return the path as it is represented relative to the current working
    directory. If that is not possible (i.e., the path is not under the current
    working directory), return the path.
    '''
    try:
        return Path(path).relative_to(Path.cwd())
    except ValueError:
        return Path(path)

class LazyPath:
    '''
    A placeholder for some file with extension given in suffix. Waits until the
    very last minute (i.e., when self.__fspath__() is called when interpreting
    this object as a path) to determine an actual value. It determines the
    value by asking the user, using a save file dialog box created from the
    arguments provided to the LazyPath constructor.

    This allows api.generate to be called without knowing the output path
    beforehand, saving time if the generation fails.
    '''

    def __init__(self, parent, caption, dir_, filter_, suffix):
        self.parent = parent
        self.caption = caption
        self.dir = dir_
        self.filter = filter_
        self.suffix = suffix
        self.path = None

    def open(self, *args, **kwargs):
        return Path(self.__fspath__()).open(*args, **kwargs)

    def __fspath__(self):
        if self.path is None:
            logging.getLogger(__name__).info('Asking user for a file path')
            self.path = QFileDialog.getSaveFileName(self.parent, self.caption, self.dir, self.filter)[0]
        return self.path

###############################################################################
###############################################################################
#### Entrypoint                                                           #####
###############################################################################
###############################################################################

def main():
    '''
    Run the snutree GUI.
    '''

    app = QApplication(sys.argv)
    _ = SnutreeGUI()
    sys.exit(app.exec_())

