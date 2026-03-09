#!/usr/bin/env python3
"""
BME280 Environmental Sensor Reader via LabJack T4

Reads temperature, humidity, and pressure from a BME280 sensor over I2C.

Wiring:
    BME280 Pin      ->  LabJack T4 Pin
    VCC             ->  VS (3.3V)
    GND             ->  GND
    SDA             ->  FIO4
    SCL             ->  FIO5

Dependencies:
    pip install labjack-ljm
"""

import struct
import time
from datetime import datetime

from labjack import ljm


# --- I2C Configuration ---
SDA_PIN = 6   # FIO6
SCL_PIN = 7   # FIO7
I2C_SPEED = 65000  # ~100 kHz clock

# --- BME280 Registers ---
BME280_CHIP_ID_REG = 0xD0
BME280_CHIP_ID = 0x60
BME280_CTRL_HUM = 0xF2
BME280_CTRL_MEAS = 0xF4
BME280_CONFIG = 0xF5
BME280_DATA_START = 0xF7  # 8 bytes: press[3] temp[3] hum[2]

# Calibration register ranges
BME280_CALIB_TEMP_PRESS_START = 0x88  # 26 bytes (0x88–0xA1)
BME280_CALIB_HUM_H1 = 0xA1           # 1 byte
BME280_CALIB_HUM_START = 0xE1        # 7 bytes (0xE1–0xE7)


def i2c_setup(handle):
    """Configure LabJack T4 I2C on FIO4 (SDA) / FIO5 (SCL)."""
    ljm.eWriteName(handle, "I2C_SDA_DIONUM", SDA_PIN)
    ljm.eWriteName(handle, "I2C_SCL_DIONUM", SCL_PIN)
    ljm.eWriteName(handle, "I2C_SPEED_THROTTLE", I2C_SPEED)
    ljm.eWriteName(handle, "I2C_OPTIONS", 0)  # default options


def i2c_write(handle, addr, data):
    """Write bytes to an I2C device."""
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", addr)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", len(data))
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", len(data), data)
    ljm.eWriteName(handle, "I2C_GO", 1)
    ack = ljm.eReadName(handle, "I2C_ACKS")
    if ack != 0:
        raise IOError(f"I2C write NACK (acks register = {int(ack):#x})")


def i2c_read(handle, addr, register, num_bytes):
    """Write a register address then read num_bytes from an I2C device."""
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", addr)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", num_bytes)
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 1, [register])
    ljm.eWriteName(handle, "I2C_GO", 1)
    ack = ljm.eReadName(handle, "I2C_ACKS")
    if ack != 0:
        raise IOError(f"I2C read NACK at register {register:#x} (acks = {int(ack):#x})")
    data = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", num_bytes)
    return [int(b) for b in data]


def i2c_scan(handle, addr):
    """Test if a device ACKs at the given I2C address (0-byte write)."""
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", addr)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)
    ljm.eWriteName(handle, "I2C_GO", 1)
    ack = ljm.eReadName(handle, "I2C_ACKS")
    return int(ack) == 0


def i2c_read_split(handle, addr, register, num_bytes):
    """Read by doing a separate write then read (no repeated start)."""
    # Write the register address
    ljm.eWriteName(handle, "I2C_SLAVE_ADDRESS", addr)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 1)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", 0)
    ljm.eWriteNameByteArray(handle, "I2C_DATA_TX", 1, [register])
    ljm.eWriteName(handle, "I2C_GO", 1)
    ack = ljm.eReadName(handle, "I2C_ACKS")
    if ack != 0:
        raise IOError(f"I2C write NACK for register {register:#x} (acks = {int(ack):#x})")
    time.sleep(0.01)
    # Now read the data
    ljm.eWriteName(handle, "I2C_NUM_BYTES_TX", 0)
    ljm.eWriteName(handle, "I2C_NUM_BYTES_RX", num_bytes)
    ljm.eWriteName(handle, "I2C_GO", 1)
    ack = ljm.eReadName(handle, "I2C_ACKS")
    if ack != 0:
        raise IOError(f"I2C read NACK (acks = {int(ack):#x})")
    data = ljm.eReadNameByteArray(handle, "I2C_DATA_RX", num_bytes)
    return [int(b) for b in data]


