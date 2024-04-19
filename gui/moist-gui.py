import serial
import time
from csv import writer
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import threading


app = tk.Tk()
app.title('MOIST')

port = 'COM6'
baudrate = 9600
ser = serial.Serial(port, baudrate)

event = threading.Event()

VALUES = 0
TEMPERATURE = 0
HUMIDITY = 1
CO2 = 2

data = [[], [], []]

def dataHandling():
    while (True):
        if(ser.in_waiting):
            temp = ser.read_until(b'\r').decode().strip().split(',')

            with open('stuff.txt', 'a', newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(temp)
                f_object.close()

            data[0].append(int(temp[0]))
            data[1].append(int(temp[1]))
            data[2].append(int(temp[2]))

            time.sleep(0.01)
        if(event.is_set()):
            break

data_thread = threading.Thread(target = dataHandling)
data_thread.start()

graphs_frame = tk.Frame(app)
graphs_frame.pack()

fig_temp, ax_temp = plt.subplots()
graph_temp = ax_temp.plot(0, 0, color = 'r')[0]
ax_temp.set_title('SCD30')
ax_temp.set_xlabel('Readings')
ax_temp.set_ylabel('Temperature ($^\circ$C)') 

temp_canvas = FigureCanvasTkAgg(fig_temp, graphs_frame)
temp_canvas.draw()
temp_canvas.get_tk_widget().pack(side = 'left', fill = 'both', expand = True)

fig_rh, ax_rh = plt.subplots()
graph_rh = ax_rh.plot(0, 0, color = 'g')[0]
ax_rh.set_title('SCD30')
ax_rh.set_xlabel('Readings')
ax_rh.set_ylabel('Relative humidity (%)')

temp_canvas = FigureCanvasTkAgg(fig_rh, graphs_frame)
temp_canvas.draw()
temp_canvas.get_tk_widget().pack(side = 'left', fill = 'both', expand = True)

fig_co2, ax_co2 = plt.subplots()
graph_co2 = ax_co2.plot(0, 0, color = 'b')[0]
ax_co2.set_title('SCD30')
ax_co2.set_xlabel('Readings')
ax_co2.set_ylabel('$CO_{2}$ (ppm)')

temp_canvas = FigureCanvasTkAgg(fig_co2, graphs_frame)
temp_canvas.draw()
temp_canvas.get_tk_widget().pack(side = 'left', fill = 'both', expand = True)

def updateTemperature(frame):
    if(data[TEMPERATURE]):
        x = np.arange(start = 1, stop = len(data[TEMPERATURE]) + 1, step = 1)
        ax_temp.set_xlim(1, len(data[TEMPERATURE]))
        ax_temp.set_ylim(min(data[TEMPERATURE]) - 1, max(data[TEMPERATURE]) + 1)
        graph_temp.set_xdata(x)
        graph_temp.set_ydata(data[TEMPERATURE])

def updateHumidity(frame):
    if(data[HUMIDITY]):
        x = np.arange(start = 1, stop = len(data[HUMIDITY]) + 1, step = 1)
        ax_rh.set_xlim(1, len(data[HUMIDITY]))
        ax_rh.set_ylim(min(data[HUMIDITY]) - 1, max(data[HUMIDITY]) + 1)
        graph_rh.set_xdata(x)
        graph_rh.set_ydata(data[HUMIDITY])

def updateCO2(frame):
    if(data[CO2]):
        x = np.arange(start = 1, stop = len(data[CO2]) + 1, step = 1)
        ax_co2.set_xlim(1, len(data[CO2]))
        ax_co2.set_ylim(min(data[CO2]) - 1, max(data[CO2]) + 1)
        graph_co2.set_xdata(x)
        graph_co2.set_ydata(data[CO2])


anim_temp = FuncAnimation(fig_temp, updateTemperature, frames = None)
anim_hum = FuncAnimation(fig_rh, updateHumidity, frames = None)
anim_co2 = FuncAnimation(fig_co2, updateCO2, frames = None)

def cleanup():
    plt.close('all')
    event.set()
    data_thread.join()
    app.destroy()

app.protocol('WM_DELETE_WINDOW', cleanup)

app.mainloop()
