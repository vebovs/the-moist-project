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

TIME = 0
ID = 1
TIMESTAMP = 2
ALTITUDE = 3
LAT = 4
LNG = 5
PRESSURE = 6
NTC = 7
HUMIDITY = 8
CO2 = 9
TEMPERATURE = 10

data = [[], [], [], [], [], [], [], [], [], [], []]

def dataHandling():
    while (True):
        if(ser.in_waiting):
            temp = ser.read_until(b'\r').decode().strip().split(',')

            with open('stuff.txt', 'a', newline='') as f_object:
                writer_object = writer(f_object)
                writer_object.writerow(temp)
                f_object.close()

            data[TIME].append(temp[TIME])
            data[ID].append(int(temp[ID]))
            data[TIMESTAMP].append(temp[TIMESTAMP])
            data[ALTITUDE].append(float(temp[ALTITUDE]))
            data[LAT].append(float(temp[LAT]))
            data[LNG].append(float(temp[LNG]))
            data[PRESSURE].append(float(temp[PRESSURE]))
            data[NTC].append(float(temp[NTC]))
            data[HUMIDITY].append(float(temp[HUMIDITY]))
            data[CO2].append(float(temp[CO2]))
            data[TEMPERATURE].append(float(temp[TEMPERATURE]))

            time.sleep(0.01)
        if(event.is_set()):
            break

data_thread = threading.Thread(target = dataHandling)
data_thread.start()

graphs_frame = tk.Frame(app)
graphs_frame.pack()

def createFigure(title = '', xlabel = '', ylabel = '', color = 'g'):
    fig, ax = plt.subplots()
    graph = ax.plot(0, 0, color = color)[0]
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    canvas = FigureCanvasTkAgg(fig, graphs_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side = 'left', fill = 'both', expand = True)
    return (fig, ax, graph)

fig_temp, ax_temp, graph_temp = createFigure('SCD30', 'Readings', 'Temperature ($^\circ$C)', 'r')
fig_rh, ax_rh, graph_rh = createFigure('SCD30', 'Readings', 'Relative humidity (%)', 'g')
fig_co2, ax_co2, graph_co2 = createFigure('SCD30', 'Readings', '$CO_{2}$ (ppm)', 'b')

def update(frame, ax, graph, INDEX):
    if(data[INDEX]):
        x = np.arange(start = 1, stop = len(data[INDEX]) + 1, step = 1)
        ax.set_xlim(1, len(data[INDEX]))
        ax.set_ylim(min(data[INDEX]) - 1, max(data[INDEX]) + 1)
        graph.set_xdata(x)
        graph.set_ydata(data[INDEX])

anim_temp = FuncAnimation(fig_temp, update, frames = None, fargs = (ax_temp, graph_temp, TEMPERATURE,))
anim_hum = FuncAnimation(fig_rh, update, frames = None, fargs = (ax_rh, graph_rh, HUMIDITY,))
anim_co2 = FuncAnimation(fig_co2, update, frames = None, fargs = (ax_co2, graph_co2, CO2,))

def cleanup():
    plt.close('all')
    event.set()
    data_thread.join()
    app.destroy()

app.protocol('WM_DELETE_WINDOW', cleanup)

app.mainloop()