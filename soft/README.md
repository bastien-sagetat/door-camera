# Door camera Motion Detector

## Purpose

`door_camera.py` uses a USB camera mounted behind a door peephole to detect motion in a hallway.

When motion is detected, it starts recording an MP4 video. Recording stops after a configurable period with no motion.

The hallway light is expected to turn on automatically when someone enters. The script detects large dark/light transitions and ignores them, so the light turning on or off does not by itself start a recording.

Motion detection runs every **100 ms**, while recording continues at the camera's configured FPS.

## Requirements

- Python 3
- OpenCV
- NumPy
- USB UVC camera (such as the InnoMaker 1080P / PS5268)
- 1920×1080 camera support

## Installation

### Ubuntu Linux

Install Python and virtual-environment support:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Create a virtual environment:

```bash
python3 -m venv ~/door_-_camera-venv
source ~/door_camera-venv/bin/activate
```

Install the Python packages:

```bash
pip install opencv-python numpy
```

### Raspberry Pi OS

The simplest option is to use the system packages:

```bash
sudo apt update
sudo apt install python3-opencv python3-numpy
```

## Setup


Make the script executable if desired:

```bash
chmod +x door_camera.py
```

The script automatically looks for an InnoMaker / PS5268 camera under `/dev/v4l/by-id`.

If automatic detection does not find it, camera `0` is used as a fallback.

## Basic Usage

Run with the default settings:

```bash
./door_camera.py
```

Recordings are saved by default to:

```text
~/recordings/
```

Files are named using the date and time, for example:

```text
2026-10-05_18-42-31.mp4
```

## Useful Options

Show all available options:

```bash
./door_camera.py --help
```

Examples:

```bash
./door_camera.py --no-motion-time 15
```

Stop recording after 15 seconds without motion.

```bash
./door_camera.py --motion-threshold 1.5
```

Make motion detection more sensitive.

```bash
./door_camera.py --debug
```

Print brightness and motion information to help tune the thresholds.

## Stopping the Script

Press:

```text
Ctrl+C
```

The current recording is closed cleanly before the program exits.

## Disabling the dynamic framerate

In order to have a stable 30 FPS.

```bash
v4l2-ctl -d /dev/v4l/by-id/<innomaker_camera> --set-ctrl=exposure_dynamic_framerate=0
```
