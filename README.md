# gsv86lib

[![PyPI version](https://img.shields.io/pypi/v/gsv86lib.svg)](https://pypi.org/project/gsv86lib/)
[![Downloads](https://img.shields.io/pypi/dm/gsv86lib.svg)](https://pypistats.org/packages/gsv86lib)
[![License](https://img.shields.io/pypi/l/gsv86lib.svg)](LICENSE)

`gsv86lib` is a Python package that provides a convenient interface to the  
**ME-Systeme GSV-8 and GSV-6** measurement amplifier via serial communication.

It is based on the original ME-Systeme Python library (`gsv8pypi_python3`) and
repackages it as a modern Python package with a proper module namespace and
relative imports, so it can be installed and reused across multiple projects. 
It is suitable for both standard measurement tasks and high-frequency data 
acquisition up to **12 kHz**.

Typical use cases:

- Reading strain gauge data from a GSV-8
- Continuous streaming with `StartTransmission()`
- Triggering digital I/O based on thresholds
- Building custom GUIs or data logging tools

---

## Features

- Pure Python, no platform-specific DLLs required
- Serial communication (USB-CDC, virtual COM port)
- Access to the full GSV-8/6 feature set:
  - Measurement values for up to 8 channels
  - Data rate configuration
  - Start/Stop transmission
  - Digital I/O configuration
  - Thresholds and trigger functions
  - CSV recording helpers (from original library)
- Designed for high-frequency measurements up to **12 kHz**
- Usable on Windows and Linux

---

## Project stats & maturity

`gsv86lib` is a focused Python library for interfacing with ME-Systeme
GSV-8 and GSV-6 measurement amplifiers.

The project is actively maintained and distributed via PyPI.
Download statistics are publicly available via pypistats.org 
(https://pypistats.org/packages/gsv86lib) and provide an 
indication of usage trends within the Python ecosystem.

Please note:
- PyPI download numbers represent package download events, not unique users
- Automated systems (CI, testing, virtual environments) may increase counts

The library is primarily intended for engineering, measurement, and
industrial applications where reliability, transparency, and long-term
maintainability are more important than mass adoption metrics.

## Installation

`gsv86lib` is published on PyPI (https://pypi.org/project/gsv86lib/). So you can install it with

```bash
pip install gsv86lib
```
 
Or you can install it directly from the Git repository:

```bash
pip install git+https://github.com/me-systeme/gsv86lib.git
```

### Updating to a New Version

When a new version is released, make sure to update explicitly:

```bash
pip install --upgrade gsv86lib
```
If you still see old behavior after upgrading, pip may be using cached wheels.
In this case, force a clean install:

```bash
pip install --upgrade --no-cache-dir gsv86lib
```

### Verify Installed Version

You can verify the installed version with:

```bash
pip show gsv86lib
```

## Requirements

- Python 3.8+
- `pyserial` (installed automatically as dependency)

## ⚠️ Measurement Data Type Support (Important Note)

Currently, support for different measurement data types is not fully implemented in `gsv86lib`.

While `float32` data is fully supported and recommended, the handling of other data types such as `int16` may be incomplete or lead to unexpected behavior depending on the device configuration.

### Recommendation

For reliable operation, it is strongly recommended to configure the device to use:

- **Data type: `float32`**

(e.g. via GSVmulti or device configuration tools)

### Need `int16` or Other Formats?

If your application requires `int16`, `int24`, or other data formats, please contact **ME-Systeme** directly.  
We can provide guidance or support depending on your specific use case and requirements.

This limitation will be addressed in future updates of the library.

## Basic Usage

```python
import time
from gsv86lib import gsv86

# Open GSV-8 device on given serial port
# Example: "COM3" on Windows, "/dev/ttyACM0" on Linux
# This is just an example. You need to set the COM port 
# and Baudrate depending on your device. 
# The default configuration of devices GSV 8 and GSV 6 are:
# GSV8: 115200
# GSV6: 230400
dev = gsv86("COM3", 115200)

# Optional: configure data rate (Hz)
dev.writeDataRate(50.0)

# Start continuous transmission
dev.StartTransmission()

time.sleep(0.2)

# Read a single measurement frame
measurement = dev.ReadValue()

# Access individual channels (1..8)
ch1 = measurement.getChannel1()
ch2 = measurement.getChannel2()

print("Channel 1:", ch1)
print("Channel 2:", ch2)

# Stop transmission when done
dev.StopTransmission()
``` 

You can build more complex applications on top of this, such as real-time
visualization, logging, or integration into test benches.

## High-Frequency Measurements (up to 12 kHz)

`gsv86lib` is designed for **continuous high-frequency data acquisition**
with sampling rates of up to **12,000 Hz**, depending on device configuration
and host system performance.

### How Performance is Measured

To evaluate performance, the library provides a benchmark example:

```bash
examples/benchmark.py
```

This script:

- Configures the device to a given sample rate (e.g. 500 Hz, 1000 Hz, …)
- Starts continuous transmission
- Uses `ReadMultiple()` in a worker thread to fetch batches of frames
- Measures the number of frames received within a fixed time window  
  (**starting from the first received frame**)

The benchmark intentionally:

- Discards the first non-empty read (synchronization phase)
- Measures **steady-state throughput**, not startup latency
- Uses an "effective rate" = `frames / elapsed_time`

### Example Results

Typical results on a standard Windows system (USB virtual COM port):

| Configured Rate | Measured Frames | Time (s) | Effective Rate |
|-----------------|----------------|----------|----------------|
| 500 Hz          | ~4960          | ~10.0    | ~495 Hz        |
| 1000 Hz         | ~9920          | ~10.0    | ~990 Hz        |

This corresponds to an accuracy of roughly **±1%**, which is expected for
a user-space acquisition loop.

### Important Notes

- The measured rate reflects **application-level throughput**, not the exact
  device transmission timing.
- Small deviations are caused by:
  - OS scheduling (`time.sleep`)
  - Python interpreter overhead
  - Serial driver buffering
- The first batch of received frames is **not counted**, as it may contain
  buffered data from before the measurement window.

### Recommendations for High-Rate Operation

For sampling rates ≥ 6 kHz (and especially near 12 kHz):

- Use `ReadMultiple()` instead of `ReadValue()`
- Keep `refresh_ms` small (e.g. 1–10 ms)
- Ensure `max_frames_per_call` is sufficiently large
- Avoid logging or printing inside the acquisition loop
- Process data in batches instead of per-frame

### Practical Considerations

At very high rates (e.g. ≥ 10 kHz), overall system performance depends on:

- CPU speed
- USB / serial driver efficiency
- Number of active channels
- Data processing in the application

For maximum performance and minimal overhead, consider:

- Running acquisition in a dedicated thread
- Minimizing work inside the read loop
- Offloading processing to another thread or process

### Comparison with the ME-Systeme Windows DLL

For comparison with the official ME-Systeme Windows DLL, see:

```bash
examples/benchmarkdll.py
```

Both implementations show comparable throughput under identical conditions.

### Important: Channel Configuration (`NUM_OBJECTS`)

When using the DLL benchmark (`examples/benchmarkdll.py`), make sure that
the constant `NUM_OBJECTS` matches the number of active measurement channels
configured on the device.

The DLL returns raw values, not frames. A "frame" consists of one value per
active channel. Therefore, the number of frames is calculated as:

```python
frames = values_read / NUM_OBJECTS
```


If `NUM_OBJECTS` is set incorrectly:

- The calculated number of frames will be wrong
- The reported effective rate will be misleading

#### Example

- 3 active channels → `NUM_OBJECTS = 3`
- 8 active channels → `NUM_OBJECTS = 8`

Make sure this value reflects the actual channel mapping of your device
(e.g. as configured via GSVmulti or other configuration tools).

## Logging

`gsv86lib` uses Python’s built-in `logging` module.
By default, the library does **not** emit any log output unless explicitly
enabled by the user.

This design ensures maximum performance, even at high data rates
(e.g. 6–12 kHz streaming).

### Enable Logging

To enable debug logging for `gsv86lib`, configure the logger:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```
For info loggings replace `DEBUG` by `INFO`.

### Performance Note

All debug log statements inside `gsv86lib` are guarded by:

```python
if logger.isEnabledFor(logging.DEBUG):
    logger.debug(...)
``` 

This avoids unnecessary string formatting and keeps overhead minimal,
even at very high sampling rates.

## API Overview

`gsv86lib` exposes the original ME-Systeme API, including (non-exhaustive):

- Measurement
  - `ReadValue()`
  - `ReadMultiple()`
  - `writeDataRate(frequency)`
  - `StartTransmission()`
  - `StopTransmission()`
- Digital I/O
  - `getDIOdirection()`, `setDIOdirection()`
  - `getDIOlevel()`, `setDIOlevel()`
  - `setDIOtype()`, `setInputToTaraInputForChannel()`, …
- Thresholds / Trigger
  - `readDIOthreshold()`, `writeDIOthreshold()`
  - `setOutputHighByThreshold()`, `setOutputHighIfInsideWindow()`, …
- Scaling and sensor configuration
  - `setUserScaleBySensor()`
  - Input type configuration (bridge, single-ended, temperature, …)

For a more detailed API reference, see the original ME-Systeme documentation
(e.g. `gsv86.html` / GSV-8PyPi 1.0.0 documentation or `documentation.pdf`) or the docstrings in the
source files.

## Project Structure

Typical layout of this package:

```text
gsv86lib/
├─ pyproject.toml
├─ README.md
├─ LICENSE
└─ src/
   └─ gsv86lib/
      ├─ __init__.py
      ├─ gsv86.py
      ├─ CSVwriter.py
      ├─ GSV_BasicMeasurement.py
      ├─ GSV_Exceptions.py
      ├─ GSV6_AnfrageCodes.py
      ├─ GSV6_BasicFrameType.py
      ├─ GSV6_ErrorCodes.py
      ├─ GSV6_FrameRouter.py
      ├─ GSV6_MessFrameHandler.py
      ├─ GSV6_Protocol.py
      ├─ GSV6_SeriallLib.py
      ├─ GSV6_UnitCodes.py
      └─ ThreadSafeVar.py
```
The public entry point for user code is `gsv86lib.gsv86`.

## License

This package is derived from the original ME-Systeme GSV-8 Python library.
Please refer to the license information provided by ME-Systeme and add your
own license information here as appropriate for your project.