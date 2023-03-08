from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import (QApplication, 
                            QMainWindow, 
                            QPushButton, 
                            QFileDialog, 
                            QListWidget, 
                            QLabel,
                            QGridLayout,
                            QWidget)
# For command line arguments
import sys, os
from pathlib import Path

import process_data

# Subclass QMainWindow to customize your application's main window
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(800, 600))

        layout = QGridLayout()

        zip_button = QPushButton("Add Zip Files")
        zip_button.clicked.connect(self.open_zip_dialog)

        dir_button = QPushButton("Add Destination Directory")
        dir_button.clicked.connect(self.open_dir_dialog)

        self.start_button = QPushButton("Start Processing")
        self.start_button.clicked.connect(self.process_files)

        self.file_list = QListWidget()
        self.des_dir = QListWidget()
        self.process_messages = QListWidget()

        layout.addWidget(QLabel('Selected Zip Files:'), 0, 0)
        layout.addWidget(self.file_list, 1, 0)
        layout.addWidget(zip_button, 1, 1)
        layout.addWidget(QLabel('Selected Destination Directory:'), 2, 0)
        layout.addWidget(self.des_dir, 3, 0)
        layout.addWidget(dir_button, 3, 1)
        layout.addWidget(QLabel('Processing messages'), 4, 0)
        layout.addWidget(self.process_messages, 5, 0)
        layout.addWidget(self.start_button, 5, 1)
        

        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)


    def open_zip_dialog(self):
        filenames, _ = QFileDialog.getOpenFileNames(self, "Select Zip Files", os.path.expanduser('~'), "ZIP (*.zip)")
        if filenames:
            self.file_list.addItems([str(Path(filename)) for filename in filenames])

    def open_dir_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory", os.path.expanduser('~'))
        if dir_name:
            if self.des_dir.count() == 0:
                self.des_dir.addItem(str(Path(dir_name)))
            else:
                self.des_dir.item(0).setText(str(Path(dir_name)))

    def process_files(self):
        self.start_button.setEnabled(False)
        dir = self.des_dir.item(0).text()
        for i in range(self.file_list.count()):
            zip_file = self.file_list.item(i).text()
            for message in process_data.extract_files(zip_file, dir):
                self.process_messages.addItem(message)
        self.start_button.setEnabled(True)

        

app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()
