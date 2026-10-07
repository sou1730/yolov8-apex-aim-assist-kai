import time

from screen import ScreenCapture


def main():

    capture = ScreenCapture()

    print("Capture started")
    print(
        f"Resolution: "
        f"{capture.width} x {capture.height}"
    )

    start = time.perf_counter()

    try:

        while time.perf_counter() - start < 5:

            frame = capture.grab()

            if frame is None:
                print("Frame acquisition failed")
                break

            print(
                f"\rFPS: {capture.get_fps():.1f}",
                end=""
            )

    finally:

        capture.close()

        print("\nCapture stopped")


if __name__ == "__main__":
    main()