def detect_bme280(handle):
    """Try to find a BME280 at 0x76, then 0x77. Returns the address or raises."""
    # First scan for any device on the bus
    print("I2C bus scan:")
    for addr in (0x76, 0x77):
        found = i2c_scan(handle, addr)
        print(f"  Address {addr:#04x}: {'ACK' if found else 'no response'}")

    # Try soft reset on any responding address, then read chip ID
    for addr in (0x76, 0x77):
        if not i2c_scan(handle, addr):
            continue
        print(f"  Sending soft reset to {addr:#04x}...")
        try:
            i2c_write(handle, addr, [0xE0, 0xB6])  # reset register
        except IOError:
            pass  # reset may NACK, that's OK
        time.sleep(0.1)  # wait for reset

        # Dump registers to diagnose
        print(f"  Register dump for {addr:#04x}:")
        for reg in [0x00, 0x88, 0xD0, 0xE0, 0xF2, 0xF4, 0xF7]:
            try:
                val = i2c_read(handle, addr, reg, 1)[0]
                print(f"    0x{reg:02X} = 0x{val:02X}")
            except IOError as e:
                print(f"    0x{reg:02X} = ERROR ({e})")

        # Try reading chip ID
        try:
            chip_id = i2c_read(handle, addr, BME280_CHIP_ID_REG, 1)[0]
            if chip_id == BME280_CHIP_ID:
                return addr
        except IOError as e:
            print(f"  Address {addr:#04x}: read failed - {e}")

    raise RuntimeError("BME280 not detected at 0x76 or 0x77. Check wiring.")


def read_calibration(handle, addr):
    """Read all BME280 calibration parameters and return them as a dict."""
    # Temperature and pressure calibration: 26 bytes at 0x88
    tp = i2c_read(handle, addr, BME280_CALIB_TEMP_PRESS_START, 26)

    # Humidity calibration: dig_H1 at 0xA1
    h1 = i2c_read(handle, addr, BME280_CALIB_HUM_H1, 1)

    # Humidity calibration: 7 bytes at 0xE1
    hx = i2c_read(handle, addr, BME280_CALIB_HUM_START, 7)

    # Unpack temperature calibration (unsigned, signed, signed)
    dig_T1 = tp[0] | (tp[1] << 8)
    dig_T2 = struct.unpack('<h', bytes(tp[2:4]))[0]
    dig_T3 = struct.unpack('<h', bytes(tp[4:6]))[0]

    # Unpack pressure calibration
    dig_P1 = tp[6] | (tp[7] << 8)
    dig_P2 = struct.unpack('<h', bytes(tp[8:10]))[0]
    dig_P3 = struct.unpack('<h', bytes(tp[10:12]))[0]
    dig_P4 = struct.unpack('<h', bytes(tp[12:14]))[0]
    dig_P5 = struct.unpack('<h', bytes(tp[14:16]))[0]
    dig_P6 = struct.unpack('<h', bytes(tp[16:18]))[0]
    dig_P7 = struct.unpack('<h', bytes(tp[18:20]))[0]
    dig_P8 = struct.unpack('<h', bytes(tp[20:22]))[0]
    dig_P9 = struct.unpack('<h', bytes(tp[22:24]))[0]

    # Unpack humidity calibration
    dig_H1 = h1[0]
    dig_H2 = struct.unpack('<h', bytes(hx[0:2]))[0]
    dig_H3 = hx[2]
    dig_H4 = (hx[3] << 4) | (hx[4] & 0x0F)
    if dig_H4 > 2047:
        dig_H4 -= 4096
    dig_H5 = ((hx[4] >> 4) & 0x0F) | (hx[5] << 4)
    if dig_H5 > 2047:
        dig_H5 -= 4096
    dig_H6 = struct.unpack('<b', bytes([hx[6]]))[0]

    return {
        'T1': dig_T1, 'T2': dig_T2, 'T3': dig_T3,
        'P1': dig_P1, 'P2': dig_P2, 'P3': dig_P3,
        'P4': dig_P4, 'P5': dig_P5, 'P6': dig_P6,
        'P7': dig_P7, 'P8': dig_P8, 'P9': dig_P9,
        'H1': dig_H1, 'H2': dig_H2, 'H3': dig_H3,
        'H4': dig_H4, 'H5': dig_H5, 'H6': dig_H6,
    }


def configure_sensor(handle, addr):
    """Set BME280 to normal mode with x1 oversampling for all measurements."""
    # Humidity oversampling x1 (must be written before ctrl_meas)
    i2c_write(handle, addr, [BME280_CTRL_HUM, 0x01])
    # Config: standby 1000ms, filter off
    i2c_write(handle, addr, [BME280_CONFIG, 0xA0])
    # Temp oversampling x1, pressure oversampling x1, normal mode
    i2c_write(handle, addr, [BME280_CTRL_MEAS, 0x27])


