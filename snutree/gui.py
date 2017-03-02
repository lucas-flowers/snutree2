import sys
import csv
import io
import logging
import tempfile
from functools import wraps
from io import StringIO
from contextlib import contextmanager, redirect_stdout
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
    working directory), return path.
    '''
    try:
        return Path(path).relative_to(Path.cwd())
    except ValueError:
        return Path(path)

def recoverable(function):

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

class SnutreeGUI(QWidget):
    '''
    A simple GUI for the snutree program. Advanced features are available in
    the CLI version of the program.
    '''

    def __init__(self):

        super().__init__()

        self.__row = 0
        self.initUI()

    @property
    def next_row(self):
        result = self.__row
        self.__row += 1
        return result

    @property
    def current_row(self):
        return self.__row

    def initUI(self):

        font_height = self.fontMetrics().height()
        self.setLayout(QGridLayout())

        self.config_box = self.file_select(
                self.next_row,
                'Configuration File:',
                'Select configuration file',
                'Supported filetypes (*.yaml);;All files (*)'
                )

        self.inputs_box = self.file_select(
                self.next_row,
                'Input Files:',
                'Select input files',
                'Supported filetypes (*.csv *.yaml *.dot);;All files (*)'
                )

        self.output_box = self.file_select(
                self.next_row,
                'Output File:',
                'Select output file',
                'PDF (*.pdf);;Graphviz source (*.dot)',
                save=True,
                )

        self.table = QTableWidget()
        self.table.setRowCount(2)
        self.table.setColumnCount(2)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.verticalHeader().hide()
        self.table.verticalHeader().setDefaultSectionSize(font_height * 1.2)
        self.table.setHorizontalHeaderLabels(['Header', 'Description'])
        self.table.setSelectionMode(QAbstractItemView.NoSelection)
        self.table.setMinimumWidth(40 * font_height)
        self.table.setMinimumHeight(10 * font_height)
        self.member_format_box = self.member_format_select(
                self.next_row,
                'Member Format:',
                'Select custom member format',
                'Supported filetypes (*.py);;All files (*)'
                )
        self.layout().addWidget(self.table, self.next_row, 1)

        self.seed_box = self.seed_select(self.next_row, 'Seed:')

        gen_button = QPushButton('Generate')
        gen_button.clicked.connect(lambda checked : self.generate())
        self.layout().addWidget(gen_button, self.next_row, 0)
        self.gen_button = gen_button

        self.center()

        self.show()

    def file_select(self, row, label, title, filetypes, save=False):
        '''
        Create a file selector in the given row of the GUI's grid. The selector
        has a label, a title (for the file selection dialog), and supported
        filetypes.
        '''

        textbox = QLineEdit()
        label = QLabel(label, alignment=Qt.AlignRight)
        button = QPushButton('Browse...')
        self.layout().addWidget(label, row, 0)
        self.layout().addWidget(textbox, row, 1)
        self.layout().addWidget(button, row, 2)

        if save:
            file_getter = lambda *args, **kwargs : [QFileDialog.getSaveFileName(*args, **kwargs)[0]]
        else:
            file_getter = lambda *args, **kwargs : QFileDialog.getOpenFileNames(*args, **kwargs)[0]

        def browse():
            '''
            Have the user select multiple files. Store the files as a
            comma-delimited list in the GUI's textbox.
            '''

            filenames = file_getter(self, title, '', filetypes)
            if filenames:
                paths = [relative_path(f) for f in filenames]
                textbox.setText(fancy_join(paths))

        button.clicked.connect(browse)

        return textbox

    def member_format_select(self, row, label, title, filetypes):
        '''
        Create a member format selector. Have the builtins already selectable
        from a drop-down, and allow the possibility for a custom Python module
        to be selected instead of the builtins.
        '''

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

        @recoverable
        def show_module_schema(index):
            module = snutree.get_member_format(combobox.currentData())
            self.table.setRowCount(0)
            for i, (k, d) in enumerate(sorted(module.schema_information().items())):


                self.table.insertRow(i)
                self.table.setItem(i, 0, QTableWidgetItem(k))

                description = QTableWidgetItem(d)
                description.setToolTip(d)
                self.table.setItem(i, 1, description)
            # self.table.resizeColumnsToContents()
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().stretchLastSection()



        button.clicked.connect(browse)
        combobox.currentIndexChanged.connect(show_module_schema)
        show_module_schema(0)

        return combobox

    def seed_select(self, row, label):
        '''
        Create the textbox to enter the seed in.
        '''

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

    @recoverable
    def generate(self):
        '''
        Run the snutree program by calling snutree.generate. Catch recoverable
        errors.
        '''

        files = [Path(f).open() for f in fancy_split(self.inputs_box.text())]
        configs = fancy_split(self.config_box.text())
        member_format = self.member_format_box.currentData()
        output_path = self.output_box.text()
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

