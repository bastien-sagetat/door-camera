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

Install Python and virtual-environment support:

```bash
sudo apt update
sudo apt install python3 python3-venv python3-pip
```

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the Python packages:

```bash
pip install opencv-python numpy
```

Or using `requirements.txt`:

```bash
pip install -r requirements.txt
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

In order to have a stable 30 FPS, the dynamic framerate of the camera should be disabled.

Listing the camera's settings:

```bash
v4l2-ctl --all --device /dev/v4l/by-id/usb-Innomaker_Innomaker-U20CAM-1080p-WDR_SN0001-video-index0
```

Disabling the dynamic framerate of the camera:

```bash
v4l2-ctl --device /dev/v4l/by-id/usb-Innomaker_Innomaker-U20CAM-1080p-WDR_SN0001-video-index0 --set-ctrl=exposure_dynamic_framerate=0
```

Check that the setting is now disabled:

```bash
v4l2-ctl --device=/dev/v4l/by-id/usb-Innomaker_Innomaker-U20CAM-1080p-WDR_SN0001-video-index0 --get-ctrl=exposure_dynamic_framerate
```

### Creating a udev rule for disabling the dynamic framerate

The following udev rules can be used to disable the dynamic framerate setting, everytime the camera is plugged-in.

Create the udev rule:

```bash
sudo nano /etc/udev/rules.d/99-innomaker-camera.rules
```

```text
ACTION=="add", SUBSYSTEM=="video4linux", KERNEL=="video[0-9]*", ATTRS{idVendor}=="0c45", ATTRS{idProduct}=="6368", RUN+="/usr/bin/v4l2-ctl --device=/dev/%k --set-ctrl=exposure_dynamic_framerate=0"
```

*99-innomaker-camera.rules content*

Then reload the udev rules to apply the change:

```bash
sudo udevadm control --reload-rules
```

## Autostart the door-camera script at boot

The following scripts and systemd unit files allows the camera-door Python script
to be setup and to be executed everytime the system boots.

Copy the setup systemd service:

```bash
sudo cp door-camera-setup.service /etc/systemd/system/
```

Copy the setup shell script and make it executable:

```bash
sudo cp setup.sh /opt/door-camera/
```

```bash
sudo chmod +x /opt/door-camera/setup.sh
```

Copy the door-camera systemd service:

```bash
sudo cp door-camera.service /etc/systemd/system/
```

Copy the door-camera-http systemd service (can be used to access the recordings remotly):

```bash
sudo cp door-camera-http.service /etc/systemd/system/
```

> [!NOTE]
> The HTTP server can be accessed from within the local network, by using the following url in a web browser:
> http://raspberrypi.local:8000/

Reload systemd:

```bash
sudo systemctl daemon-reload
```

Enable the services:

```bash
sudo systemctl enable door-camera-setup.service
```

```bash
sudo systemctl enable door-camera.service
```

```bash
sudo systemctl enable door-camera-http.service
```

Also, the door-camera service runs using the `door-camera-user` user.
This user needs to be created, and must have access to the camera:

```bash
sudo useradd --create-home --user-group --shell /usr/sbin/nologin door-camera-user
```

```bash
sudo usermod -aG video door-camera-user
```

## Services status and logs

Check the services status:

```bash
sudo systemctl status door-camera-setup.service
```

```bash
sudo systemctl status door-camera.service
```

```bash
sudo systemctl status door-camera-http.service
```

Get the services logs:

```bash
sudo journalctl -u door-camera-setup.service -f
```

```bash
sudo journalctl -u door-camera.service -f
```

```bash
sudo journalctl -u door-camera-http.service -f
```
