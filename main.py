import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QLineEdit, QSlider
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QDoubleValidator
import subprocess


class RunDetectionThread(QThread):
    def __init__(self, command, HFW):
        super().__init__()
        self.command = command
        self.HFW = HFW

    def run(self):
        command_with_HFW = f"{self.command} --HFW {self.HFW}"
        subprocess.call(command_with_HFW, shell=True)


class AppDemo(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Detection Runner')
        self.setLayout(QVBoxLayout())

        # Source Path
        self.source_label = QLabel('Source Path:')
        self.layout().addWidget(self.source_label)

        self.source_entry = QLineEdit()
        self.layout().addWidget(self.source_entry)

        self.source_button = QPushButton('Browse...')
        self.source_button.clicked.connect(self.browse_source)
        self.layout().addWidget(self.source_button)

        # Project Path
        self.project_label = QLabel('Project Path:')
        self.layout().addWidget(self.project_label)

        self.project_entry = QLineEdit()
        self.layout().addWidget(self.project_entry)

        self.project_button = QPushButton('Browse...')
        self.project_button.clicked.connect(self.browse_project)
        self.layout().addWidget(self.project_button)

        # Confidence Threshold
        self.conf_label = QLabel('Confidence Threshold:')
        self.layout().addWidget(self.conf_label)

        self.conf_slider = QSlider(Qt.Horizontal)
        self.conf_slider.setMinimum(0)
        self.conf_slider.setMaximum(100)
        self.conf_slider.valueChanged.connect(self.update_label)
        self.layout().addWidget(self.conf_slider)

        # HFW (Half Field Width)
        self.HFW_label = QLabel('HFW (micrometer):')
        self.layout().addWidget(self.HFW_label)

        self.HFW_entry = QLineEdit()
        self.HFW_entry.setValidator(QDoubleValidator(0.0, 1000.0, 2))  # Allow decimals with 2 decimal places
        self.layout().addWidget(self.HFW_entry)

        # Run Detection
        self.run_button = QPushButton('Run Detection')
        self.run_button.clicked.connect(self.run_detection)
        self.layout().addWidget(self.run_button)

    def browse_source(self):
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory()
        self.source_entry.setText(dir_path)

    def browse_project(self):
        file_dialog = QFileDialog()
        dir_path = file_dialog.getExistingDirectory()
        self.project_entry.setText(dir_path)

    def update_label(self):
        self.conf_label.setText('Confidence Threshold: ' + str(self.conf_slider.value() / 100))

    def run_detection(self):
        source_path = self.source_entry.text()
        project_path = self.project_entry.text()
        confidence = self.conf_slider.value() / 100
        HFW = float(self.HFW_entry.text())

        if not source_path or not project_path:
            return

        command = f"python detect.py --source {source_path} --project {project_path} --conf-thres {confidence} --hide-conf --hide-labels --save-txt"
        self.thread = RunDetectionThread(command, HFW)
        self.thread.finished.connect(self.close)
        self.thread.start()


app = QApplication(sys.argv)
demo = AppDemo()
demo.show()

sys.exit(app.exec_())
