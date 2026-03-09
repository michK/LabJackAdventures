import numpy as np
import signal
import time
import matplotlib.pyplot as plt

import u3
from setup import arm_labjack
from lj_tools import calc_freq

# Initialize labjack
lj = arm_labjack()

# Set operating parameters
rpm_target = 200
n_poles = 5

# Set PID gains
kp = 0.001
ki = 0.002
kd = 0.004

# Configure the timer for PWM and set initial parameters.
throttle_setting = 0.0
throttle_range = [0, 1]
duty_range = [5.9, 12.1]
duty_cycle = np.interp(throttle_setting, throttle_range, duty_range) / 100

baseValue = int((1-duty_cycle) * 65536)
lj.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))


def handler(signum, frame):
    """Used to catch Ctrl-C event to stop script"""
    throttle_setting = 0
    duty_cycle = np.interp(throttle_setting, throttle_range, duty_range) / 100
    baseValue = int((1-duty_cycle) * 65536)
    lj.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))
    lj.close()
    plt.plot(time_list, rpm_list)
    plt.show()
    exit(1)


signal.signal(signal.SIGINT, handler)

# Initialize errors
int_error = 0
error_prev = 0

rpm_list = []
time_list = []
start_time_glob = time.time()

# Run motor
while True:
    # Start timer
    start_time = time.time()
    # Get current frequency
    freq = calc_freq(lj, duration=0.001) / n_poles
    rpm_measured = freq
    rpm_list.append(rpm_measured)
    time_list.append(time.time() - start_time_glob)
    print("RPM measured: {}".format(round(rpm_measured)))
    dt = time.time() - start_time
    # Compute error
    error = rpm_target - rpm_measured
    int_error = int_error + error * dt
    der_error = (error - error_prev) / dt

    throttle_setting = kp*error + ki*int_error + kd*der_error
    if throttle_setting > 1:
        throttle_setting = 1
    elif throttle_setting < 0:
        throttle_setting = 0

    print("Current throttle setting: {}".format(throttle_setting))
    # Update throttle setting
    duty_cycle = np.interp(throttle_setting, throttle_range, duty_range) / 100
    baseValue = int((1-duty_cycle) * 65536)
    lj.getFeedback(u3.Timer0Config(TimerMode=0, Value=baseValue))
    # Save error
    error_prev = error

# Close labjack.
lj.close()
