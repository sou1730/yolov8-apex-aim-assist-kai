import time

import cv2
import mss
import numpy as np


class ScreenCapture:

    def __init__(self, monitor_index=1):
        self.sct = mss.mss()

        monitors = self.sct.monitors

        if monitor_index >= len(monitors):
            monitor_index = 1

        self.monitor = monitors[monitor_index]

        self.width = self.monitor["width"]
        self.height = self.monitor["height"]

        self.frame_count = 0
        self.last_time = time.perf_counter()
        self.fps = 0.0

    def grab(self):
        raw = self.sct.grab(self.monitor)

        frame = np.asarray(raw)

        # BGRA → BGR
        frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2BGR
        )

        self.frame_count += 1

        now = time.perf_counter()
        elapsed = now - self.last_time

        if elapsed >= 1.0:
            self.fps = self.frame_count / elapsed

            self.frame_count = 0
            self.last_time = now

        return frame

    def get_fps(self):
        return self.fps

    def get_resolution(self):
        return self.width, self.height

    def close(self):
        self.sct.close()