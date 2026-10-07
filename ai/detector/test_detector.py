from pathlib import Path
import sys

# プロジェクトルートをパスに追加
BASE_DIR = Path(__file__).resolve().parents[2]

sys.path.insert(
    0,
    str(BASE_DIR)
)

from capture.screen import ScreenCapture
from detector import Detector


MODEL_PATH = (
    BASE_DIR
    / "models"
    / "yolo11n.pt"
)


def main():

    print("=== Detector Test ===")

    # Detector初期化
    detector = Detector(
        MODEL_PATH
    )

    print("Detector initialized")

    # 画面キャプチャ初期化
    capture = ScreenCapture()

    width, height = capture.get_resolution()

    print(
        f"Screen: {width} x {height}"
    )

    try:

        # 画面を1枚取得
        print("Capturing frame...")

        frame = capture.grab()

        print("Frame captured")

        # YOLO推論
        print("Running YOLO...")

        detections = detector.detect(
            frame
        )

        print(
            f"Detections: {len(detections)}"
        )

        # 検出結果を表示
        for i, detection in enumerate(
            detections,
            start=1
        ):

            print(
                f"[{i}] "
                f"class={detection['class_id']} "
                f"confidence={detection['confidence']:.3f} "
                f"box=("
                f"{detection['x1']:.1f}, "
                f"{detection['y1']:.1f}, "
                f"{detection['x2']:.1f}, "
                f"{detection['y2']:.1f}"
                f")"
            )

    finally:

        capture.close()

    print("=== Test Finished ===")


if __name__ == "__main__":
    main()