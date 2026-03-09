import u3
import time


def calc_freq(lj, duration):
    """Estimate frequency of input signal using Timer1 period measurement"""
    # Pause to sample edges
    time.sleep(duration)
    # Read pulse width in ticks
    cmd = u3.Timer(timer=1)
    ticks = lj.getFeedback(cmd)[0]

    # Scale ticks to a period in seconds, then convert to frequency in Hz
    if ticks > 0:
        period_secs = ticks / 4000000.0
        freq = 1 / period_secs
    else:
        freq = 0

    return freq
