'''
File: reading.py
Author: N. L. Stepien
Created: April 2024
Description: This code processes measured data from a weather balloon and plots the results
Course: TEK5720
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import json
import scipy as sp
from scipy.signal import savgol_filter

'''
Reading and extracting data
'''
df_data = pd.read_csv('merged_data_header.txt', sep=',')

df_data = df_data.sort_values('id') 

elapsed_time = df_data['elapsed_time']
id = df_data['id']
time = df_data['time']
altitude = df_data['alt']
latitude = df_data['lat']
longitude = df_data['lng']
pressure = df_data['pressure']
thermistor = df_data['ohm']
temperature = df_data['temp']
co2 = df_data['co2']
humidity = df_data['hum']
rssi = df_data['rssi']

'''
Resistance to Temperature Conversion
'''
# Material constants
A1 = 3.354016e-3
B1 = 2.569850e-4
C1 = 2.620131e-6
D1 = 6.383091e-8


# Logarithmic values of resistance
R_NTC = thermistor
log_NTC = np.log(R_NTC/10000)


# Steinhart and Hart Equation
temp_ntc = (1 / (A1 + B1 * log_NTC + C1 * log_NTC * log_NTC + D1 * log_NTC * log_NTC * log_NTC)) - 273.15

'''
Pressure to Altitude Conversion
'''
# CONVERSION BASED ON EQUATION FROM SCHROEDER
def altitude_calculation(pres, temp):
    P_0 = 101036
    P_z = pres
    tmp = temp
    k = 8.3144598 
    m = 0.02896968 # [kg/mol]
    g = 9.80665 # [m/s^2]
    z = ((np.log(P_z) - np.log(P_0)) * k * (tmp + 274.15)) / (- m * g)

    return z

# Calculating altitude based on pressure
altitude_from_pressure = altitude_calculation(pressure, temp_ntc)
max_altitude = max(altitude_from_pressure)

'''
Time Conversion: 
- 14:06:14 ---- Time of Launch [58]
- 15:09:20 ---- Time of Burst [1756]
- 15:28:51 ---- Time of Last Signal [2276]
'''
df = pd.DataFrame({'Time': time})
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')  # Convert the 'Time' column to a datetime type
time_fix = df['Time']

launch_time = pd.to_datetime('14:06:15', format='%H:%M:%S')
balloon_burst = pd.to_datetime('15:09:20', format='%H:%M:%S')
lastsignal_time = pd.to_datetime('15:28:51', format='%H:%M:%S')

burst_index = 1756
launch_index = 58
lastsignal_index = 2276

# INDEX ANALYSIS
pd.set_option('display.max_rows', None) 
#print(time_fix)

'''
Reading data from Andøya radiosonde
'''

# Reading the JSON file in a very unpleasent way but it works
with open('data_radiosonde.geojson') as f:
    data = json.load(f)

def create_lists(atr:str, data:list):
    tmp = []
    for feature,j in zip(data["features"], range(len(data["features"]))):
        try:
            tmp.append(feature['properties'][atr])
        except:
            #print(f"Didn't find '{atr}' at index {j}")
            tmp.append(np.nan)

    return tmp 

altitudes_r = create_lists("gpheight", data)
times_r = create_lists("time", data)
temperatures_r = create_lists("temp", data)
temperatures_r_c = []
for i in temperatures_r:
    temp_r_c = i - 273.15
    temperatures_r_c.append(temp_r_c)
dewpoints_r = create_lists("dewpoint", data)
pressures_r = create_lists("pressure", data)
pressures_r_pa = []
for i in pressures_r:
    pres_r_pa = i * 100
    pressures_r_pa.append(pres_r_pa)
wind_us_r = create_lists("wind_u", data)
wind_vs_r = create_lists("wind_v", data)

'''
Calculating ascent and descent rates
'''

index_max = np.argmax(altitude_from_pressure)

def plot_radisonde_vs_moist():
    # EXTERNAL TEMPERATURE VS ALTITUDE (COMPARISON)
    plt.plot(temperatures_r_c, altitudes_r, label='Radiosonde', color='blue', linewidth=0.9)
    plt.plot(temp_ntc[:index_max], altitude_from_pressure[:index_max], label='Ascent (MOIST)', color='red', linewidth=0.9)
    plt.plot(temp_ntc[index_max:], altitude_from_pressure[index_max:], label='Descent (MOIST)', color='salmon', linewidth=0.9)
    plt.scatter(temp_ntc[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 (8 °C)', color='green', s=100)
    plt.scatter(temp_ntc[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 (-27 °C)', color='black', s=100)
    plt.scatter(temp_ntc[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 (1.6 °C)', color='blue', s=100)
    troposphere_start = 10
    troposphere_end = 7700
    tropopause_start = 7700
    tropopause_end = 25000
    stratosphere_start = 25000
    stratosphere_end = 32000
    plt.fill_between(np.linspace(max(temperatures_r_c), min(temperatures_r_c)), troposphere_start, troposphere_end, alpha=0.2, color='blue', label='Troposphere (end = {} m)'.format(troposphere_end))
    plt.fill_between(np.linspace(max(temperatures_r_c), min(temperatures_r_c)), tropopause_start, tropopause_end, alpha=0.2, color='green', label='Tropopause (end = {} m)'.format(tropopause_end))
    plt.fill_between(np.linspace(max(temperatures_r_c), min(temperatures_r_c)), stratosphere_start, stratosphere_end, alpha=0.2, color='yellow', label='Stratosphere (end = {} m)'.format(stratosphere_end))
    plt.xlabel('Temperature [°C]')
    plt.ylabel('Altitude [m]')
    plt.grid()
    plt.legend()
    plt.title('Temperature vs Altitude (Andøya Radiosonde vs MOIST) - ATMOSPHERE LAYERS')
    plt.show()

    # PRESSURE VS ALTITUDE (COMPARISON)
    plt.plot(altitudes_r, pressures_r_pa, label='Radiosonde', color='blue', linewidth=0.9)
    plt.plot(altitude_from_pressure[:index_max], pressure[:index_max], label='Ascent (MOIST)', color='brown', linewidth=0.9)
    plt.plot(altitude_from_pressure[index_max:], pressure[index_max:], label='Descent (MOIST)', color='peru', linewidth=0.9)
    plt.scatter(altitude_from_pressure[58], pressure[58], marker='x', label='Launch: 14:06:14 (101036 Pa)', color='green', s=100)
    plt.scatter(altitude_from_pressure[1756], pressure[1756], marker='x', label='Burst: 15:09:20 (7751 Pa)',  color='black', s=100)
    plt.scatter(altitude_from_pressure[2276], pressure[2276], marker='x', label='Last Signal: 15:28:51 (98355 Pa)', color='blue', s=100)
    plt.ylabel('Pressure [Pa]')
    plt.xlabel('Altitude [m]')
    plt.grid()
    plt.legend()
    plt.title('Pressure vs Altitude (Andøya Radiosonde vs MOIST)')
    plt.show()

def plot_moist():
    # EXTERNAL TEMPERATURE VS TIME [NTC]
    plt.title('External Temperature [NTC]')
    plt.grid()
    plt.ylabel('Temperature [°C]')
    plt.xlabel('Time [Hour:Min]')
    plt.plot(time_fix[:index_max], temp_ntc[:index_max], color='red', linewidth='0.8', label='Ascent')
    plt.plot(time_fix[index_max:], temp_ntc[index_max:], color='salmon', linewidth='0.8', label='Descent')
    plt.scatter(time_fix[58], temp_ntc[58], marker='x', label='Launch: 14:06:14 (8 °C)', color='green', s=100)
    plt.scatter(time_fix[1756], temp_ntc[1756], marker='x', label='Burst: 15:09:20 (-27 °C)', color='black', s=100)
    plt.scatter(time_fix[2276], temp_ntc[2276], marker='x', label='Last Signal: 15:28:51 (1.6 °C)', color='blue', s=100)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.show()

    # EXTERNAL TEMPERATURE VS ALTITUDE [NTC]
    plt.title('External Temperature [NTC]')
    plt.grid()
    plt.ylabel('Altitude [m]')
    plt.xlabel('Temperature [°C]')
    plt.plot(temp_ntc[:index_max], altitude_from_pressure[:index_max], color='red', linewidth='0.8', label='Ascent')
    plt.plot(temp_ntc[index_max:], altitude_from_pressure[index_max:], color='salmon', linewidth='0.8', label='Descent')
    plt.scatter(temp_ntc[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 (8 °C)', color='green', s=100)
    plt.scatter(temp_ntc[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 (-27 °C)', color='black', s=100)
    plt.scatter(temp_ntc[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 (1.6 °C)', color='blue', s=100)
    plt.legend()
    plt.show()

    # ALTITUDE VS TIME [BN-880 and BMP-280]
    plt.title('Altitude [BN-880 and BMP-280]')
    plt.grid()
    plt.ylabel('Alitutde [m]')
    plt.xlabel('Time [Hour:Min]')
    plt.plot(time_fix, altitude_from_pressure, label='BMP-280 (Based on Pressure and Temperature)', color='orange')
    plt.plot(time_fix, altitude, color='blue', linewidth='1', label='BN-880')
    plt.scatter(time_fix[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 (23 m)', color='green', s=100)
    plt.scatter(time_fix[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 ({:.0f} m)'.format(max_altitude),  color='black', s=100)
    plt.scatter(time_fix[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 (248 m)', color='blue', s=100)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.show()

    # PRESSURE VS TIME [BMP-280]
    plt.title('Pressure [BMP-280]')
    plt.grid()
    plt.ylabel('Pressure [Pa]')
    plt.xlabel('Time [Hour:Min]')
    plt.plot(time_fix[:index_max], pressure[:index_max], color='brown', linewidth='1', label='Ascent')
    plt.plot(time_fix[index_max:], pressure[index_max:], color='peru', linewidth='1', label='Descent')
    plt.scatter(time_fix[58], pressure[58], marker='x', label='Launch: 14:06:14 (101036 Pa)', color='green', s=100)
    plt.scatter(time_fix[1756], pressure[1756], marker='x', label='Burst: 15:09:20 (7751 Pa)',  color='black', s=100)
    plt.scatter(time_fix[2276], pressure[2276], marker='x', label='Last Signal: 15:28:51 (98355 Pa)', color='blue', s=100)
    plt.legend()
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.show()

    # PRESSURE VS ALTITUDE [BMP-280]
    plt.title('Pressure [BMP-280]')
    plt.grid()
    plt.xlabel('Altitude [m]')
    plt.ylabel('Pressure [Pa]')
    plt.plot(altitude_from_pressure[:index_max], pressure[:index_max], color='brown', linewidth='1', label='Ascent')
    plt.plot(altitude_from_pressure[index_max:], pressure[index_max:], color='peru', linewidth='1', label='Descent')
    plt.scatter(altitude_from_pressure[58], pressure[58], marker='x', label='Launch: 14:06:14 (101036 Pa)', color='green', s=100)
    plt.scatter(altitude_from_pressure[1756], pressure[1756], marker='x', label='Burst: 15:09:20 (7751 Pa)',  color='black', s=100)
    plt.scatter(altitude_from_pressure[2276], pressure[2276], marker='x', label='Last Signal: 15:28:51 (98355 Pa)', color='blue', s=100)
    plt.legend()
    plt.show()

    # INTERNAL TEMPERATURE VS TIME [SCD30]
    plt.title('Internal Temperature [SCD30]')
    plt.grid()
    plt.ylabel('Temperature [°C]')
    plt.xlabel('Time [Hour:Min]')
    plt.scatter(time_fix[58], temperature[58], marker='x', label='Launch: 14:06:14 (42 °C)', color='green', s=100)
    plt.scatter(time_fix[1756], temperature[1756], marker='x', label='Burst: 15:09:20 (-9 °C)',  color='black', s=100)
    plt.scatter(time_fix[2276], temperature[2276], marker='x', label='Last Signal: 15:28:51 (-9 °C)', color='blue', s=100)

    # Best Accuracy: 14:06 to 14:34
    yellow_zone1_start = 0
    yellow_zone1_end = 20
    green_zone_start = 20
    green_zone_end = 30
    yellow_zone2_start = 30
    yellow_zone2_end = 42
    red_zone1_start = 42
    red_zone1_end = 50
    red_zone2_start = 0
    red_zone2_end = min(temperature)

    plt.legend()
    plt.plot(time_fix[:index_max], temperature[:index_max], color='orange', linewidth='1', label='Ascent')
    plt.plot(time_fix[index_max:], temperature[index_max:], color='brown', linewidth='1', label='Descent')
    plt.fill_between(time_fix, yellow_zone1_start, yellow_zone1_end, alpha=0.2, color='yellow', label='Accuracy ± 6 °C')
    plt.fill_between(time_fix, green_zone_start, green_zone_end, alpha=0.2, color='green', label='Accuracy ± 1 °C')
    plt.fill_between(time_fix, yellow_zone2_start, yellow_zone2_end, alpha=0.2, color='yellow')
    plt.fill_between(time_fix, red_zone1_start, red_zone1_end, alpha=0.2, color='red')
    plt.fill_between(time_fix, red_zone2_start, red_zone2_end, alpha=0.2, color='red', label='Accuracy < ± 10°C')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.show()

    # INTERNAL TEMPERATURE VS ALTITUDE [SCD30]
    plt.title('Internal Temperature [SCD30]')
    plt.grid()
    plt.xlabel('Temperature [°C]')
    plt.ylabel('Altitude [m]')
    plt.scatter(temperature[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 (42 °C)', color='green', s=100)
    plt.scatter(temperature[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 (-9 °C)',  color='black', s=100)
    plt.scatter(temperature[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 (-9 °C)', color='blue', s=100)
    plt.fill_betweenx(np.linspace(min(altitude_from_pressure), max(altitude_from_pressure)), yellow_zone1_start, yellow_zone1_end, alpha=0.2, color='yellow', label='Accuracy ± 6 °C')
    plt.fill_betweenx(np.linspace(min(altitude_from_pressure), max(altitude_from_pressure)), green_zone_start, green_zone_end, alpha=0.2, color='green', label='Accuracy ± 1 °C')
    plt.fill_betweenx(np.linspace(min(altitude_from_pressure), max(altitude_from_pressure)), yellow_zone2_start, yellow_zone2_end, alpha=0.2, color='yellow')
    plt.fill_betweenx(np.linspace(min(altitude_from_pressure), max(altitude_from_pressure)), red_zone1_start, red_zone1_end, alpha=0.2, color='red')
    plt.fill_betweenx(np.linspace(min(altitude_from_pressure), max(altitude_from_pressure)), red_zone2_start, red_zone2_end, alpha=0.2, color='red', label='Accuracy < ± 10°C')
    plt.legend()
    plt.plot(temperature[:index_max], altitude_from_pressure[:index_max], color='orange', linewidth='1', label='Ascent')
    plt.plot(temperature[index_max:], altitude_from_pressure[index_max:], color='brown', linewidth='1', label='Descent')
    plt.show()

    sea_level_pressure = 101325
    co2_pressure = sea_level_pressure / pressure
    new_co2 = co2 * co2_pressure

    # CO2 VS TIME [SCD30]
    plt.title('$CO_2$ [SCD30] - With Pressure')
    plt.grid()
    plt.ylabel('$CO_2$ [ppm]')
    plt.xlabel('Time [Hour:Min]')
    plt.scatter(time_fix[58], co2[58], marker='x', label='Launch: 14:06:14 (477 ppm)', color='green', s=100)
    plt.scatter(time_fix[1756], co2[1756], marker='x', label='Burst: 15:09:20 (8.5 ppm)',  color='black', s=100)
    plt.scatter(time_fix[2276], co2[2276], marker='x', label='Last Signal: 15:28:51 (300 ppm)', color='blue', s=100)
    green_time_start = time_fix[0]
    green_time_end = time_fix[828]
    yellow_time_start = time_fix[828]
    yellow_time_end = time_fix[2276]
    plt.fill_betweenx(np.linspace(min(co2), max(co2)), green_time_start, green_time_end, alpha=0.2, color='green', label='Accuracy ± 2.5 ppm')
    plt.fill_betweenx(np.linspace(min(co2), max(co2)), yellow_time_start, yellow_time_end, alpha=0.2, color='gray', label='Accuracy < ± 2.5 ppm (not specified)')
    plt.plot(time_fix[:index_max], co2[:index_max], color='limegreen', linewidth='0.9', label='Ascent')
    plt.plot(time_fix[index_max:], co2[index_max:], color='green', linewidth='0.9', label='Descent')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.show()

    # CO2 VS ALTITUDE [SCD30]
    plt.title('$CO_2$ [SCD30] - With Pressure')
    plt.grid()
    plt.ylabel('Altitude [m]')
    plt.xlabel('$CO_2$ [ppm]')
    plt.scatter(co2[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 (477 ppm)', color='green', s=100)
    plt.scatter(co2[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 (8.5 ppm)',  color='black', s=100)
    plt.scatter(co2[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 (300 ppm)', color='blue', s=100)
    plt.plot(co2[:index_max], altitude_from_pressure[:index_max], color='limegreen', linewidth='0.9', label='Ascent')
    plt.plot(co2[index_max:], altitude_from_pressure[index_max:], color='green', linewidth='0.9', label='Descent')
    plt.legend()
    plt.show()

    # CO2 VS TIME [SCD30] without pressure
    plt.title('$CO_2$ [SCD30] - Without Pressure')
    plt.grid()
    plt.ylabel('$CO_2$ [ppm]')
    plt.xlabel('Time [Hour:Min]')
    plt.scatter(time_fix[58], new_co2[58], marker='x', label='Launch: 14:06:14 ({:.0f} ppm)'.format(new_co2[58]), color='green', s=100)
    plt.scatter(time_fix[1756], new_co2[1756], marker='x', label='Burst: 15:09:20 ({:.0f} ppm)'.format(new_co2[1756]),  color='black', s=100)
    plt.scatter(time_fix[2276], new_co2[2276], marker='x', label='Last Signal: 15:28:51 ({:.0f} ppm)'.format(new_co2[2276]), color='blue', s=100)
    green_time_start = time_fix[0]
    green_time_end = time_fix[828]
    yellow_time_start = time_fix[828]
    yellow_time_end = time_fix[2276]
    plt.fill_betweenx(np.linspace(min(new_co2), max(new_co2)), green_time_start, green_time_end, alpha=0.2, color='green', label='Accuracy ± 2.5 ppm')
    plt.fill_betweenx(np.linspace(min(new_co2), max(new_co2)), yellow_time_start, yellow_time_end, alpha=0.2, color='gray', label='Accuracy < ± 2.5 ppm (not specified)')
    plt.plot(time_fix[:index_max], new_co2[:index_max], color='limegreen', linewidth='0.9', label='Ascent')
    plt.plot(time_fix[index_max:], new_co2[index_max:], color='green', linewidth='0.9', label='Descent')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.show()

    # CO2 VS ALTITUDE [SCD30] without pressure
    plt.title('$CO_2$ [SCD30] - Without Pressure')
    plt.grid()
    plt.ylabel('Altitude [m]')
    plt.xlabel('$CO_2$ [ppm]')
    plt.scatter(new_co2[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 ({:.0f} ppm)'.format(new_co2[58]), color='green', s=100)
    plt.scatter(new_co2[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 ({:.0f} ppm)'.format(new_co2[1756]),  color='black', s=100)
    plt.scatter(new_co2[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 ({:.0f} ppm)'.format(new_co2[2276]), color='blue', s=100)
    plt.legend()
    plt.plot(new_co2[:index_max], altitude_from_pressure[:index_max], color='limegreen', linewidth='0.9', label='Ascent')
    plt.plot(new_co2[index_max:], altitude_from_pressure[index_max:], color='green', linewidth='0.9', label='Descent')
    plt.legend()
    plt.show()

    # HUMIDITY VS TIME [SCD30]
    plt.title('Relative Humidity [SCD30]')
    plt.grid()
    plt.ylabel('Relative Humidity [RH %]')
    plt.xlabel('Time [Hour:Min]')
    plt.scatter(time_fix[58], humidity[58], marker='x', label='Launch: 14:06:14 ({:.0f}%)'.format(humidity[58]), color='green', s=100)
    plt.scatter(time_fix[1756], humidity[1756], marker='x', label='Burst: 15:09:20 ({:.0f}%)'.format(humidity[1756]),  color='black', s=100)
    plt.scatter(time_fix[2276], humidity[2276], marker='x', label='Last Signal: 15:28:51 ({:.0f}%)'.format(humidity[2276]), color='blue', s=100)
    green_time_start = time_fix[245]
    green_time_end = time_fix[465]
    gray_time1_start = time_fix[0]
    gray_time1_end = time_fix[245]
    gray_time2_start = time_fix[465]
    gray_time2_end = time_fix[2276]
    plt.fill_betweenx(np.linspace(min(humidity), max(humidity)), green_time_start, green_time_end, alpha=0.2, color='green', label='Accuracy ± 3%RH')
    plt.fill_betweenx(np.linspace(min(humidity), max(humidity)), gray_time1_start, gray_time1_end, alpha=0.2, color='gray', label='Accuracy < ± 3%RH (not specified)')
    plt.fill_betweenx(np.linspace(min(humidity), max(humidity)), gray_time2_start, gray_time2_end, alpha=0.2, color='gray')
    plt.plot(time_fix[:index_max], humidity[:index_max], color='dodgerblue', linewidth='1', label='Ascent')
    plt.plot(time_fix[index_max:], humidity[index_max:], color='springgreen', linewidth='1', label='Descent')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.show()

    # HUMIDITY VS ALTITUDE [SCD30]
    plt.title('Relative Humidity [SCD30]')
    plt.grid()
    plt.xlabel('Relative Humidity [RH %]')
    plt.ylabel('Altitude [m]')
    plt.scatter(humidity[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14 ({:.0f}%)'.format(humidity[58]), color='green', s=100)
    plt.scatter(humidity[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20 ({:.0f}%)'.format(humidity[1756]),  color='black', s=100)
    plt.scatter(humidity[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51 ({:.0f}%)'.format(humidity[2276]), color='blue', s=100)
    plt.plot(humidity[:index_max], altitude_from_pressure[:index_max], color='dodgerblue', linewidth='1', label='Ascent')
    plt.plot(humidity[index_max:], altitude_from_pressure[index_max:], color='springgreen', linewidth='1', label='Descent')
    plt.legend()
    plt.show()

    # MIX (EXTERNAL TEMPERATURE VS INTERNAL TEMPERATURE VS ALTITUDE)
    plt.title('Temperature Comparison [NTC and SCD30]')
    plt.grid()
    plt.ylabel('Altitude [m]')
    plt.xlabel('Temperature [°C]')
    plt.plot(temp_ntc[:index_max], altitude_from_pressure[:index_max], color='red', linewidth='0.8', label='Ascent (external)')
    plt.plot(temp_ntc[index_max:], altitude_from_pressure[index_max:], color='salmon', linewidth='0.8', label='Descent (external)')
    plt.plot(temperature[:index_max], altitude_from_pressure[:index_max], color='orange', linewidth='0.8', label='Ascent (internal)')
    plt.plot(temperature[index_max:], altitude_from_pressure[index_max:], color='brown', linewidth='0.8', label='Descent (internal)')
    plt.scatter(temp_ntc[58], altitude_from_pressure[58], marker='x', label='Launch: 14:06:14', color='green', s=100)
    plt.scatter(temp_ntc[1756], altitude_from_pressure[1756], marker='x', label='Burst: 15:09:20', color='black', s=100)
    plt.scatter(temp_ntc[2276], altitude_from_pressure[2276], marker='x', label='Last Signal: 15:28:51', color='blue', s=100)
    plt.scatter(temperature[58], altitude_from_pressure[58], marker='x', color='green', s=100)
    plt.scatter(temperature[1756], altitude_from_pressure[1756], marker='x',  color='black', s=100)
    plt.scatter(temperature[2276], altitude_from_pressure[2276], marker='x', color='blue', s=100)
    plt.legend()
    plt.show()

   # MIX (CO2 VS HUMIDITY VS EXTERNAL TEMPERATURE VS ALTITUDE VS TIME)
    fig, ax = plt.subplots()
    fig.subplots_adjust(right=0.75)

    twin1 = ax.twinx()
    twin2 = ax.twinx()
    twin3 = ax.twinx()

    twin2.spines.right.set_position(("axes", 1.1))
    twin3.spines.right.set_position(("axes", 1.2))

    p1, = ax.plot(time_fix, temp_ntc, "r-")
    p2, = twin1.plot(time_fix, humidity, "b-")
    p3, = twin2.plot(time_fix, new_co2, "g-")
    p4, = twin3.plot(time_fix, altitude_from_pressure, "black", linestyle='dashdot', linewidth=0.5)

    ax.set_xlabel("Time [Hour:Min]")
    ax.set_ylabel("External Temperature [°C]")
    twin1.set_ylabel("Relative Humidity [RH %]")
    twin2.set_ylabel("$CO_2$ [ppm]")
    twin3.set_ylabel("Altitude [m]")

    ax.yaxis.label.set_color(p1.get_color())
    twin1.yaxis.label.set_color(p2.get_color())
    twin2.yaxis.label.set_color(p3.get_color())
    twin3.yaxis.label.set_color(p4.get_color())

    tkw = dict(size=4, width=1.5)
    ax.tick_params(axis='y', colors=p1.get_color(), **tkw)
    twin1.tick_params(axis='y', colors=p2.get_color(), **tkw)
    twin2.tick_params(axis='y', colors=p3.get_color(), **tkw)
    twin3.tick_params(axis='y', colors=p4.get_color(), **tkw)
    ax.tick_params(axis='x', **tkw)

    plt.title('Comparison of External Temperature & Relative Humidity & $CO_2$ [SCD30 and NTC]')
    plt.axvline(time_fix[58], label='Launch: 14:06:14', color='black', linestyle='solid')
    plt.axvline(time_fix[1756], label='Burst: 15:09:20', color='black', linestyle='dashed')
    plt.axvline(time_fix[2276], label='Last Signal: 15:28:51', color='black', linestyle='dotted')
    plt.grid()
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend(loc='upper center')
    plt.show()

    # MIX (CO2 VS HUMIDITY VS EXTERNAL TEMPERATURE VS ALTITUDE VS TIME)
    fig, ax = plt.subplots()
    fig.subplots_adjust(top=0.75)

    twin1 = ax.twiny()
    twin2 = ax.twiny()

    twin2.spines.top.set_position(("axes", 1.1))

    p1, = ax.plot(temp_ntc[index_max:], altitude_from_pressure[index_max:], "salmon")
    p1, = ax.plot(temp_ntc[:index_max], altitude_from_pressure[:index_max], "red")
    p2, = twin1.plot(humidity[index_max:], altitude_from_pressure[index_max:], "dodgerblue")
    p2, = twin1.plot(humidity[:index_max], altitude_from_pressure[:index_max], "blue")
    p3, = twin2.plot(new_co2[index_max:], altitude_from_pressure[index_max:], "springgreen")
    p3, = twin2.plot(new_co2[:index_max], altitude_from_pressure[:index_max], "green")

    ax.set_xlabel("External Temperature [°C]")
    ax.set_ylabel("Altitude [m]")
    twin1.set_xlabel("Relative Humidity [RH %]")
    twin2.set_xlabel("$CO_2$ [ppm]")

    ax.xaxis.label.set_color(p1.get_color())
    twin1.xaxis.label.set_color(p2.get_color())
    twin2.xaxis.label.set_color(p3.get_color())

    tkw = dict(size=2, width=1.5)
    ax.tick_params(axis='x', colors=p1.get_color(), **tkw)
    twin1.tick_params(axis='x', colors=p2.get_color(), **tkw)
    twin2.tick_params(axis='x', colors=p3.get_color(), **tkw)
    ax.tick_params(axis='y', **tkw)

    plt.title('Comparison of External Temperature & Relative Humidity & $CO_2$ [SCD30 and NTC]')
    plt.axhline(altitude_from_pressure[58], label='Launch: 14:06:14', color='black', linestyle='solid')
    plt.axhline(altitude_from_pressure[1756], label='Burst: 15:09:20', color='black', linestyle='dashed')
    plt.axhline(altitude_from_pressure[2276], label='Last Signal: 15:28:51', color='black', linestyle='dotted')
    plt.grid()
    plt.legend(loc='upper center')
    plt.show()

def rssi_and_rates_plot():
    # Applying Savitzky-Golay Filter 
    window_length = 60 # Must be an odd number
    poly_order = 2  # Degree of the fitting polynomial

    # Convert the time data to datetime type
    time_fix_ = pd.to_datetime(time_fix)

    # Calculate the difference in seconds from the starting timestamp
    seconds_difference = (time_fix_ - time_fix_.iloc[0]).dt.seconds

    delta_t = np.diff(seconds_difference)
    delta_h = np.diff(altitude_from_pressure)

    full_rate = delta_h / delta_t
    average_full_altitude = altitude_from_pressure.drop(altitude_from_pressure.index[-1])
    smooth_full_rate = savgol_filter(full_rate, window_length, poly_order)

    index_max = np.argmax(average_full_altitude)

    plt.title('Ascent and Descent Rate of MOIST CanSat')
    plt.plot(full_rate, average_full_altitude, linewidth='0.5', color='black', alpha=0.2)
    plt.plot(smooth_full_rate[:index_max], average_full_altitude[:index_max], linewidth='0.5', color='red', label='Ascent: avg {:.1f} m/s'.format(np.average(smooth_full_rate[:index_max])))
    plt.plot(smooth_full_rate[index_max:], average_full_altitude[index_max:], linewidth='0.9', color='blue', label='Descent: avg {:.1f} m/s'.format(np.average(smooth_full_rate[index_max:])))
    plt.ylabel('Altitude [m]')
    plt.grid()
    plt.xlabel('Velocity [m/s]')
    plt.legend()
    plt.show()

'''
Plotting all results
'''

rssi_and_rates_plot()
plot_moist()
plot_radisonde_vs_moist()


