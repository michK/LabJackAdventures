import numpy as np
import time

import u3

def ramp_up(d, rpm_max, n, theta_step):
    """Ramp up stepper rpm in n increments"""
    for rpm in np.linspace(0.1, rpm_max, n):
        f_step = rpm * 360 * 32 / (60 * theta_step)
        divisor = int(48e6 / (256 * f_step))

        d.configTimerClock(TimerClockBase=6, TimerClockDivisor=divisor)
        duty_cycle = 0.5
        baseValue = int((1-duty_cycle) * 65536)
        d.getFeedback(u3.Timer0Config(TimerMode=1, Value=baseValue))
        time.sleep(0.05)
