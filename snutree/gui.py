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
        QDesktopWidget
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

        inputs = QHBoxLayout()
        inputs_label = QLabel('Input Files:')
        inputs_browse = QPushButton('Browse...')
        inputs_browse.clicked.connect(self.inputs_browse)
        inputs_box = QLineEdit()
        inputs.addWidget(inputs_label)
        inputs.addWidget(inputs_box)
        inputs.addWidget(inputs_browse)

        buttons = QHBoxLayout()
        gen_button = QPushButton('Generate')
        gen_button.clicked.connect(self.generate)
        buttons.addWidget(gen_button)

        layout = QVBoxLayout()
        # layout.addLayout(config)
        layout.addLayout(inputs)
        layout.addLayout(buttons)

        self.setLayout(layout)

        # self.config_box = config_box
        self.inputs_box = inputs_box

        self.resize(600, 150)
        self.center()

        self.show()

    def center(self):

        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Delete:
            self.rem_files()

    def inputs_browse(self):

        filenames, _filter = QFileDialog.getOpenFileNames(self, 'Find', '',
                'All supported filetypes (*.csv *.yaml *.dot);;All files (*.*)')

        if not filenames:
            return

        paths = []
        for filename in filenames:
            try:
                paths.append(Path(filename).relative_to(Path.cwd()))
            except ValueError:
                paths.append(Path(filename))

        filenames_stream = StringIO()
        csv.writer(filenames_stream, delimiter=';').writerow(paths)
        self.inputs_box.setText(filenames_stream.getvalue())

    # def config_browse(self):
    #
    #     filename, _filter = QFileDialog.getOpenFileName(self, 'Find', '',
    #             'All supported filetypes (*.yaml);;All files (*.*)')
    #
    #     if not filename:
    #         return
    #
    #     try:
    #         path = Path(filename).relative_to(Path.cwd())
    #     except ValueError:
    #         path = Path(filename)
    #
    #     self.config_box.setText(str(path))


    def rem_files(self):

        for item in self.inputs.selectedItems():
            self.inputs.takeItem(self.inputs.row(item))

    def generate(self):

        files = next(csv.reader(StringIO(self.inputs_box.text()), delimiter=';'))

        output_name, _filter = QFileDialog.getSaveFileName(self, 'Find', '',
                'PDF (*.pdf);;Graphviz source (*.dot)', 'PDF (*.pdf)')

        config = self.config_box.text() or None
        configs = [config] if config else []

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



