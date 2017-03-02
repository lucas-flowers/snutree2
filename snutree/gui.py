import sys
import csv
import logging
from itertools import count
from functools import wraps
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
from . import snutree

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

def catched(function):
    '''
    Surround the function with a try-catch block wherever it is called. When
    exceptions occur, they are displayed as error messages to the user.
    '''

    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except Exception as e:
            logging.error(e)
            error = QErrorMessage()
            error.resize(700, 400)
            error.showMessage(str(e).replace('\n', '<br>'))
            error.exec_()

    return wrapped

class LazyPath:
    '''
    A placeholder for some path. Waits until the very last minute (i.e., when
    self.__str__() is called) to determine an actual value. It determines the
    value by asking the user using a save file dialog box created from the
    arguments provided to the LazyPath constructor.

    This allows snutree.generate to be called without knowing the output path
    beforehand, saving time if the generation fails.

    NOTE: Replace __str__ with __fspath__ in Python 3.6
    '''

    def __init__(self, parent, caption, dir_, filter_):
        self.parent = parent
        self.caption = caption
        self.dir = dir_
        self.filter = filter_

    def __str__(self):
        return QFileDialog.getSaveFileName(self.parent, self.caption, self.dir, self.filter)[0]

class SchemaTable(QTableWidget):

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
        self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setMinimumWidth(40 * font_height)
        self.setMinimumHeight(10 * font_height)

    @catched
    def show_module_schema(self, module_name):

        module = snutree.get_member_format(module_name)
        self.setRowCount(0)

        for i, (k, d) in enumerate(sorted(module.schema_information().items())):
            self.insertRow(i)
            self.setItem(i, 0, QTableWidgetItem(k))
            description = QTableWidgetItem(d)
            description.setToolTip(d)
            self.setItem(i, 1, description)

        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().stretchLastSection()


class SnutreeGUI(QWidget):
    '''
    A simple GUI for the snutree program. Advanced features are available in
    the CLI version of the program.
    '''

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):

        row = count(start=0)

        self.setLayout(QGridLayout())

        # Configuration
        self.config_box = self.file_select(
                row,
                'Configuration File:',
                'Select configuration file',
                'Supported filetypes (*.yaml);;All files (*)'
                )

        # Data sources (e.g., DOT, CSV, and SQL credential files)
        self.inputs_box = self.file_select(
                row,
                'Input Files:',
                'Select input files',
                'Supported filetypes (*.csv *.yaml *.dot);;All files (*)'
                )

        # Member format dropdown, custom browse button, and schema information
        self.member_format_box = self.member_format_select(
                row,
                'Member Format:',
                'Select custom member format',
                'Supported filetypes (*.py);;All files (*)'
                )

        self.seed_box = self.seed_select(row, 'Seed:')

        gen_button = QPushButton('Generate')
        gen_button.clicked.connect(lambda checked : self.generate())
        self.layout().addWidget(gen_button, next(row), 0)
        self.gen_button = gen_button

        self.center()

        self.show()

    def file_select(self, row_counter, label, title, filetypes):
        '''
        Create a file selector in the given row of the GUI's grid. The selector
        has a label, a title (for the file selection dialog), and supported
        filetypes.
        '''

        row = next(row_counter)

        textbox = QLineEdit()
        label = QLabel(label, alignment=Qt.AlignRight)
        button = QPushButton('Browse...')
        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(textbox, row, 1)
        self.layout().addWidget(button, row, 2)

        def browse():
            '''
            Have the user select multiple files. Store the files as a
            comma-delimited list in the GUI's textbox.
            '''

            filenames, _filter = QFileDialog.getOpenFileNames(self, title, '', filetypes)
            if filenames:
                paths = [relative_path(f) for f in filenames]
                textbox.setText(fancy_join(paths))

        button.clicked.connect(browse)

        return textbox

    def member_format_select(self, row_counter, label, title, filetypes):
        '''
        Create a member format selector. Have the builtins already selectable
        from a drop-down, and allow the possibility for a custom Python module
        to be selected instead of the builtins.
        '''

        row = next(row_counter)

        table = SchemaTable()
        combobox = QComboBox()
        label = QLabel(label, alignment=Qt.AlignRight)
        button = QPushButton('Browse...')
        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(combobox, row, 1)
        self.layout().addWidget(button, row, 2)

        # Populate default formats
        formats = snutree.PLUGIN_BASE.make_plugin_source(searchpath=[]).list_plugins()
        for fmt in formats:
            combobox.addItem(fmt, fmt)

        def browse():
            '''
            Have the user select a single file to provide the member format.
            Add the file's name as an option in the dropdown (and remove any
            previous custom modules that were selected).
            '''

            filename, _filter = QFileDialog.getOpenFileName(self, title, '', filetypes)
            if filename:
                path = relative_path(filename)
                if len(formats) < combobox.count():
                    # Remove the last custom module selected
                    combobox.removeItem(combobox.count()-1)
                combobox.addItem(str(path.name), str(path))
                combobox.setCurrentIndex(combobox.count()-1)

        button.clicked.connect(browse)
        combobox.currentIndexChanged.connect(lambda index : table.show_module_schema(combobox.currentData()))

        table.show_module_schema(combobox.currentData())
        self.layout().addWidget(table, next(row_counter), 1)

        return combobox

    def seed_select(self, row_counter, label):
        '''
        Create the textbox to enter the seed in.
        '''

        row = next(row_counter)

        label = QLabel(label, alignment=Qt.AlignRight)
        textbox = QLineEdit()
        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(textbox, row, 1)

        textbox.setValidator(QIntValidator())

        return textbox

    def center(self):
        '''
        Center this widget on the screen.
        '''
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    @catched
    def generate(self):
        '''
        Run the snutree program by calling snutree.generate.
        '''

        files = [Path(f).open() for f in fancy_split(self.inputs_box.text())]
        configs = fancy_split(self.config_box.text())
        member_format = self.member_format_box.currentData()
        output_path = LazyPath(self, 'Select output file', '', 'PDF (*.pdf);;Graphviz source (*.dot)')
        seed = int(self.seed_box.text()) if self.seed_box.text() else 0

        snutree.generate(
                files=files,
                output_path=output_path,
                log_path=None,
                config_paths=configs,
                member_format=member_format,
                input_format=None,
                seed=seed,
                debug=False,
                verbose=True,
                quiet=False,
                )

def main():

    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    _ = SnutreeGUI()
    sys.exit(app.exec_())

