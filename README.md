# door-camera

A camera that sees through a door peephole.

The camera is mounted on the inside of the door, with its lens placed right against the peephole, so it looks through the peephole optics and sees the hallway outside. It is driven by a Raspberry Pi 5.

The hallway is often completely dark, and its lights are switched on by a motion detector. The camera has to cope with both darkness and sudden changes in lighting.

## Hardware

- Raspberry Pi 5
- innomaker OV5647 5MP camera module with M12 lens, connected to the Pi's CSI port (needs a 15-pin to 22-pin adapter cable on the Pi 5)
- 3D-printed support that holds the camera in front of the peephole

## Setup

The Pi runs **Raspberry Pi OS (64-bit)**, the recommended image. The camera tools (`rpicam-apps`, based on libcamera) come preinstalled.

1. With the Pi powered off, connect the camera to one of the CSI ports (CAM0 or CAM1).
2. Boot, then check that the camera is detected:

   ```sh
   rpicam-hello --list-cameras
   ```

   It should list an `ov5647` sensor. If it doesn't, force the overlay in `/boot/firmware/config.txt` and reboot:

   ```ini
   camera_auto_detect=0
   dtoverlay=ov5647        # add ",cam0" if the camera is on the CAM0 port
   ```

3. Focus is manual: rotate the M12 lens to adjust it, using captured frames to check the result.

## Usage

The Pi is **headless** (no screen): run the commands over SSH. `-n` disables the preview window.

All captures use **1920 x 1080 at 30 FPS** (a native OV5647 sensor mode). Times given to `-t` are in milliseconds.

Commands are run from the repository root on the Pi. They use the tuning file in [`soft/tuning/`](soft/tuning/README.md), whose `custom` exposure mode allows more gain than the stock modes, so the image stays usable in low light.

### Capture a frame

```sh
rpicam-still -n --width 1920 --height 1080 \
  --tuning-file soft/tuning/ov5647_door.json --exposure custom --denoise cdn_hq -o frame.jpg
```

Add `--immediate` to skip the auto-exposure settling delay, or `-e png -o frame.png` for a lossless image.

### Record a video

The Pi 5 has no hardware H.264 encoder, so encoding is done in software via libav. Writing an `.mp4` makes the file playable directly.

```sh
# Record for 10 seconds
rpicam-vid -n --width 1920 --height 1080 --framerate 30 \
  --tuning-file soft/tuning/ov5647_door.json --exposure custom --denoise cdn_hq \
  -t 10000 --codec libav -o video.mp4

# Record until CTRL+C
rpicam-vid -n --width 1920 --height 1080 --framerate 30 \
  --tuning-file soft/tuning/ov5647_door.json --exposure custom --denoise cdn_hq \
  -t 0 --codec libav -o video.mp4
```

### Stream over the network

The Pi serves the stream itself on TCP port 8888, using only `rpicam-vid` (nothing extra to install). The user connects to the Pi's own address with VLC.

Start the stream on the Pi:

```sh
while true; do
  rpicam-vid -n --width 1920 --height 1080 --framerate 30 \
    --tuning-file soft/tuning/ov5647_door.json --exposure custom --denoise cdn_hq \
    -t 0 --inline --listen -o tcp://0.0.0.0:8888
  sleep 1
done
```

`--listen` makes `rpicam-vid` wait for a viewer to connect before it starts streaming. `--inline` repeats the H.264 headers in the stream. `rpicam-vid` exits when the viewer disconnects, so the loop restarts it for the next one (CTRL+C stops the loop).

To watch it, open VLC on a machine on the local network, choose *Media > Open Network Stream*, and enter:

```
tcp/h264://<pi-ip>:8888
```

or from a terminal:

```sh
vlc --h264-fps=30 --network-caching=200 tcp/h264://<pi-ip>:8888
```

A raw H.264 stream carries no timestamps: `--h264-fps` must match the Pi's `--framerate` (VLC assumes 25 otherwise). `--network-caching` lowers the latency (in ms).

Limitations:
- One viewer at a time.
- `rpicam-vid` exits when the viewer disconnects (restarted by the loop above).

## Repository layout

| Path           | Content                                                        |
|----------------|----------------------------------------------------------------|
| `cad/`         | Camera support: FreeCAD source (`.FCStd`) and printable `.stl` |
| `soft/`        | Software running on the Raspberry Pi (work in progress)        |
| `soft/tuning/` | libcamera tuning file for the camera                           |

## Status

Work in progress: the camera mount is designed and printed. The software is not written yet.

## License

See [LICENSE](LICENSE).
