import sys
import json
from pathlib import Path

sys.path.insert(
    0,
    str(Path(__file__).resolve().parent.parent)
)

from PySide6.QtCore import Qt

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSlider,
    QPushButton,
    QGroupBox,
)

from capture.worker import CaptureWorker


BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = BASE_DIR / "config"
CONFIG_FILE = CONFIG_DIR / "settings.json"


DEFAULT_SETTINGS = {
    "aim_strength": 0.65,
    "target_range": 350,
    "smoothing": 0.55,
}


def load_settings():
    CONFIG_DIR.mkdir(exist_ok=True)

    if not CONFIG_FILE.exists():
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(data)

        return settings

    except (json.JSONDecodeError, OSError):
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    CONFIG_DIR.mkdir(exist_ok=True)

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.settings = load_settings()
        self.running = False

        self.setWindowTitle("ONI-LIKE AI TEST TOOL")
        self.resize(600, 650)

        self.setup_ui()
        self.update_ui_from_settings()

        self.capture_worker = None

    def setup_ui(self):

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(15)

        # -------------------------
        # Title
        # -------------------------

        title = QLabel("ONI-LIKE AI TEST TOOL")
        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)

        main_layout.addWidget(title)

        # -------------------------
        # AI Settings
        # -------------------------

        settings_group = QGroupBox("AI SETTINGS")
        settings_layout = QVBoxLayout()

        # Aim Strength
        self.aim_label = QLabel()
        self.aim_slider = QSlider(Qt.Horizontal)

        self.aim_slider.setMinimum(0)
        self.aim_slider.setMaximum(100)

        self.aim_slider.valueChanged.connect(
            self.on_aim_strength_changed
        )

        settings_layout.addWidget(self.aim_label)
        settings_layout.addWidget(self.aim_slider)

        # Target Range
        self.range_label = QLabel()
        self.range_slider = QSlider(Qt.Horizontal)

        self.range_slider.setMinimum(50)
        self.range_slider.setMaximum(1000)

        self.range_slider.valueChanged.connect(
            self.on_target_range_changed
        )

        settings_layout.addWidget(self.range_label)
        settings_layout.addWidget(self.range_slider)

        # Smoothing
        self.smoothing_label = QLabel()
        self.smoothing_slider = QSlider(Qt.Horizontal)

        self.smoothing_slider.setMinimum(0)
        self.smoothing_slider.setMaximum(100)

        self.smoothing_slider.valueChanged.connect(
            self.on_smoothing_changed
        )

        settings_layout.addWidget(self.smoothing_label)
        settings_layout.addWidget(self.smoothing_slider)

        settings_group.setLayout(settings_layout)
        main_layout.addWidget(settings_group)

        # -------------------------
        # Capture
        # -------------------------

        capture_group = QGroupBox("CAPTURE")
        capture_layout = QVBoxLayout()

        self.fps_label = QLabel("FPS: --")
        self.resolution_label = QLabel("Resolution: --- × ---")
        self.status_label = QLabel("Status: STOPPED")

        capture_layout.addWidget(self.fps_label)
        capture_layout.addWidget(self.resolution_label)
        capture_layout.addWidget(self.status_label)

        capture_group.setLayout(capture_layout)
        main_layout.addWidget(capture_group)

        # -------------------------
        # Detection
        # -------------------------

        detection_group = QGroupBox("DETECTION")
        detection_layout = QVBoxLayout()

        self.target_label = QLabel("Targets: 0")
        self.confidence_label = QLabel("Confidence: 0.00")

        detection_layout.addWidget(self.target_label)
        detection_layout.addWidget(self.confidence_label)

        detection_group.setLayout(detection_layout)
        main_layout.addWidget(detection_group)

        # -------------------------
        # Buttons
        # -------------------------

        button_layout = QHBoxLayout()

        self.start_button = QPushButton("START")
        self.stop_button = QPushButton("STOP")

        self.start_button.clicked.connect(self.start_system)
        self.stop_button.clicked.connect(self.stop_system)

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)

        main_layout.addLayout(button_layout)

    # -------------------------
    # Settings
    # -------------------------

    def update_ui_from_settings(self):

        aim_strength = self.settings["aim_strength"]
        target_range = self.settings["target_range"]
        smoothing = self.settings["smoothing"]

        self.aim_slider.setValue(
            int(aim_strength * 100)
        )

        self.range_slider.setValue(
            int(target_range)
        )

        self.smoothing_slider.setValue(
            int(smoothing * 100)
        )

        self.update_labels()

    def update_labels(self):

        aim = self.settings["aim_strength"]
        target_range = self.settings["target_range"]
        smoothing = self.settings["smoothing"]

        self.aim_label.setText(
            f"AIM ASSIST STRENGTH: {aim:.0%}"
        )

        self.range_label.setText(
            f"TARGET RANGE: {target_range} px"
        )

        self.smoothing_label.setText(
            f"SMOOTHING: {smoothing:.0%}"
        )

    def on_aim_strength_changed(self, value):

        self.settings["aim_strength"] = value / 100

        self.update_labels()
        save_settings(self.settings)

    def on_target_range_changed(self, value):

        self.settings["target_range"] = value

        self.update_labels()
        save_settings(self.settings)

    def on_smoothing_changed(self, value):

        self.settings["smoothing"] = value / 100

        self.update_labels()
        save_settings(self.settings)

    # -------------------------
    # System control
    # -------------------------

    def start_system(self):

        if self.running:
            return

        self.capture_worker = CaptureWorker()

        self.capture_worker.fps_updated.connect(
            self.update_fps
        )

        self.capture_worker.start()

        self.running = True

        self.status_label.setText(
            "Status: RUNNING"
        )

    def stop_system(self):

        if not self.running:
            return

        self.running = False

        if self.capture_worker is not None:

            self.capture_worker.stop()
            self.capture_worker = None

        self.status_label.setText(
            "Status: STOPPED"
        )

        self.fps_label.setText(
            "FPS: --"
        )

        self.resolution_label.setText(
            "Resolution: --- × ---"
        )

    def update_fps(self, fps):

        self.fps_label.setText(
            f"FPS: {fps:.1f}"
        )



def main():

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()