import sys
import os
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

        config = QHBoxLayout()
        config_label = QLabel('Configuration File:')
        config_browse = QPushButton('Browse...')
        config_browse.clicked.connect(self.config_browse)
        config_box = QLineEdit()
        config.addWidget(config_label)
        config.addWidget(config_box)
        config.addWidget(config_browse)

        gen_Button = QPushButton('Generate')
        gen_Button.clicked.connect(self.generate)
        add_button = QPushButton('Add...')
        add_button.clicked.connect(self.add_files)
        rem_button = QPushButton('Remove')
        rem_button.clicked.connect(self.rem_files)

        buttons = QHBoxLayout()
        buttons.addWidget(gen_Button)
        buttons.addWidget(add_button)
        buttons.addWidget(rem_button)

        layout = QVBoxLayout()
        layout.addLayout(config)
        layout.addWidget(inputs)
        layout.addLayout(buttons)

        self.setLayout(layout)

        self.config_box = config_box
        self.inputs = inputs

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

    def add_files(self):

        filenames, _filter = QFileDialog.getOpenFileNames(self, 'Find', '',
                'All supported filetypes (*.csv *.yaml *.dot);;All files (*.*)')

        for filename in filenames:
            try:
                path = Path(filename).relative_to(Path.cwd())
            except ValueError:
                path = Path(filename)
            self.inputs.addItem(str(path))

    def config_browse(self):

        filename, _filter = QFileDialog.getOpenFileName(self, 'Find', '',
                'All supported filetypes (*.yaml);;All files (*.*)')

        try:
            path = Path(filename).relative_to(Path.cwd())
        except ValueError:
            path = Path(filename)

        self.config_box.setText(str(path))


    def rem_files(self):

        for item in self.inputs.selectedItems():
            self.inputs.takeItem(self.inputs.row(item))

    def generate(self):

        items = self.inputs
        files = []
        for i in range(items.count()):
            files.append(Path(items.item(i).text()).open())

        output_name, _filter = QFileDialog.getSaveFileName(self, 'Find')

        snutree.generate(
                files,
                output_name,
                None,
                [self.config_box.text()],
                0,
                False,
                True,
                False,
                snutree.get_member_format('sigmanu'),
                None
                )

def main():

    app = QApplication(sys.argv)
    _ = SnutreeGUI()
    sys.exit(app.exec_())



