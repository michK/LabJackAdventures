#!/usr/bin/env python3
"""
Rotary Encoder Reader via LabJack T4

Reads a C38S6G5-1000Z-G24N incremental rotary encoder (1000 PPR, ABZ, NPN
open collector output) using the T4's hardware quadrature decoder (DIO_EF).

4x decoding: 4000 counts per revolution.

Wiring:
    Encoder Wire    ->  LabJack T4 Pin     Notes
    Red (Vcc)       ->  VS (5V)
    Black (0V)      ->  GND
    Green (A Phase) ->  FIO4               pull-up 4.7k-10k to VS
    White (B Phase) ->  FIO5               pull-up 4.7k-10k to VS
    Gray (Z Phase)  ->  EIO2 (DIO10)       pull-up 4.7k-10k to VS
    Shield          ->  GND

    NPN open collector outputs require external pull-up resistors to VS
    on A, B, and Z lines.

Pin safety — these pins are used by other sensors and must NOT be touched:
    AIN0            ->  EI1022 temperature probe
    FIO6            ->  SPI CLK (MAX6675)
    FIO7            ->  SPI MISO (MAX6675)
    EIO0 (DIO8)     ->  SPI CS (MAX6675)
    EIO1 (DIO9)     ->  SPI MOSI (MAX6675, assigned)

Dependencies:
    pip install labjack-ljm
"""

import time
from datetime import datetime

from labjack import ljm


# --- Quadrature Configuration ---
PHASE_A_DIO = 4     # FIO4 (DIO4) — must be even number of an even/odd pair
PHASE_B_DIO = 5     # FIO5 (DIO5) — must be the next (odd) DIO
Z_PHASE_DIO = 10    # EIO2 (DIO10)

PULSES_PER_REV = 1000   # Encoder resolution
COUNTS_PER_REV = 4000   # 4x decoding: 4 counts per pulse


def quadrature_setup(handle):
    """Configure DIO_EF hardware quadrature decoding on FIO4/FIO5 with Z on EIO2."""
    a = PHASE_A_DIO
    b = PHASE_B_DIO

    # Disable DIO_EF on both channels before configuring
    ljm.eWriteName(handle, f"DIO{a}_EF_ENABLE", 0)
    ljm.eWriteName(handle, f"DIO{b}_EF_ENABLE", 0)

    # Set feature index to 10 (Quadrature In) on both channels
    ljm.eWriteName(handle, f"DIO{a}_EF_INDEX", 10)
    ljm.eWriteName(handle, f"DIO{b}_EF_INDEX", 10)

    # CONFIG_A: Z-phase mode (0=off, 1=on, 3=one-shot)
    # Enable Z-phase to reset count once per revolution
    ljm.eWriteName(handle, f"DIO{a}_EF_CONFIG_A", 1)

    # CONFIG_B: DIO number for Z-phase input
    ljm.eWriteName(handle, f"DIO{a}_EF_CONFIG_B", Z_PHASE_DIO)

    # Enable quadrature on both channels
    ljm.eWriteName(handle, f"DIO{a}_EF_ENABLE", 1)
    ljm.eWriteName(handle, f"DIO{b}_EF_ENABLE", 1)


def read_quadrature(handle):
    """Read the current quadrature count (signed 32-bit, 4x decoded).

    Returns:
        (count, errors)
        count: signed integer, increments CW, decrements CCW
        errors: number of edge-rate errors since last read
    """
    a = PHASE_A_DIO
    count = ljm.eReadName(handle, f"DIO{a}_EF_READ_A")
    errors = ljm.eReadName(handle, f"DIO{a}_EF_READ_B")
    # READ_A returns unsigned 32-bit; interpret as signed 2's complement
    count = int(count)
    if count >= 0x80000000:
        count -= 0x100000000
    return count, int(errors)


def read_and_reset_quadrature(handle):
    """Read the current quadrature count and reset it to zero.

    Returns:
        (count, errors)
    """
    a = PHASE_A_DIO
    count = ljm.eReadName(handle, f"DIO{a}_EF_READ_A_AND_RESET")
    errors = ljm.eReadName(handle, f"DIO{a}_EF_READ_B")
    count = int(count)
    if count >= 0x80000000:
        count -= 0x100000000
    return count, int(errors)


def count_to_degrees(count):
    """Convert quadrature count to angular position in degrees."""
    return (count % COUNTS_PER_REV) / COUNTS_PER_REV * 360.0


def count_to_revolutions(count):
    """Convert quadrature count to total revolutions."""
    return count / COUNTS_PER_REV


def main():
    handle = None
    try:
        handle = ljm.openS("T4", "ANY", "ANY")
        info = ljm.getHandleInfo(handle)
        print(f"Connected to LabJack T4 (serial: {info[2]})")

        quadrature_setup(handle)
        print(f"Quadrature input configured: A=FIO{PHASE_A_DIO}, "
              f"B=FIO{PHASE_B_DIO}, Z=DIO{Z_PHASE_DIO}")
        print(f"Encoder: {PULSES_PER_REV} PPR, {COUNTS_PER_REV} counts/rev (4x decoding)")

        # Initial read to clear any startup counts
        read_and_reset_quadrature(handle)
        time.sleep(0.1)

        print()
        print("Rotary Encoder Reader (LabJack T4)")
        print("-" * 65)

        total_errors = 0

        while True:
            count, errors = read_quadrature(handle)
            total_errors += errors
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            degrees = count_to_degrees(count)
            revs = count_to_revolutions(count)

            line = (f"{now} | Count: {count:>8d} | "
                    f"Pos: {degrees:6.2f}\u00b0 | Revs: {revs:>8.2f}")

            if total_errors > 0:
                line += f" | Errors: {total_errors}"

            print(line, flush=True)
            time.sleep(0.1)

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
