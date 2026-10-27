# door-camera

A camera mounted on the **inside of an apartment door, looking through the door peephole** to see the hallway.

## Physical setup

- The camera lens is placed as close as possible to the inner side of the peephole, pointing into it. The camera sees the hallway *through* the peephole optics.
- Consequences for image processing:
  - The useful image is a small, roughly circular area in the middle of the frame, with heavy fisheye/barrel distortion from the peephole lens. Everything around it is dark (the inside of the peephole and the door).
  - Expect vignetting and low light reaching the sensor. Cropping/ROI around the peephole circle, and possibly undistortion, are relevant.
  - The mount position can shift slightly, so don't hard-code the circle position without a way to calibrate it.
- Hallway lighting conditions:
  - Often **pitch black** (no window), sometimes with windows, so daylight levels vary.
  - Hallway lights are switched on by a **motion detector** in the hallway. A sudden jump in brightness often means someone is there, but the camera must handle the fast transition from dark to lit (auto-exposure/AWB settling time).
  - Without light the camera sees nothing useful unless an IR source is added (see the IR filter note below).

## Hardware

- **Host:** Raspberry Pi 5 running **Raspberry Pi OS (64-bit)** (the recommended image, not a Yocto build for now).
  - The Pi is always **headless** (no screen): everything is done over SSH, never rely on a preview window or a desktop (always pass `-n` to `rpicam-*`).
  - The Pi 5 has **no hardware H.264 encoder**: video encoding is done in software (libav/x264), so watch CPU load.
- **Capture format:** always **1920 x 1080 at 30 FPS** (`--width 1920 --height 1080 --framerate 30`), for stills, recordings and streaming. This is a native OV5647 sensor mode.
- **Streaming:** keep it simple. The Pi serves the stream on its own address with `rpicam-vid --listen -o tcp://0.0.0.0:8888` (raw H.264 over TCP, one viewer at a time). No multicast, and don't push the stream to a fixed receiver address. VLC is **not** used on the Pi: it is only what users typically run on their own machine to watch the stream (`tcp/h264://<pi-ip>:8888`). Plain RTP was dropped because it is push-only. A viewer can't connect to the Pi over RTP without an RTSP server, which would be extra software on the Pi.
- **Camera:** innomaker 5MP camera module, OmniVision **OV5647** sensor, connected to the RPi 5 over MIPI CSI-2.
  - Sensor: 5 MP, 2592 x 1944 stills, 1/4" optical format, 1.4 µm pixels.
  - Video modes: 1080p30, 720p60, 640x480p60/90.
  - Lens: interchangeable **M12x0.5** lens, adjustable focus. The stock lens is listed as FOV 90° diagonal (about 72° horizontal).
  - IR filter: the product is listed as "M12 lens with IR filter", so it is probably **not** sensitive to IR light. Swapping to an M12 lens without an IR-cut filter would make IR illumination usable in the dark. Unverified; check the actual lens.
  - Board: 36 x 36 mm, 4 mounting holes.
  - Connection: the RPi 5 uses 22-pin 0.5 mm pitch CSI connectors, while the camera board uses the classic 15-pin 1 mm connector, so a 15-to-22-pin adapter cable is needed.
- Software stack on the Pi: the OV5647 is supported by the mainline kernel driver and **libcamera** (`rpicam-apps`, `picamera2` in Python). On the RPi 5, the image pipeline is the PiSP (Pi 5 ISP), not the legacy MMAL/V4L2 camera stack, so `raspistill`/`raspivid` and the legacy camera interface don't work.
  - Capture/record/stream commands using only `rpicam-apps` are documented in `README.md` (Usage section). Keep them in sync when changing the setup.
  - If the camera isn't detected automatically: `camera_auto_detect=0` and `dtoverlay=ov5647` (with `,cam0` if plugged into the CAM0 port) in `/boot/firmware/config.txt`.

## Repository layout

- `cad/`: the 3D-printed camera support that holds the camera in front of the peephole.
  - `door_camera.FCStd`: FreeCAD source model (edit this one).
  - `door_camera.stl`: exported mesh for printing. Re-export it from FreeCAD whenever the model changes, and commit both together.
  - Binary files: don't try to edit them as text.
- `soft/`: software running on the Raspberry Pi (work in progress).

## Conventions

- Python is the main language for the camera software (`picamera2` / libcamera). Use C when performance or low-level access requires it.
- A Python virtualenv lives in `.venv/` (git-ignored).
- Commit messages use an area prefix: `cad:`, `soft:`, etc.
