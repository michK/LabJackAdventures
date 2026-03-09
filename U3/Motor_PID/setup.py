import u3

def arm_labjack():
    # Open the first found LabJack.
    lj = u3.U3()
    # Enable two timers: Timer0 for PWM output, Timer1 for frequency measurement
    lj.configIO(NumberOfTimersEnabled=2, TimerCounterPinOffset=4)

    # Set timer clock to 4 MHz, no divisor
    cmd = lj.configTimerClock(0, 0)
    lj.getFeedback(cmd)

    # Configure Timer1 for period measurement (TimerMode=2)
    cmd = u3.Timer1Config(TimerMode=2, Value=0)
    lj.getFeedback(cmd)

    return lj
