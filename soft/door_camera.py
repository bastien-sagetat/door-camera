#!/usr/bin/env python3

import argparse
import logging
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np

FPS = 30.0
DETECTION_INTERVAL = 0.1  # 100 ms


def parse_args():
    parser = argparse.ArgumentParser(description="Door camera motion detector and recorder.")
    parser.add_argument("--camera", default="auto", help="Camera index, device path, or 'auto'. Default: auto")
    parser.add_argument("--output-dir", type=Path, default=Path.home() / "recordings", help="Directory for recordings and log files.")
    parser.add_argument("--no-motion-time", type=float, default=10.0, help="Seconds without motion before recording stops. Default: 10")
    parser.add_argument("--motion-threshold", type=float, default=2.0, help="Percentage of changed pixels needed to detect motion. Default: 2.0")
    parser.add_argument("--pixel-threshold", type=int, default=25, help="Minimum grayscale pixel difference counted as a change. Default: 25")
    parser.add_argument("--darkness-threshold", type=float, default=40.0, help="Average grayscale brightness below this is considered dark. Default: 40")
    parser.add_argument("--light-ignore-time", type=float, default=2.0, help="Seconds to ignore motion after a light transition. Default: 2")
    parser.add_argument("--debug", action="store_true", help="Enable detailed debug logging.")
    return parser.parse_args()


def find_camera():
    by_id_dir = Path("/dev/v4l/by-id")
    if by_id_dir.exists():
        for device in sorted(by_id_dir.iterdir()):
            name = device.name.lower()
            if "innomaker" in name or "ps5268" in name:
                return str(device)
    return 0


def setup_logging(output_dir, debug):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = output_dir / f"{timestamp}.log"
    level = logging.DEBUG if debug else logging.INFO
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logging.basicConfig(level=level, handlers=[console_handler, file_handler])
    return log_file


def main(args):
    args.output_dir.mkdir(parents=True, exist_ok=True)
    log_file = setup_logging(args.output_dir, args.debug)
    logging.info("Door camera motion detector starting.")
    logging.info("Log file: %s", log_file)
    logging.info("Output directory: %s", args.output_dir)
    logging.info("FPS: %.1f", FPS)
    logging.info("Motion detection interval: %.0f ms", DETECTION_INTERVAL * 1000)
    logging.info("No-motion timeout: %.1f s", args.no_motion_time)
    logging.info("Motion threshold: %.2f%%", args.motion_threshold)
    logging.info("Pixel threshold: %d", args.pixel_threshold)
    logging.info("Darkness threshold: %.1f", args.darkness_threshold)
    logging.info("Light ignore time: %.1f s", args.light_ignore_time)

    if args.camera.lower() == "auto":
        camera_source = find_camera()
    elif args.camera.isdigit():
        camera_source = int(args.camera)
    else:
        camera_source = args.camera

    logging.info("Opening camera: %s", camera_source)
    cap = cv2.VideoCapture(camera_source, cv2.CAP_V4L2)
    if not cap.isOpened():
        logging.warning("V4L2 open failed; trying default camera backend.")
        cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        logging.error("Could not open camera: %s", camera_source)
        return 1

    cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    cap.set(cv2.CAP_PROP_FPS, FPS)

    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    actual_fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))

    fourcc_text = "".join(
        chr((actual_fourcc >> (8 * i)) & 0xFF)
        for i in range(4)
    )

    logging.info("Camera resolution: %dx%d", actual_width, actual_height)
    logging.info("Camera FPS reported by driver: %.1f", actual_fps)
    logging.info("Camera pixel format: %s", fourcc_text)

    previous_gray = None
    previous_brightness = None
    recording = False
    writer = None
    recording_started_at = 0.0
    last_motion_time = 0.0
    next_detection_time = 0.0
    ignore_motion_until = 0.0

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                logging.warning("Could not read frame from camera.")
                time.sleep(0.1)
                continue

            now = time.monotonic()
            motion = False

            if previous_gray is None or now >= next_detection_time:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = float(np.mean(gray))

                if previous_gray is not None:
                    was_dark = previous_brightness < args.darkness_threshold
                    is_dark = brightness < args.darkness_threshold
                    light_transition = was_dark != is_dark

                    if light_transition:
                        ignore_motion_until = now + args.light_ignore_time
                        logging.info("Light transition detected: brightness %.1f -> %.1f; ignoring motion for %.1f s.", previous_brightness, brightness, args.light_ignore_time)
                    elif now < ignore_motion_until:
                        logging.debug("Motion check ignored while light transition settles (%.2f s remaining).", ignore_motion_until - now)
                    else:
                        difference = cv2.absdiff(gray, previous_gray)
                        changed_pixels = np.count_nonzero(difference >= args.pixel_threshold)
                        changed_percentage = (changed_pixels / difference.size) * 100.0
                        motion = changed_percentage >= args.motion_threshold
                        logging.debug("Brightness=%.1f, changed=%.2f%%, motion=%s", brightness, changed_percentage, motion)

                previous_gray = gray
                previous_brightness = brightness
                next_detection_time = now + DETECTION_INTERVAL

            if motion:
                last_motion_time = now
                if not recording:
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    output_file = args.output_dir / f"{timestamp}.mp4"
                    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
                    writer = cv2.VideoWriter(str(output_file), fourcc, FPS, (actual_width, actual_height))
                    if not writer.isOpened():
                        logging.error("Could not create video file: %s", output_file)
                        writer = None
                        continue
                    recording = True
                    recording_started_at = now
                    logging.info("Recording started: %s", output_file)

            if recording:
                writer.write(frame)
                if now - last_motion_time >= args.no_motion_time:
                    writer.release()
                    writer = None
                    recording = False
                    duration = now - recording_started_at
                    logging.info("Recording stopped: duration %.1f s, no motion for %.1f s.", duration, args.no_motion_time)

    except KeyboardInterrupt:
        logging.info("Stopping due to Ctrl+C.")
    finally:
        if writer is not None:
            writer.release()
        cap.release()
        cv2.destroyAllWindows()
        logging.info("Door camera motion detector stopped.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(parse_args()))
