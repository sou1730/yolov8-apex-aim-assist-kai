from pathlib import Path

from ultralytics import YOLO


class Detector:

    def __init__(self, model_path):

        self.model_path = Path(model_path)

        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model not found: {self.model_path}"
            )

        self.model = YOLO(
            str(self.model_path)
        )

    def detect(self, frame):

        results = self.model(
            frame,
            verbose=False
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                xyxy = box.xyxy[0].tolist()

                confidence = float(
                    box.conf[0]
                )

                class_id = int(
                    box.cls[0]
                )

                detection = {
                    "class_id": class_id,
                    "confidence": confidence,
                    "x1": float(xyxy[0]),
                    "y1": float(xyxy[1]),
                    "x2": float(xyxy[2]),
                    "y2": float(xyxy[3]),
                }

                detections.append(
                    detection
                )

        return detections