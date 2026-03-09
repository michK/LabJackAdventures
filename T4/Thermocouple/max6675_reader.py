#!/usr/bin/env python3
"""
Temperature Reader via LabJack T4

Reads thermocouple temperature from a MAX6675 amplifier (SPI) and
ambient temperature from a LabJack EI1022 probe (analog, AIN0).

Wiring:
    MAX6675 Pin     ->  LabJack T4 Pin
    VCC             ->  VS (3.3V)
    GND             ->  GND
    CLK (SCK)       ->  FIO6
    DO (MISO)       ->  FIO7
    CS              ->  EIO0

    EI1022 Pin      ->  LabJack T4 Pin
    +5V (red)       ->  VS (5V)
    GND (black)     ->  GND
    Signal (white)  ->  AIN0

Dependencies:
    pip install labjack-ljm
"""

import time
from datetime import datetime

from labjack import ljm


# --- SPI Configuration (MAX6675) ---
SPI_CLK_PIN = 6    # FIO6
SPI_MISO_PIN = 7   # FIO7
SPI_CS_PIN = 8     # EIO0 (DIO8)
SPI_MOSI_PIN = 9   # EIO1 — unused, MAX6675 is read-only

# --- Analog Configuration (EI1022) ---
EI1022_AIN = "AIN0"


def read_ei1022(handle):
    """Read the EI1022 temperature probe on AIN0.

    The EI1022 outputs 10 mV per degree Kelvin.
    Conversion: temp_C = 100.0 * voltage - 273.15

    Returns temperature in degrees Celsius.
    """
    voltage = ljm.eReadName(handle, EI1022_AIN)
    temp_c = 100.0 * voltage - 273.15
    return temp_c


def spi_setup(handle):
    """Configure LabJack T4 SPI for MAX6675 thermocouple amplifier."""
    ljm.eWriteName(handle, "SPI_CS_DIONUM", SPI_CS_PIN)
    ljm.eWriteName(handle, "SPI_CLK_DIONUM", SPI_CLK_PIN)
    ljm.eWriteName(handle, "SPI_MISO_DIONUM", SPI_MISO_PIN)
    ljm.eWriteName(handle, "SPI_MOSI_DIONUM", SPI_MOSI_PIN)
    ljm.eWriteName(handle, "SPI_MODE", 0)              # Mode 0 (CPOL=0, CPHA=0)
    ljm.eWriteName(handle, "SPI_SPEED_THROTTLE", 0)    # Default speed
    ljm.eWriteName(handle, "SPI_OPTIONS", 0)            # Default options


def read_max6675(handle):
    """Read 16 bits from MAX6675 and parse thermocouple temperature.

    MAX6675 outputs 16 bits:
        Bit 15:    dummy sign bit (always 0)
        Bits 14-3: 12-bit thermocouple temperature (0.25 deg C resolution)
        Bit 2:     thermocouple input state (1 = open circuit)
        Bit 1:     device ID (always 0)
        Bit 0:     three-state

    Returns:
        (tc_temp_c, fault_str)
        If no fault: fault_str is None.
        If fault: tc_temp_c is None, fault_str describes the fault.
    """
    ljm.eWriteName(handle, "SPI_NUM_BYTES", 2)
    # Write 2 dummy bytes to clock in 2 bytes from MAX6675
    ljm.eWriteNameByteArray(handle, "SPI_DATA_TX", 2, [0x00, 0x00])
    ljm.eWriteName(handle, "SPI_GO", 1)
    raw = ljm.eReadNameByteArray(handle, "SPI_DATA_RX", 2)
    raw = [int(b) for b in raw]

    # Combine into 16-bit value
    word = (raw[0] << 8) | raw[1]

    # Check open thermocouple bit (bit 2)
    if word & (1 << 2):
        return None, "open circuit (no thermocouple detected)"

    # Temperature: bits 14-3, 12-bit unsigned, 0.25 deg C resolution
    tc_raw = (word >> 3) & 0x0FFF
    tc_temp_c = tc_raw * 0.25

    return tc_temp_c, None


def main():
    handle = None
    try:
        handle = ljm.openS("T4", "ANY", "ANY")
        info = ljm.getHandleInfo(handle)
        print(f"Connected to LabJack T4 (serial: {info[2]})")

        spi_setup(handle)

        # Allow sensors to stabilize
        time.sleep(0.5)

        # Calibrate TC offset using EI1022 as reference
        # Both sensors should be at the same ambient temperature at startup
        NUM_CAL_SAMPLES = 10
        CAL_INTERVAL = 0.5  # seconds between samples
        print(f"Calibrating TC offset ({NUM_CAL_SAMPLES} samples)...")
        ei_samples = []
        tc_samples = []
        for i in range(NUM_CAL_SAMPLES):
            ei_temp = read_ei1022(handle)
            tc_temp, fault = read_max6675(handle)
            ei_samples.append(ei_temp)
            if fault:
                print(f"  Sample {i+1}: EI1022={ei_temp:.2f}\u00b0C | TC: FAULT ({fault})")
            else:
                tc_samples.append(tc_temp)
                print(f"  Sample {i+1}: EI1022={ei_temp:.2f}\u00b0C | TC={tc_temp:.2f}\u00b0C",
                      flush=True)
            if i < NUM_CAL_SAMPLES - 1:
                time.sleep(CAL_INTERVAL)

        if not tc_samples:
            print("WARNING: No valid TC readings during calibration, offset = 0.0")
            tc_offset = 0.0
        else:
            ei_avg = sum(ei_samples) / len(ei_samples)
            tc_avg = sum(tc_samples) / len(tc_samples)
            tc_offset = ei_avg - tc_avg
            print(f"Calibration complete: EI1022 avg={ei_avg:.2f}\u00b0C, "
                  f"TC avg={tc_avg:.2f}\u00b0C, offset={tc_offset:+.2f}\u00b0C",
                  flush=True)

        print()
        print("Temperature Reader (LabJack T4)")
        print("-" * 65)

        while True:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Read EI1022 ambient probe
            ei_temp_c = read_ei1022(handle)
            ei_temp_f = ei_temp_c * 9.0 / 5.0 + 32.0

            # Read MAX6675 thermocouple
            tc_temp, fault = read_max6675(handle)

            line = f"{now} | Ambient: {ei_temp_c:.1f}\u00b0C ({ei_temp_f:.1f}\u00b0F)"
            if fault:
                line += f" | TC: FAULT ({fault})"
            else:
                tc_cal = tc_temp + tc_offset
                tc_f = tc_cal * 9.0 / 5.0 + 32.0
                line += f" | TC: {tc_cal:.1f}\u00b0C ({tc_f:.1f}\u00b0F)"

            print(line, flush=True)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except ljm.LJMError as e:
        print(f"LabJack error: {e}")
    finally:
        if handle is not None:
            ljm.close(handle)
            print("LabJack connection closed.")


if __name__ == "__main__":
    main()
