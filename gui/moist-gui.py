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
from PIL import Image, ImageTk
from tkinter import PhotoImage

port = 'COM6'
baudrate = 9600
ser = serial.Serial(port, baudrate)

event = threading.Event()

ALTITUDE = 0
PRESSURE = 1
NTC = 2
HUMIDITY = 3
CO2 = 4
TEMPERATURE = 5

data = [[], [], [], [], [], []]
file = ''
recording = False
elapsed_time = 'Elapsed time: -'

app = tk.Tk()
app.title('MOIST')

container_frame = tk.Frame(app)
container_frame.pack(fill = 'both', expand = True)

map_label = tk.Label(container_frame)
map_label.pack(side = 'right')

line = [(69.295188, 16.029263), (69.295189, 16.029264)]
map_widget = tkintermapview.TkinterMapView(map_label, width = 600, height = 800, corner_radius = 0)
map_widget.set_position(69.295188, 16.029263) # Starting position
marker = map_widget.set_marker(69.295188, 16.029263, 'Cansat')
path = map_widget.set_path(line)
map_widget.set_zoom(10)
map_widget.pack()

graphs_container = tk.Frame(container_frame)
graphs_container.pack(side = 'left')

top_graphs_frame = tk.Frame(graphs_container)
top_graphs_frame.pack()

bottom_graphs_frame = tk.Frame(graphs_container)
bottom_graphs_frame.pack()

menu_frame = tk.Frame(app, background = 'white')
menu_frame.pack(side = 'bottom', fill = 'both', expand = True)

time_elapsed_label = tk.Label(menu_frame, text = elapsed_time, background = 'white', font = ('Arial', 15))
time_elapsed_label.pack(side = 'right')

def save():
    global file
    files = [('Text file', '*.txt')]
    file = asksaveasfile(filetypes = files, defaultextension = files).name

save_icon = PhotoImage(file = './assets/icons8-save-30.png')
save_btn = tk.Button(menu_frame, command = lambda: save(), image = save_icon, width = 30, height = 30, background = 'white')
save_btn.pack(side = 'left')

start_recording_icon = PhotoImage(file = './assets/icons8-start-30.png')
stop_recording_icon = PhotoImage(file = './assets/icons8-pause-squared-30.png')

def updateRecording():
    global recording
    recording = not recording
    if(recording):
        recording_btn.configure(image = stop_recording_icon)
    else:
        recording_btn.configure(image = start_recording_icon)

recording_btn = tk.Button(menu_frame, command = lambda: updateRecording(), image = start_recording_icon, background = 'white')
recording_btn.pack(side = 'left')

recording_icon = PhotoImage(file = './assets/icons8-recording-30.png')
recording_label = tk.Label(menu_frame, image = recording_icon, background = 'white')
recording_label.pack(side = 'left')

def dataHandling():
    while (True):
        try:
            if(not ser.is_open): ser.open() # handle reconnect
            if(ser.in_waiting):
                temp = ser.read_until(b'\r').decode().strip().split(',')
                if(len(temp) > 1):
                    if(os.path.isfile(file) and recording):    
                        with open(file, 'a', newline='') as f_object:
                            writer_object = writer(f_object)
                            writer_object.writerow(temp)
                            f_object.close()
                    
                    global elapsed_time
                    elapsed_time = temp[0]

                    if(float(temp[4]) != 0 and float(temp[5]) != 0):
                        line.append((float(temp[4]), float(temp[5])))

                    data[ALTITUDE].append(float(temp[3]))
                    data[PRESSURE].append(float(temp[6]))
                    data[NTC].append(float(temp[7]))
                    data[HUMIDITY].append(float(temp[8]))
                    data[CO2].append(float(temp[9]))
                    data[TEMPERATURE].append(float(temp[10]))
        except serial.SerialException as se:
            ser.close() # handle disconnect

        if(event.is_set()):
            break

        time.sleep(0.01)

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
    time_elapsed_label.configure(text = 'Elapsed time: ' + elapsed_time)
    time_elapsed_label.after(1000, func = updateElapsedTime)
updateElapsedTime()

def updateMap():
    lat, lng = line[-1]
    marker.set_position(lat, lng)
    path.set_position_list(line)
    map_widget.after(1000, func = updateMap)
updateMap()

def flashRecording(state):
    if(recording):
        if(state):
            recording_label.configure(image = '')
        else:
            recording_label.configure(image = recording_icon)
    else:
        recording_label.configure(image = '')
    recording_label.after(1000, flashRecording, not state)
flashRecording(recording)

app.protocol('WM_DELETE_WINDOW', cleanup)
app.mainloop()
