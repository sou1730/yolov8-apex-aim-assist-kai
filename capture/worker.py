import time

from PySide6.QtCore import QThread, Signal

from capture.screen import ScreenCapture


class CaptureWorker(QThread):

    frame_ready = Signal(object)
    fps_updated = Signal(float)

    def __init__(self):
        super().__init__()

        self.running = False
        self.capture = None

    def run(self):

        self.capture = ScreenCapture()
        self.running = True

        last_fps_update = time.perf_counter()

        try:

            while self.running:

                frame = self.capture.grab()

                if frame is None:
                    continue

                self.frame_ready.emit(frame)

                now = time.perf_counter()

                if now - last_fps_update >= 0.5:

                    self.fps_updated.emit(
                        self.capture.get_fps()
                    )

                    last_fps_update = now

        finally:

            if self.capture is not None:

                self.capture.close()
                self.capture = None

    def stop(self):

        self.running = False

        self.wait()