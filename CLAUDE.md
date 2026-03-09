# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A collection of Python scripts for controlling hardware via LabJack data acquisition devices. Scripts are standalone — no build system, no tests, no package structure.

| Device | Library | Install |
|--------|---------|---------|
| U3-HV | `u3` | `pip install LabJackPython` |
| T4 | `labjack.ljm` | `pip install labjack-ljm` |

## Running Scripts

```bash
python U3/Stepper/stepper_control.py
python T4/Thermocouple/max6675_reader.py
```

All scripts require a physical LabJack device connected via USB.

## Repository Structure

```
U3/
  Analog/          # analog_in.py, analog_out.py, stream.py
  Frequency/       # calc_freq.py, calc_rpm.py
  PWM/             # pwm_single.py, pwm_esc.py, pwm_sweep.py
  Stepper/         # stepper_control.py, stepper_rampup.py, stepper_tools.py
  Motor_PID/       # main.py + setup.py + lj_tools.py (multi-file project)
  Temperature_Logging/  # log_temp.py + plot_temperature*.py
  Temp_Hum_Probe/  # temp_hum_probe.py
T4/
  Environmental/   # bme280_reader.py (I2C)
  Encoders/        # encoder_reader.py (quadrature DIO_EF)
  Thermocouple/    # max6675_reader.py (SPI + analog)
```

## Key U3 API Patterns

- `d = u3.U3()` — open device; always call `d.close()` at end
- `d.configTimerClock(TimerClockBase, TimerClockDivisor)` — base clock is 48 MHz; effective frequency = 48e6 / (256 × divisor)
- `d.configIO(NumberOfTimersEnabled=N, TimerCounterPinOffset=4)` — enables timers on FIO pins starting at offset
- `d.writeRegister(address, value)` — Modbus: 5000=DAC0, 5002=DAC1
- `d.getFeedback(u3.Timer0Config(TimerMode=M, Value=V))` — configure timer; Mode 0=PWM, Mode 1=freq-based PWM, Mode 2=period measurement
- `d.spi([...])` — SPI transaction; default pins FIO4–FIO7

## Key T4 API Patterns

- `handle = ljm.openS("T4", "ANY", "ANY")` — open device; always call `ljm.close(handle)`
- `ljm.eWriteName(handle, "NAME", value)` / `ljm.eReadName(handle, "NAME")` — register-based access
- SPI: configure via `SPI_CS_DIONUM`, `SPI_CLK_DIONUM`, etc., then `SPI_GO`
- I2C: configure via `I2C_SDA_DIONUM`, `I2C_SCL_DIONUM`, etc., then `I2C_GO`
- Quadrature encoder: `DIO{N}_EF_INDEX=10`, `DIO{N}_EF_ENABLE=1`, read via `DIO{N}_EF_READ_A`

## Multi-file Projects

**Motor_PID**: Run `main.py` from within `U3/Motor_PID/` — it imports `setup` and `lj_tools` from the same directory.

**Temperature_Logging**: `log_temp.py` is designed to run as a cron job on a Raspberry Pi; the path `/home/pi/LabJack/Temperature_Log/temperature-log.txt` is hardcoded. Plot scripts take a filename as `sys.argv[1]`.
