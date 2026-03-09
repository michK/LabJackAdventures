# LabJackAdventures
The [LabJack](https://labjack.com/) is a general purpose data acquisition device that can be used for many different things on top of acquiring data, including:
- Measuring analog voltage signals
- Outputting analog voltage signals
- Reading and writing digital signals
- Generating clock signals of different frequencies
- Using high speed timers and counters, which can in turn be used for:
    - Outputting PWM signals at different frequencies and duty cycles
    - Measuring signal frequencies
    - Reading encoders (rotary encoders for input or shaft encoders for motor speed)
    - Many more things ...

LabJack has many example scripts of how to use their devices in many different use cases, and their [website](https://labjack.com/) and [Github repo](https://github.com/labjack) are great resources.

Over time I've used LabJacks for various different things and thought I would throw my scripts into this repo; maybe someone will find it useful.

I've only used the U3-HV and T4 models, and although they are programmed with different APIs, for the most part everything I've been able to do with the T4 I've also been able to do with the U3, so in my opinion the U3 is good enough for most applications unless you want to use the LJ as a stand-alone device in which case you need the Lua scripting functionality of the T-series.

Questions, suggestions and bug notifications are welcome, just post an 'issue'

---

## Scripts

### U3 (`u3` library — `pip install LabJackPython`)

#### `U3/Analog/`
| Script | Description |
|--------|-------------|
| `analog_in.py` | Read a calibrated analog voltage from AIN channels |
| `analog_out.py` | Output a voltage on DAC0 or DAC1 via Modbus register |
| `stream.py` | Stream two analog channels at a fixed scan rate |

#### `U3/Frequency/`
| Script | Description |
|--------|-------------|
| `calc_freq.py` | Measure signal frequency on FIO4 using timer period mode |
| `calc_rpm.py` | Same as above but converts to RPM for a brushless motor |

#### `U3/PWM/`
| Script | Description |
|--------|-------------|
| `pwm_single.py` | Output a single PWM signal at a fixed duty cycle |
| `pwm_esc.py` | PWM for an ESC (brushless motor controller), duty cycle mapped from throttle range |
| `pwm_sweep.py` | Sweep PWM duty cycle from ~0% to 100% in steps |

#### `U3/Stepper/`
| Script | Description |
|--------|-------------|
| `stepper_control.py` | Run a stepper motor with the DRV8825 driver at a fixed RPM, forward then reverse |
| `stepper_rampup.py` | Ramp a stepper motor up to speed in increments to avoid missed steps |
| `stepper_tools.py` | Helper: `ramp_up()` function used by `stepper_rampup.py` |

> Speed is set by PWM **frequency** (not duty cycle). Only discrete speeds are achievable due to integer clock divisors (48 MHz base / 256 / divisor).

#### `U3/Motor_PID/`
| Script | Description |
|--------|-------------|
| `main.py` | PID speed controller for a brushless motor; uses Timer0 for PWM output, Timer1 for RPM feedback |
| `setup.py` | Helper: initializes the LabJack with two timers (PWM + period measurement) |
| `lj_tools.py` | Helper: `calc_freq()` using timer period measurement |

#### `U3/Temperature_Logging/`
| Script | Description |
|--------|-------------|
| `log_temp.py` | Read a voltage-based temperature sensor and append a timestamped reading to a CSV log file. Intended to run as a cron job on a Raspberry Pi |
| `plot_temperature.py` | Plot multi-room temperature logs with time-aligned overlays |
| `plot_temperature_single.py` | Plot a single-channel temperature log file (`python plot_temperature_single.py <file>`) |
| `plot_temperature_mult.py` | Plot a two-channel temperature log file (`python plot_temperature_mult.py <file>`) |

#### `U3/Temp_Hum_Probe/`
| Script | Description |
|--------|-------------|
| `temp_hum_probe.py` | Bit-bang the start-communication sequence for a DHT-style temperature/humidity probe using digital IO |

---

### T4 (`labjack-ljm` library — `pip install labjack-ljm`)

#### `T4/Environmental/`
| Script | Description |
|--------|-------------|
| `bme280_reader.py` | Read temperature, humidity, and pressure from a BME280 sensor over I2C. Includes full calibration compensation |

#### `T4/Encoders/`
| Script | Description |
|--------|-------------|
| `encoder_reader.py` | Read a quadrature incremental encoder using the T4's hardware DIO_EF decoder (4x decoding, Z-phase reset support) |

#### `T4/Thermocouple/`
| Script | Description |
|--------|-------------|
| `max6675_reader.py` | Read thermocouple temperature from a MAX6675 amplifier (SPI) and ambient temperature from an EI1022 probe (analog). Includes auto-calibration of TC offset against the ambient probe at startup |
