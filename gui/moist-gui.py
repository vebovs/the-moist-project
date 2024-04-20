import serial
import time
from csv import writer
import tkinter as tk
from tkinter.filedialog import asksaveasfile
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import numpy as np
import threading
import tkintermapview
import os

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
file = ''
recording = False
app = tk.Tk()
app.title('MOIST')

container_frame = tk.Frame(app)
container_frame.pack(fill = 'both', expand = True)

map_label = tk.Label(container_frame)
map_label.pack(side = 'right')

map_widget = tkintermapview.TkinterMapView(map_label, width = 600, height = 800, corner_radius = 0)
map_widget.set_position(69.295188, 16.029263) # Starting position
marker = map_widget.set_marker(69.295188, 16.029263, 'Cansat')
path = map_widget.set_path([(69.295188, 16.029263), (69.295189, 16.029264)])
map_widget.set_zoom(10)
map_widget.pack()

graphs_container = tk.Frame(container_frame)
graphs_container.pack(side = 'left')

top_graphs_frame = tk.Frame(graphs_container)
top_graphs_frame.pack()

bottom_graphs_frame = tk.Frame(graphs_container)
bottom_graphs_frame.pack()

menu_frame = tk.Frame(app)
menu_frame.pack(side = 'bottom', fill = 'both', expand = True)

time_elapsed_label = tk.Label(menu_frame, text = 'Elapsed time: -')
time_elapsed_label.pack(side = 'left')

def save():
    global file
    files = [('Text file', '*.txt')]
    file = asksaveasfile(filetypes = files, defaultextension = files).name

save_btn = tk.Button(menu_frame, text = 'Save', command = lambda: save())
save_btn.pack(side = 'left')

def updateRecording(state):
    global recording
    recording = state

start_recording_btn = tk.Button(menu_frame, text = 'Start Recording', command = lambda: updateRecording(True))
start_recording_btn.pack(side = 'left')

stop_recording_btn = tk.Button(menu_frame, text = 'Stop Recording', command = lambda: updateRecording(False))
stop_recording_btn.pack(side = 'left')

def dataHandling():
    while (True):
        if(ser.in_waiting):
            temp = ser.read_until(b'\r').decode().strip().split(',')

            if(os.path.isfile(file) and recording):    
                with open(file, 'a', newline='') as f_object:
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

canvas_pool = []

def createFigure(title = '', xlabel = '', ylabel = '', color = 'g', parent_frame = None):
    fig, ax = plt.subplots()
    fig.set_size_inches(6.4, 4)
    graph = ax.plot(0, 0, color = color)[0]
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    canvas = FigureCanvasTkAgg(fig, parent_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(side = 'left', fill = 'both', expand = True)
    canvas_pool.append(canvas)
    return (fig, ax, graph)

fig_temp, ax_temp, graph_temp = createFigure('SCD30', 'Readings', 'Temperature ($^\circ$C)', 'r', top_graphs_frame)
fig_rh, ax_rh, graph_rh = createFigure('SCD30', 'Readings', 'Relative humidity (%)', 'g', top_graphs_frame)
fig_co2, ax_co2, graph_co2 = createFigure('SCD30', 'Readings', '$CO_{2}$ (ppm)', 'b', top_graphs_frame)

fig_ntc, ax_ntc, graph_ntc = createFigure('NTC', 'Readings', 'Resistance ($\Omega$)', 'c', bottom_graphs_frame)
fig_pressure, ax_pressure, graph_pressure = createFigure('BMP-280', 'Readings', 'Pressure (Pa)', 'y', bottom_graphs_frame)
fig_alt, ax_alt, graph_alt = createFigure('BN-880', 'Readings', 'Altitude (m)', 'm', bottom_graphs_frame)

def update(frame, ax, graph, INDEX):
    if(data[INDEX]):
        x = np.arange(start = 1, stop = len(data[INDEX]) + 1, step = 1)
        ax.set_xlim(1, len(data[INDEX]) + 1)
        ax.set_ylim(min(data[INDEX]) - 1, max(data[INDEX]) + 1)
        graph.set_xdata(x)
        graph.set_ydata(data[INDEX])

anim_temp = FuncAnimation(fig_temp, update, cache_frame_data = False, fargs = (ax_temp, graph_temp, TEMPERATURE,))
anim_hum = FuncAnimation(fig_rh, update, cache_frame_data = False, fargs = (ax_rh, graph_rh, HUMIDITY,))
anim_co2 = FuncAnimation(fig_co2, update, cache_frame_data = False, fargs = (ax_co2, graph_co2, CO2,))

anim_ntc = FuncAnimation(fig_ntc, update, cache_frame_data = False, fargs=(ax_ntc, graph_ntc, NTC,))
anim_pressure = FuncAnimation(fig_pressure, update, cache_frame_data = False, fargs=(ax_pressure, graph_pressure, PRESSURE,))
anim_alt = FuncAnimation(fig_alt, update, cache_frame_data = False, fargs=(ax_alt, graph_alt, ALTITUDE,))

def cleanup():
    plt.close('all')
    for canvas in canvas_pool:
        canvas.stop_event_loop()
    map_widget.destroy()
    event.set()
    data_thread.join()
    app.destroy()

def updateElapsedTime():
    if(data[TIME]):
        time_elapsed_label.configure(text = 'Elapsed time: ' + data[TIME][-1])
    time_elapsed_label.after(1000, func = updateElapsedTime)
updateElapsedTime()

app.protocol('WM_DELETE_WINDOW', cleanup)
app.mainloop()
