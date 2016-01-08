from __future__ import division
from pyiso import client_factory
import matplotlib.pyplot as plt
import seaborn
import datetime
import pytz


def get_duck_curve(client, start_at, end_at, timeZone, loadScale=1, windScale=1, solarScale=1):
    """
    """

    data = client.get_generation(start_at=start_at, end_at=end_at)
    timeSolar = []
    timeWind = []
    solar = {}
    wind = {}
    for eachData in data:
        if eachData['fuel_name'] == 'solarpv':
            timeSolar.append(eachData['timestamp'])
            solar[timeSolar[-1]] = eachData['gen_MW'] * solarScale
        if eachData['fuel_name'] == 'wind':
            timeWind.append(eachData['timestamp'])
            wind[timeWind[-1]] = eachData['gen_MW'] * windScale

    data = client.get_load(start_at=start_at, end_at=end_at)
    timeLoad = []
    load = {}
    for eachData in data:
        timeLoad.append(eachData['timestamp'])
        load[timeLoad[-1]] = eachData['load_MW'] * loadScale

    duck = []
    timeList = []
    for time in timeSolar:
        if time >= start_at and time <= end_at:
            timeList.append(time)
    timeList.sort()

    for time in timeList:
        try:
            duck.append(load[time] - solar[time] - wind[time])
        except:
            print('No data for ' + str(time))
            duck.append(duck[-1])
            # import pdb;
            # pdb.set_trace()

    timeList = [time.replace(tzinfo=pytz.utc).astimezone(timeZone) for time in timeList]
    print("")
    return timeList, duck


def get_solar_wind_load(client, start_at, end_at):
    """

    Args:
        client:
        start_at:
        end_at:
        timeZone:

    Returns:

    """
    # Get generation as a dictionnary {date: value}
    data = client.get_generation(start_at=start_at, end_at=end_at)
    timeSolar = []
    solar = {}
    solarth = {}
    wind = {}
    for eachData in data:
        if eachData['fuel_name'] == 'solarpv':
            timeSolar.append(eachData['timestamp'])
            solar[timeSolar[-1]] = eachData['gen_MW']
        if eachData['fuel_name'] == 'solarth':
            solarth[eachData['timestamp']] = eachData['gen_MW']
        if eachData['fuel_name'] == 'wind':
            wind[eachData['timestamp']] = eachData['gen_MW']

    # Get load as a dictionnary {date: value}
    data = client.get_load(start_at=start_at, end_at=end_at)
    timeLoad = []
    load = {}
    for eachData in data:
        timeLoad.append(eachData['timestamp'])
        load[timeLoad[-1]] = eachData['load_MW']

    # Get a list of timestamp
    timeList = []
    for time in timeSolar:
        if time >= start_at and time <= end_at:
            timeList.append(time)
    timeList.sort()

    return timeList, solar, solarth, wind, load


def plot_duck_curve(time, duck):
    # Avoid frame around plot
    seaborn.set_style("whitegrid")
    seaborn.despine()

    # Plot the data
    plt.plot(time, duck)
    plt.xlabel('Time', fontsize=14)
    plt.ylabel('Power (MW)', fontsize=14)
    plt.title('Duck curve from ' + str(time[0]) + ' to ' + str(time[-1]))

    plt.show()


def scale_duck_curve(duck, maxPower):
    maxDuck = max(duck) * 1000
    coef = maxPower / maxDuck  # kW
    duck = [duck[i] * coef for i in range(0, len(duck))]

    return duck
