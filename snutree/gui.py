import sys
import csv
import logging
from io import StringIO
from contextlib import contextmanager
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QIntValidator,
    )
from PyQt5.QtWidgets import (
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

        self.member_format_box = self.member_format_select(
                self.next_row,
                'Member Format:',
                'Select custom member format',
                'Supported filetypes (*.py);;All files (*)'
                )

        self.seed_box = self.seed_select(self.next_row, 'Seed:')

        gen_button = QPushButton('Generate')
        gen_button.clicked.connect(self.generate)
        self.layout().addWidget(gen_button, self.next_row, 0)
        self.gen_button = gen_button

        self.resize(600, 150)
        self.center()

        self.show()

    def file_select(self, row, label, title, filetypes):
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

        button.clicked.connect(browse)

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

    @contextmanager
    def progress(self):


        self.setEnabled(False)
        yield
        self.setEnabled(True)

    def generate(self):
        '''
        Run the snutree program by calling snutree.generate. Catch recoverable
        errors.
        '''

        files = [Path(f).open() for f in fancy_split(self.inputs_box.text())]
        configs = fancy_split(self.config_box.text())
        member_format = self.member_format_box.currentData()
        seed = int(self.seed_box.text()) if self.seed_box.text() else 0

        output_name, _filter = QFileDialog.getSaveFileName(self, 'Find', '',
                'PDF (*.pdf);;Graphviz source (*.dot)', 'PDF (*.pdf)')

        if not output_name:
            return

        with self.progress():

            try:

                snutree.generate(
                        files=files,
                        output_path=output_name,
                        log_path=None,
                        config_paths=configs,
                        member_format=member_format,
                        input_format=None,
                        seed=seed,
                        debug=False,
                        verbose=True,
                        quiet=False,
                        )

            except snutree.SnutreeError as e:
                logging.error(e)
                error = QErrorMessage()
                error.showMessage(str(e).replace('\n', '<br>'))
                error.exec_()

def main():

    try:
        app = QApplication(sys.argv)
        _ = SnutreeGUI()
        sys.exit(app.exec_())
    except Exception:
        logging.error('Unexpected error.', exc_info=True)
        error = QErrorMessage()
        error.showMessage('Unexpected error. See log for details.')
        sys.exit(error.exec_())


