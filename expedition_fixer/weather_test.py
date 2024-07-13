# Import Meteostat library and dependencies
from datetime import datetime
import matplotlib.pyplot as plt
from meteostat import Point, Daily, Hourly, Stations

# Set time period
start = datetime(2022, 12, 31)
end = datetime(2023, 1, 5)

# Create Point for Lemmenjoki
lemmenjoki = Point(68.7586, 26.2308, 325)

# Get nearby weather stations
stations = Stations()
stations = stations.nearby(lemmenjoki._lat, lemmenjoki._lon)
station = stations.fetch(1)

# Print DataFrame
print(station)


# Get daily data for NY 2023/4
data = Daily(station, start, end)
data = data.fetch()

# Plot line chart including average, minimum and maximum temperature
data.plot(y=['tavg', 'tmin', 'tmax'])
plt.show()

# Get hourly data
data = Hourly(lemmenjoki, start, end)
data = data.fetch()

# Print DataFrame
print(data)