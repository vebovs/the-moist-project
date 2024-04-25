import serial
import time
from csv import writer
import numpy as np
import threading
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import tkinter as tk
from tkinter.filedialog import asksaveasfile
import tkintermapview
from PIL import Image, ImageTk
import math
import time

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
tilt_gps = 'GPS based tilt: -'
tilt_pressure = 'Pressure based tilt: -'
rssi = 'RSSI: -'
ntc_temp = 0.0

starting_pos = (69.296011, 16.028944) # Starting position of Cansat
operator_pos = (69.296049, 16.030619) # Starting position of operator

# NTC Material constants
A1 = 3.354016e-3
B1 = 2.569850e-4
C1 = 2.620131e-6
D1 = 6.383091e-8

app = tk.Tk()
app.title('MOIST')

container_frame = tk.Frame(app)
container_frame.pack(fill = 'both', expand = True)

map_label = tk.Label(container_frame)
map_label.pack(side = 'right')

line = [starting_pos, starting_pos]
op_can_line = [operator_pos, starting_pos]
map_widget = tkintermapview.TkinterMapView(map_label, width = 600, height = 800, corner_radius = 0)
map_widget.set_position(69.296177, 16.030525)
marker = map_widget.set_marker(69.296177, 16.030525, 'Cansat')
path = map_widget.set_path(line)
op_can_path = map_widget.set_path(op_can_line, color = 'red')
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
time_elapsed_label.pack(expand=True)

tilt_gps_label = tk.Label(menu_frame, text = tilt_gps, background = 'white', font = ('Arial', 15))
tilt_gps_label.pack()

tilt_pressure_label = tk.Label(menu_frame, text = tilt_pressure, background = 'white', font = ('Arial', 15))
tilt_pressure_label.pack()

rssi_label = tk.Label(menu_frame, text = rssi, background = 'white', font = ('Arial', 15))
rssi_label.pack()

ntc_temp_label = tk.Label(menu_frame, text = 'NTC Temperature: -', background = 'white', font = ('Arial', 15))
ntc_temp_label.pack()

def save():
    global file
    files = [('Text file', '*.txt')]
    file = asksaveasfile(filetypes = files, defaultextension = files).name

save_image = Image.open('./assets/icons8-save-30.png')
save_icon = ImageTk.PhotoImage(image = save_image)
save_btn = tk.Button(menu_frame, command = lambda: save(), image = save_icon, width = 30, height = 30, background = 'white')
save_btn.pack(side = 'left')

start_recording_image = Image.open('./assets/icons8-start-30.png')
start_recording_icon = ImageTk.PhotoImage(image = start_recording_image)
stop_recording_image = Image.open('./assets/icons8-pause-squared-30.png')
stop_recording_icon = ImageTk.PhotoImage(image = stop_recording_image)

def updateRecording():
    global recording
    recording = not recording
    if(recording):
        recording_btn.configure(image = stop_recording_icon)
    else:
        recording_btn.configure(image = start_recording_icon)

recording_btn = tk.Button(menu_frame, command = lambda: updateRecording(), image = start_recording_icon, background = 'white')
recording_btn.pack(side = 'left')

recording_image = Image.open('./assets/icons8-recording-30.png')
recording_icon = ImageTk.PhotoImage(image = recording_image)
recording_label = tk.Label(menu_frame, image = recording_icon, background = 'white')
recording_label.pack(side = 'left')

def ntc_ohms_to_temp(ntc_ohms):
    # Logarithmic values of resistance
    log_NTC = np.log(ntc_ohms/10000)
    # Steinhart and Hart Equation
    temp = (1 / (A1 + B1 * log_NTC + C1 * log_NTC * log_NTC + D1 * log_NTC * log_NTC * log_NTC)) - 273.15
    return temp

# As specified in the Andøya Cansat handbook
def calcAltitude(temp, p):
    pb = 101325 # Starting pressure (Pa)
    hb = 1 # Starting altitude
    tb = temp + 273.15 # Starting temperature in celsius
    lb = -0.0065 # Temperature gradient
    R = 287.06 # Specific gas constant
    g = 9.80665 # Gravitational constant
    return hb + (tb/lb) * ((p/pb)**((-R*lb)/(g)) - 1)

# Graciously provided by the TUMOR group
def distance(current_lat, current_lng):  # returns distance in meters
    op_lat, op_lng = operator_pos
    op_lat = math.radians(op_lat)
    op_lng = math.radians(op_lng)
    current_lat = math.radians(current_lat)
    current_lng = math.radians(current_lng)

    diff_lon = current_lng - op_lng
    diff_lat = current_lat - op_lat

    a = math.sin(diff_lat / 2) ** 2 + math.cos(op_lat) * math.cos(current_lat) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = 6371 * c  # Earth radius * angle between the two points

    return distance * 1000

def calcTilt(alt, lat, lng):
     current_distance = distance(lat, lng)
     return math.degrees(math.atan2(alt, current_distance))

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
                    
                    global elapsed_time, rssi, tilt_gps, tilt_pressure, op_can_path, ntc_temp
                    elapsed_time = temp[0]
                    rssi = temp[11]

                    ntc_temp = ntc_ohms_to_temp(float(temp[7]))
                    
                    lat = float(temp[4])
                    lng = float(temp[5])

                    op_can_line[-1] = (lat, lng)

                    if(lat != 0 and lng != 0):
                        line.append([lat, lng])
                        tilt_gps = calcTilt(float(temp[3]), lat, lng)
                        tilt_pressure = calcTilt(calcAltitude(float(temp[7]), float(temp[6])), lat, lng)

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
    fig.set_size_inches(4.4, 4)
    graph = ax.plot(0, 0, color = color)[0]
    ax.set_title(title + ' ' + ylabel)
    ax.set_xlabel(xlabel)
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

def updateLabels():
    time_elapsed_label.configure(text = 'Elapsed time: ' + elapsed_time)
    rssi_label.configure(text = 'RSSI: ' + rssi + ' dbm')
    ntc_temp_label.configure(text = 'NTC Temperature: ' + str(ntc_temp) + u'\N{DEGREE SIGN}' + 'C')
    tilt_gps_label.configure(text = 'GPS based tilt: ' + str(tilt_gps) + u'\N{DEGREE SIGN}')
    tilt_pressure_label.configure(text = 'Pressure based tilt: ' + str(tilt_pressure) + u'\N{DEGREE SIGN}')
    time_elapsed_label.after(1000, func = updateLabels)
updateLabels()

def updateMap():
    lat, lng = line[-1]
    marker.set_position(lat, lng)
    path.set_position_list(line)
    op_can_path.set_position_list(op_can_line)
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
