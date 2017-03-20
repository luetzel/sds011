#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:   Dr. M. Luetzelberger
# Date:     2017-03-08
# Name:     sds011_pylab.py
# Purpose:  UI for controlling SDS011 PM sensor
# Version:  1.2.0
# License:  GPL 3.0
# Depends:  must use Python 2.7, requires matplotlib
# Changes:
# Credits:  http://raspberryblog.de  
# TODO:     Add datetime to UI 
#

from __future__ import print_function
from gps import *
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial, struct, time, pylab, csv, datetime, threading, simplekml, tkMessageBox, os, getpass

# open serial port
ser = serial.Serial()
#ser.port = sys.argv[1]
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

# setting the global variable
gpsd = None

# path to log files
username = getpass.getuser()
kml = simplekml.Kml()
datafile = "/home/" + username + "/data.csv"
kmlpath = "/home/" + username + "/"

# requires gpsd /dev/ttyACM0 running in background
class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    # bring it in scope
    global gpsd
    # starting the stream of info
    gpsd = gps(mode=WATCH_ENABLE)
    self.current_value = None
    # setting the thread running to true
    self.running = True

  def run(self):
    global gpsd
    while gpsp.running:
      # this will continue to loop and grab EACH set of gpsd info to clear the buffer
      gpsd.next()

