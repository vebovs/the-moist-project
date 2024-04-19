import serial
import time
from csv import writer
import tkinter as tk

"""
port = 'COM6'
baudrate = 9600
ser = serial.Serial(port, baudrate)

while (True):
    if(ser.in_waiting):
        data = ser.readline(ser.in_waiting).decode()
        print(data, end='')
    time.sleep(0.01)
"""

"""
# List that we want to add as a new row
data_str = "1,2,3,4,5"
data_list = data_str.split(',')

while (True):
    # Open our existing CSV file in append mode
    # Create a file object for this file
    with open('stuff.txt', 'a', newline='') as f_object:
        # Pass this file object to csv.writer()
        # and get a writer object
        writer_object = writer(f_object)

        # Pass the list as an argument into
        # the writerow()
        writer_object.writerow(data_list)

        # Close the file object
        f_object.close()
    time.sleep(1)
"""

app = tk.Tk()
app.title('MOIST')

app.mainloop()

