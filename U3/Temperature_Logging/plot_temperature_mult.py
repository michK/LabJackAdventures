import sys
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import matplotlib.dates as mdates

in_file = sys.argv[1]

str2date = lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

fix, ax = plt.subplots()

data_time    = np.genfromtxt(in_file, delimiter=',', usecols=0, converters={0: str2date}, encoding='utf-8')
data_temp_atm = np.genfromtxt(in_file, delimiter=',', usecols=1, encoding='utf-8')
data_temp_in  = np.genfromtxt(in_file, delimiter=',', usecols=2, encoding='utf-8')

ax.plot(data_time, data_temp_atm)
ax.plot(data_time, data_temp_in)

# Plot settings
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))

ax.set_xlabel('Time')
ax.set_ylabel('Temperature [deg C]')

plt.gcf().autofmt_xdate()

ax.grid()

ax.legend(['Temp atm [deg C]', 'Temp in [deg C]'])

plt.show()