def compensate_temperature(raw_temp, cal):
    """BME280 temperature compensation. Returns (temp_C, t_fine)."""
    var1 = ((raw_temp >> 3) - (cal['T1'] << 1)) * cal['T2'] >> 11
    var2 = (((((raw_temp >> 4) - cal['T1']) * ((raw_temp >> 4) - cal['T1'])) >> 12)
            * cal['T3']) >> 14
    t_fine = var1 + var2
    temp_c = (t_fine * 5 + 128) >> 8
    return temp_c / 100.0, t_fine


def compensate_pressure(raw_press, t_fine, cal):
    """BME280 pressure compensation. Returns pressure in Pa."""
    var1 = t_fine - 128000
    var2 = var1 * var1 * cal['P6']
    var2 = var2 + ((var1 * cal['P5']) << 17)
    var2 = var2 + (cal['P4'] << 35)
    var1 = ((var1 * var1 * cal['P3']) >> 8) + ((var1 * cal['P2']) << 12)
    var1 = ((1 << 47) + var1) * cal['P1'] >> 33
    if var1 == 0:
        return 0.0
    p = 1048576 - raw_press
    p = (((p << 31) - var2) * 3125) // var1
    var1 = (cal['P9'] * (p >> 13) * (p >> 13)) >> 25
    var2 = (cal['P8'] * p) >> 19
    p = ((p + var1 + var2) >> 8) + (cal['P7'] << 4)
    return p / 256.0


def compensate_humidity(raw_hum, t_fine, cal):
    """BME280 humidity compensation. Returns relative humidity in %."""
    h = t_fine - 76800
    if h == 0:
        return 0.0
    h = ((((raw_hum << 14) - (cal['H4'] << 20) - (cal['H5'] * h)) + 16384) >> 15) * \
        (((((((h * cal['H6']) >> 10) * (((h * cal['H3']) >> 11) + 32768)) >> 10)
           + 2097152) * cal['H2'] + 8192) >> 14)
    h = h - (((((h >> 15) * (h >> 15)) >> 7) * cal['H1']) >> 4)
    h = max(0, min(h, 419430400))
    return (h >> 12) / 1024.0


def read_sensor_data(handle, addr, cal):
    """Read raw data from BME280 and return compensated (temp_C, humidity_%, pressure_hPa)."""
    data = i2c_read(handle, addr, BME280_DATA_START, 8)

    raw_press = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    raw_temp = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    raw_hum = (data[6] << 8) | data[7]

    temp_c, t_fine = compensate_temperature(raw_temp, cal)
    pressure_pa = compensate_pressure(raw_press, t_fine, cal)
    humidity = compensate_humidity(raw_hum, t_fine, cal)

    return temp_c, humidity, pressure_pa / 100.0  # hPa


def main():
    handle = None
    try:
        handle = ljm.openS("T4", "ANY", "ANY")
        info = ljm.getHandleInfo(handle)
        print(f"Connected to LabJack T4 (serial: {info[2]})")

        # Power BME280 from DAC0 at 3.3V to bypass level translator
        ljm.eWriteName(handle, "DAC0", 3.3)
        print("DAC0 set to 3.3V for BME280 power")
        time.sleep(0.2)  # allow sensor to power up

        i2c_setup(handle)
        addr = detect_bme280(handle)
        print(f"BME280 detected at address: {addr:#04x}")

        cal = read_calibration(handle, addr)
        configure_sensor(handle, addr)

        # Allow sensor to take first measurement
        time.sleep(0.5)

        print()
        print("BME280 Environmental Sensor (LabJack T4)")
        print("-" * 55)

        while True:
            temp_c, humidity, pressure = read_sensor_data(handle, addr, cal)
            temp_f = temp_c * 9.0 / 5.0 + 32.0
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{now} | Temp: {temp_c:.1f}\u00b0C ({temp_f:.1f}\u00b0F) "
                  f"| Humidity: {humidity:.1f}% | Pressure: {pressure:.2f} hPa",
                  flush=True)
            time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopped by user.")
    except ljm.LJMError as e:
        print(f"LabJack error: {e}")
    except RuntimeError as e:
        print(f"Error: {e}")
    finally:
        if handle is not None:
            ljm.close(handle)
            print("LabJack connection closed.")


if __name__ == "__main__":
    main()
