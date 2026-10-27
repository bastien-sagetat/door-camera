# Camera tuning

`ov5647_door.json` is a libcamera tuning file for the OV5647 on the Raspberry Pi 5 (PiSP). Use it with `--tuning-file`.

It is a copy of the stock `/usr/share/libcamera/ipa/rpi/pisp/ov5647.json` (libcamera v0.7.2+rpt20260817, BSD-2-Clause) with one addition: a `custom` exposure mode in the first `rpi.agc` channel.

| Mode     | Exposure times (µs)                   | Gains                          |
|----------|---------------------------------------|--------------------------------|
| `normal` | `[ 100, 10000, 30000, 50000, 66666 ]` | `[ 1.0, 1.5, 2.0, 4.0, 8.0 ]`  |
| `custom` | same as `normal`                      | `[ 1.0, 1.5, 2.0, 4.0, 24.0 ]` |

At 30 FPS, the exposure time is capped at about 33 ms by the frame period. In a dark hallway, the stock modes then hit their 8x gain ceiling and the image stays dark. The `custom` mode lets auto-exposure raise the analogue gain up to 24x. The image is brighter but noisier, so use it with `--denoise cdn_hq`:

```sh
rpicam-vid ... --tuning-file soft/tuning/ov5647_door.json --exposure custom --denoise cdn_hq
```

Raise or lower the last gain value to trade brightness against noise. Check the effect with `--metadata meta.json --metadata-format json` (`ExposureTime`, `AnalogueGain`, `Lux`).

When `rpicam-apps`/libcamera is upgraded on the Pi, diff the stock file against this one and carry the `custom` block over to the new version.
