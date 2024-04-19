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
