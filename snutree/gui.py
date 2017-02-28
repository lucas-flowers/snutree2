import sys
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
        QListWidgetItem,
        QAbstractItemView
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
        layout.addWidget(inputs)
        layout.addLayout(buttons)


        self.inputs = inputs
        self.setLayout(layout)

        self.show()

    def keyPressEvent(self, event):

        key = event.key()
        if key == Qt.Key_Delete:
            self.rem_files()

    def add_files(self):

        # TODO are these the conventional names to assign?
        filenames, _ = QFileDialog.getOpenFileNames(
                self,
                'Find',
                '',
                'All supported filetypes (*.csv *.yaml *.dot);;All files (*.*)'
                )

        for filename in filenames:
            try:
                path = Path(filename).relative_to(Path.cwd())
            except ValueError:
                path = Path(filename)
            self.inputs.addItem(str(path))

    def rem_files(self):

        for item in self.inputs.selectedItems():
            self.inputs.takeItem(self.inputs.row(item))

    def generate(self):

        items = self.inputs
        files = []
        for i in range(items.count()):
            files.append(Path(items.item(i).text()).open())

        snutree.generate(
                files,
                'out.pdf',
                None,
                [],
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



