import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import matplotlib.dates as mdates

str2date = lambda x: datetime.strptime(x, '%Y-%m-%d %H:%M:%S')

fix, ax = plt.subplots()

###############
# Living room #
###############

data_time_living = np.genfromtxt('temperature-log-living.txt', delimiter=',', usecols=0, converters={0: str2date}, encoding='utf-8')
data_temp_living = np.genfromtxt('temperature-log-living.txt', delimiter=',', usecols=1, encoding='utf-8')

start     = datetime(year=2023, month=8, day=7, hour=7, minute=0, second=2)
ind_start = np.argwhere(data_time_living==start)[0][0]
end       = datetime(year=2023, month=8, day=8, hour=7, minute=0, second=1)
ind_end   = np.argwhere(data_time_living==end)[0][0]

ax.plot(data_time_living[ind_start:ind_end], data_temp_living[ind_start:ind_end])

ax.set_xlim([data_time_living[ind_start], data_time_living[ind_end]])
ax.set_ylim(15, 30)

###########
# Bedroom #
###########

data_time_bed = np.genfromtxt('temperature-log-bed.txt', delimiter=',', usecols=0, converters={0: str2date}, encoding='utf-8')
data_temp_bed = np.genfromtxt('temperature-log-bed.txt', delimiter=',', usecols=1, encoding='utf-8')

start     = datetime(year=2023, month=8, day=9, hour=7, minute=0, second=1)
ind_start = np.argwhere(data_time_bed==start)[0][0]
end       = datetime(year=2023, month=8, day=10, hour=7, minute=0, second=1)
ind_end   = np.argwhere(data_time_bed==end)[0][0]

ax.plot(data_time_bed[ind_start:ind_end] - timedelta(hours=48), data_temp_bed[ind_start:ind_end])

start     = datetime(year=2023, month=8, day=10, hour=7, minute=0, second=1)
ind_start = np.argwhere(data_time_bed==start)[0][0]
end       = datetime(year=2023, month=8, day=11, hour=7, minute=0, second=1)
ind_end   = np.argwhere(data_time_bed==end)[0][0]

ax.plot(data_time_bed[ind_start:ind_end] - timedelta(hours=72), data_temp_bed[ind_start:ind_end])

# Plot settings
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=2))

ax.set_xlabel('Time')
ax.set_ylabel('Temperature [deg C]')

plt.gcf().autofmt_xdate()

ax.grid()

ax.legend(['Living-room (7 Aug)', 'Bedroom (9 Aug)', 'Bedroom (10 Aug)'])

plt.show()
