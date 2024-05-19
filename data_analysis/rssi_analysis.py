'''
File: reading.py
Author: N. L. Stepien
Created: April 2024
Description: This code plots the RSSI values from different ground stations
Course: TEK5720
'''

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import scipy as sp
from scipy.signal import savgol_filter

'''
Reading and extracting data
'''

#df_data = pd.read_csv('logs/andenes_gs.txt', sep=',')
#df_data = pd.read_csv('logs/andoya_gs.txt', sep=',')
df_data = pd.read_csv('logs/automatic_antenna_gs.txt', sep=',')

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
- 15:28:51 ---- Time of Splashdown [2276]
'''
df = pd.DataFrame({'Time': time})
df['Time'] = pd.to_datetime(df['Time'], format='%H:%M:%S')  # Convert the 'Time' column to a datetime type
time_fix = df['Time']

#launch_time = pd.to_datetime('14:06:15', format='%H:%M:%S')
#balloon_burst = pd.to_datetime('15:09:20', format='%H:%M:%S')
#splashdown_time = pd.to_datetime('15:28:51', format='%H:%M:%S')

#burst_index = 1756
#launch_index = 58
#splashdown_index = 2276

# INDEX ANALYSIS
pd.set_option('display.max_rows', None) 
#print(time_fix)


index_max = np.argmax(altitude_from_pressure)


def rssi_and_rates_plot():
    # Applying Savitzky-Golay Filter 
    window_length = 60 # Must be an odd number
    poly_order = 2  # Degree of the fitting polynomial
    smoothed = savgol_filter(rssi, window_length, poly_order)

    # RSSI TIME 
    plt.plot(time_fix, rssi, linewidth=0.2, label='Original', alpha=0.3, color='black')
    plt.plot(time_fix[:index_max], smoothed[:index_max], label='Ascent', color='Red')
    plt.plot(time_fix[index_max:], smoothed[index_max:], label='Descent', color='Blue')
    #plt.plot(time_fix[:burst_index], smoothed[:burst_index], label='Filtered (ascent)', linewidth='0.8', color='red')
   # plt.plot(time_fix[burst_index:], smoothed[burst_index:], label='Filtered (descent)', linewidth='0.8', color='blue')
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.title('Andenes Ground Station 2 (Motorised Antenna)')
    plt.xlabel('Time [Hour:Min]')
    plt.ylabel('RSSI')
    plt.grid()
    plt.show()

    # RSSI ALTITUDE
    plt.plot(rssi, altitude_from_pressure, linewidth=0.2, label='Original', alpha=0.3, color='black')
    plt.plot(smoothed[:index_max], altitude_from_pressure[:index_max], label='Ascent', color='Red')
    plt.plot(smoothed[index_max:], altitude_from_pressure[index_max:], label='Descent', color='Blue')
   # plt.plot(smoothed[:burst_index], altitude_from_pressure[:burst_index], label='Filtered (ascent)', linewidth='0.8', color='red')
   # plt.plot(smoothed[burst_index:], altitude_from_pressure[burst_index:], label='Filtered (descent)', linewidth='0.8', color='blue')
    #plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M'))  # Format x-axis labels to display only hour:minute
    plt.legend()
    plt.title('Andenes Ground Station 2 (Motorised Antenna)')
    plt.xlabel('RSSI')
    plt.ylabel('Altitude [m]')
    plt.grid()
    plt.show()

rssi_and_rates_plot()