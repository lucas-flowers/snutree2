import sys
import os
import csv
from io import StringIO
from pathlib import Path
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
        QApplication,
        QWidget,
        QLabel,
        QPushButton,
        QHBoxLayout,
        QVBoxLayout,
        QFileDialog,
        QListWidget,
        QAbstractItemView,
        QLineEdit,
        QDesktopWidget,
        QComboBox,
        )
from . import snutree

# Click icon
# Select member type from one of:
#   + Selector
#   + Path
# Select input file
# See list of input files and select more
# Execute (reading from 'config.yaml')
# Log
# Save

def fancy_join(lst):
    stream = StringIO()
    csv.writer(stream).writerow(lst)
    return stream.getvalue().strip()

def fancy_split(string):
    return next(csv.reader(StringIO(string)))

def relative_path(path):
    try:
        return Path(path).relative_to(Path.cwd())
    except ValueError:
        return Path(path)

class SnutreeGUI(QWidget):

    def __init__(self):

        super().__init__()

        self.member_type = 'sigmanu'

        self.initUI()

    def initUI(self):

        inputs = QListWidget()
        inputs.setSelectionMode(QAbstractItemView.ExtendedSelection)

        # config = QHBoxLayout()
        # config_label = QLabel('Configuration File:')
        # config_browse = QPushButton('Browse...')
        # config_browse.clicked.connect(self.config_browse)
        # config_box = QLineEdit()
        # config.addWidget(config_label)
        # config.addWidget(config_box)
        # config.addWidget(config_browse)
        # self.config_box = config_box

        config, self.config_box = self.file_select(
                'Configuration File:',
                'Select configuration file',
                'Supported filetypes (*.yaml);;All files (*.*)'
                )

        inputs, self.inputs_box = self.file_select(
                'Input Files:',
                'Select input files',
                'Supported filetypes (*.csv *.yaml *.dot);;All files (*.*)'
                )

        member_format, self.member_format_box = self.member_format_select(
                'Member Format:',
                'Select custom member format',
                'Supported filetypes (*.py);;All files (*.*)'
                )

        buttons = QHBoxLayout()
        gen_button = QPushButton('Generate')
        gen_button.clicked.connect(self.generate)
        buttons.addWidget(gen_button)

        layout = QVBoxLayout()
        layout.addLayout(config)
        layout.addLayout(inputs)
        layout.addLayout(member_format)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.resize(600, 150)
        self.center()

        self.show()

    def file_select(self, label, title, filetypes):

        row = QHBoxLayout()
        textbox = QLineEdit()
        label = QLabel(label)
        button = QPushButton('Browse...')
        row.addWidget(label)
        row.addWidget(textbox)
        row.addWidget(button)

        def browse():

            filenames, _filter = QFileDialog.getOpenFileNames(self, title, '', filetypes)
            if filenames:
                paths = [relative_path(f) for f in filenames]
                textbox.setText(fancy_join(paths))

        button.clicked.connect(browse)

        return row, textbox

    def member_format_select(self, label, title, filetypes):

        row = QHBoxLayout()
        combobox = QComboBox()
        label = QLabel(label)
        button = QPushButton('Browse...')
        row.addWidget(label)
        row.addWidget(combobox)
        row.addWidget(button)

        formats = snutree.PLUGIN_BASE.make_plugin_source(searchpath=[]).list_plugins()
        for f in formats:
            combobox.addItem(f)

        def browse():

            filename, _filter = QFileDialog.getOpenFileName(self, title, '', filetypes)
            if filename:
                path = relative_path(filename)
                combobox.insertItem(0, str(path))

        button.clicked.connect(browse)

        return row, combobox

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def generate(self):

        files = fancy_split(self.inputs_box.text())
        configs = fancy_split(self.config_box.text())

        output_name, _filter = QFileDialog.getSaveFileName(self, 'Find', '',
                'PDF (*.pdf);;Graphviz source (*.dot)', 'PDF (*.pdf)')

        if not output_name:
            return

        snutree.generate(
                files=files,
                output_path=output_name,
                log_path=None,
                config_paths=configs,
                member_format='sigmanu',
                input_format=None,
                seed=0,
                debug=False,
                verbose=True,
                quiet=False,
                )

def main():

    app = QApplication(sys.argv)
    _ = SnutreeGUI()
    sys.exit(app.exec_())