class App:
        def __init__(self, master):

            # generate UI
            frame = Frame(master)
            frame.pack()
            
            Label(frame, text="Lat: ").grid(row=0, column=0)
            Label(frame, text="Lon: ").grid(row=1, column=0)
            
            self.latitude = DoubleVar()
            Label(frame, textvariable=self.latitude).grid(row=0, column=1)
            self.longitude = DoubleVar()
            Label(frame, textvariable=self.longitude).grid(row=1, column=1)
            
            Label(frame, text="PM 2.5: ").grid(row=0, column=2)
            Label(frame, text="PM  10: ").grid(row=1, column=2)
            
            Label(frame, text="µg/m^3: ").grid(row=0, column=4)
            Label(frame, text="µg/m^3: ").grid(row=1, column=4)
            
            self.result_pm25 = DoubleVar()
            Label(frame, textvariable=self.result_pm25).grid(row=0, column=3)

            self.result_pm10 = DoubleVar()
            Label(frame, textvariable=self.result_pm10).grid(row=1, column=3)

            button0 = Button(frame, text="Start", command=self.sensor_wake)
            button0.grid(row=4, column=0)

            button1 = Button(frame, text="Sleep", command=self.sensor_sleep)
            button1.grid(row=4, column=1)

            button2 = Button(frame, text="Read", command=self.single_read)
            button2.grid(row=4, column=2)

            button3 = Button(frame, text="Auto", command=self.sensor_live)
            button3.grid(row=4, column=3)

            button4 = Button(frame, text="Quit", command=self.quit)
            button4.grid(row=4, column=4)

            #Label(frame, text="").grid(row=3, column=3)

            fig = pylab.Figure()
            self.canvas = FigureCanvasTkAgg(fig, master=master)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            self.ax = fig.add_subplot(1,1,1) # 1st subplot 1x1 grid
            self.clear_plot()
            self.plot = False
            
        # 0xAA, 0xB4, 0x06, 0x01, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x06, 0xAB
        def sensor_wake(self):
            bytes = ['\xaa', #head
            '\xb4', #command 1
            '\x06', #data byte 1
            '\x01', #data byte 2 (set mode)
            '\x01', #data byte 3 (sleep)
            '\x00', #data byte 4
            '\x00', #data byte 5
            '\x00', #data byte 6
            '\x00', #data byte 7
            '\x00', #data byte 8
            '\x00', #data byte 9
            '\x00', #data byte 10
            '\x00', #data byte 11
            '\x00', #data byte 12
            '\x00', #data byte 13
            '\xff', #data byte 14 (device id byte 1)
            '\xff', #data byte 15 (device id byte 2)
            '\x05', #checksum
            '\xab'] #tail

            for b in bytes:
                ser.write(b)
        
        # xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB
        def sensor_sleep(self):
            ser.flushInput()
            bytes = ['\xaa', #head
            '\xb4', #command 1
            '\x06', #data byte 1
            '\x01', #data byte 2 (set mode)
            '\x00', #data byte 3 (sleep)
            '\x00', #data byte 4
            '\x00', #data byte 5
            '\x00', #data byte 6
            '\x00', #data byte 7
            '\x00', #data byte 8
            '\x00', #data byte 9
            '\x00', #data byte 10
            '\x00', #data byte 11
            '\x00', #data byte 12
            '\x00', #data byte 13
            '\xff', #data byte 14 (device id byte 1)
            '\xff', #data byte 15 (device id byte 2)
            '\x05', #checksum
            '\xab'] #tail

            for b in bytes:
                ser.write(b)

        def process_frame(self, d):

            # dump raw data to console
            #dump_data(d)

            r = struct.unpack('<HHxxBBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(ord(v) for v in d[2:8])%256

            # print to console
            #print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))

            # read GPS position
            latitude = gpsd.fix.latitude
            longitude = gpsd.fix.longitude

            # print data on display
            self.latitude.set(str(latitude)[:6])
            self.longitude.set(str(longitude)[:6])
            self.result_pm25.set(pm25)
            self.result_pm10.set(pm10)

            # pack results into variable
            data = [pm25, pm10, longitude, latitude]
            return data

        def single_read(self):
            byte = 0
            self.sensor_wake()
            time.sleep(10)
            data = self.sensor_read()
            self.csv_save(data)
            self.sensor_sleep()
            return data
                   
        def sensor_read(self):
            ser.flushInput()
            byte = 0
            while byte != "\xaa":
                byte = ser.read(size=1)
                d = ser.read(size=10)
                if d[0] == "\xc0":
                    data = self.process_frame(byte + d)
                    return data

        def csv_save(self, data):
            mode = 'ab' if os.path.exists(datafile) else 'w+'
            with open(datafile, mode) as csvfile:
                        file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        file.writerow([str(gpsd.utc)[:19], data[0], data[1],data[3],data[2]])
                        csvfile.close()

        def sensor_live(self):
            # clear, if an old plot exists
            if self.plot == True:
                self.clear_plot()
                
            # init arrays to hold data points    
            x, y1, y2 = [], [], []

            # sample each 30 s for 5 min
            for i in range(0, 330, 30):
                self.sensor_wake()
                time.sleep(10)
                data = self.sensor_read()

            # plot data on display    
                if data is not None:
                    x.append(i)
                    y1.append(data[0])
                    y2.append(data[1])
                    line1, = self.ax.plot(x,y1,'r-x')
                    line2, = self.ax.plot(x,y2,'b-x')
                    self.canvas.draw()
                    # append to csv
                    self.csv_save(data)
                    # append to kml
                    self.kml_save(data)
                # discontinuous sensor read    
                self.sensor_sleep()
                time.sleep(20)

            self.sensor_sleep()

            # store GPS and sensor data in kml file
            kmlfile = kmlpath + "sample_" + str(datetime.datetime.now().replace(microsecond=0).isoformat()) + ".kml"                    
            kml.save(kmlfile)

            self.plot = True
            
            # recording done - start another cycle?
            root.withdraw()
            var = tkMessageBox.askyesno("Complete", "Continue?")
            if var == True:
                root.deiconify()
                root.update()
                self.sensor_live()
            else:
                root.deiconify()
                root.update()
                self.sensor_sleep()

        def clear_plot(self):
                self.ax.cla()
                self.ax.grid(True)
                self.ax.set_title("PM2.5 and PM10")
                self.ax.set_xlabel("Time (seconds)")
                self.ax.set_ylabel("PM (ug/m^3)")
                self.ax.axis([0,300,0,60])
                self.canvas.draw()

        def kml_save(self, data):
            # do not add points if thers is no GPS signal           
            if (str(data[2]) != "nan" and str(data[3]) != "nan"):    
                        pnt = kml.newpoint(name=gpsd.utc, coords=[(data[2],data[3])])  # lon, lat, optional height
                        pnt.description = "PM2.5: " + str(data[0]) +  " ug/m3 PM10: " + str(data[1]) + " ug/m3"

        def quit(self):
            root.destroy()

try:
    gpsp = GpsPoller()
    gpsp.start()
    root = Tk()
    root.wm_title("SDS011 PM Sensor")
    # hide window decoration
    #root.overrideredirect(True)
    app = App(root)
    root.geometry("480x320+0+0")
    root.mainloop()

except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nKilling Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
    print("Done.\nExiting.")
