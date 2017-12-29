#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:   Dr. M. Luetzelberger
# Date:     2017-03-08
# Name:     sds011_pylab.py
# Purpose:  UI for controlling SDS011 PM sensor
# Version:  1.4.0
# License:  GPL 3.0
# Depends:  must use Python 2.7, requires matplotlib
# Changes:  Store data without simplekml module
#           Draw lines instead of placemarks
#           Improved user Interface
#           Auto sample time set to 600 seconds     
# Credits:  http://raspberryblog.de
#           c't Magazine, Issue 01/2018, https://github.com/custom-build-robots/Feinstaubsensor
# TODO:     Add datetime to UI 
#

from __future__ import print_function
from gps import *
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial, struct, time, pylab, csv, datetime, threading, tkMessageBox, os, getpass, subprocess

# open serial port
ser = serial.Serial()
#ser.port = sys.argv[1]
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

# setting the global variable
gpsd = None

# set path to data files
username = getpass.getuser()
datafile = "/home/" + username + "/data.csv"
kmlpath = "/home/" + username + "/kmldata/"

# requires gpsd /dev/ttyACM0 running in background
class GpsPoller(threading.Thread):
  def __init__(self):
    # bring it in scope
    global gpsd
    threading.Thread.__init__(self)
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
            # -- general settings and global variables --
            
            # sample time in "Auto" mode 
            global sampletime, intervall
            sampletime = 600
            intervall = 30
            
            # -- end of general settings --
            
            # generate UI
            frame = Frame(master)
            frame.pack()
            
            Label(frame, text="Lat: ", font=("Courier",10, "bold"), width=5).grid(row=0, column=0, columnspan=2)
            Label(frame, text="Lon: ", font=("Courier",10, "bold"), width=5).grid(row=1, column=0, columnspan=2)
            
            self.latitude = DoubleVar()
            Label(frame, textvariable=self.latitude,font=("Courier",10, "normal")).grid(row=0, column=1, columnspan=2)
            self.longitude = DoubleVar()
            Label(frame, textvariable=self.longitude,font=("Courier",10, "normal")).grid(row=1, column=1, columnspan=2)
            
            Label(frame, text="PM 2.5: ", font=("Courier",10, "bold"), width=8, fg="red").grid(row=0, column=3, columnspan=2)
            Label(frame, text="PM  10: ", font=("Courier",10, "bold"), width=8, fg="blue").grid(row=1, column=3, columnspan=2)
            
            self.result_pm25 = DoubleVar()
            Label(frame, textvariable=self.result_pm25, font=("Courier",10, "normal"), width=8).grid(row=0, column=4, columnspan=2)

            self.result_pm10 = DoubleVar()
            Label(frame, textvariable=self.result_pm10, font=("Courier",10, "normal"), width=8).grid(row=1, column=4, columnspan=2)
            
            
            Label(frame, text=u"µg/m\u00b3 ", font=("Courier",10, "bold"), width=8).grid(row=0, column=5, columnspan=2)
            Label(frame, text=u"µg/m\u00b3 ", font=("Courier",10, "bold"), width=8).grid(row=1, column=5, columnspan=2)
            
            
            if (self.is_running("gpsd") == True):
                Label(frame, text=" GPS: ON", fg="green", font=("Courier",10, "bold")).grid(row=0, rowspan=3,column=8)
            elif (self.is_running("gpsd") == False):
                Label(frame, text=" GPS: OFF", fg="red", font=("Courier",10, "bold")).grid(row=0, rowspan=3, column=8)

            button0 = Button(frame, text="Start", bg="green", fg="white", font=("Courier",10, "bold") , command=self.sensor_wake)
            button0.grid(row=4, column=2)

            button1 = Button(frame, text="Sleep", bg="red", fg="white", font=("Courier",10, "bold"), command=self.sensor_sleep)
            button1.grid(row=4, column=3)

            button2 = Button(frame, text="Read", bg="orange", fg="white", font=("Courier",10, "bold"), command=self.single_read)
            button2.grid(row=4, column=4)

            button3 = Button(frame, text="Auto", bg="brown", fg="white", font=("Courier",10, "bold"), command=self.sensor_live)
            button3.grid(row=4, column=5)

            button4 = Button(frame, text="Quit", bg="blue", fg="white", font=("Courier",10, "bold"), command=self.quit)
            button4.grid(row=4, column=6)

            #Label(frame, text="").grid(row=3, column=3)

            fig = pylab.figure(dpi=68, facecolor='w', edgecolor='k')
            self.canvas = FigureCanvasTkAgg(fig, master=master)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
            self.ax = fig.add_subplot(111) # 1st subplot 1x1 grid
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
            gps_time = gpsd.utc

            # print data on display
            self.latitude.set(str(latitude)[:6])
            self.longitude.set(str(longitude)[:6])
            self.result_pm25.set(pm25)
            self.result_pm10.set(pm10)

            # pack results into variable
            data = [pm25, pm10, longitude, latitude, gps_time]
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
            
            lat_old = "initial"
            lon_old = "initial"
            pm_old_25 = 0
            pm_old_10 = 0

            # create kml filenames
            fname25_line = kmlpath+'pm_25_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'
            fname10_line = kmlpath+'pm_10_line_'+datetime.datetime.now().strftime ("%Y%m%d_%H_%M_%S")+'.kml'
            
            # create kml files
            self.write_kml_file(fname25_line, "25")
            self.write_kml_file(fname10_line, "10")
            
            # sample each 30 s for 10 min
            for i in range(0, sampletime + intervall, intervall):
                self.sensor_wake()
                time.sleep(10)
                # get data from sensor
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
                    
                    # Note: order of data list [pm25, pm10, longitude, latitude]
                    
                    if lat_old == "initial":
                        lat_old = data[3]

                    if lon_old == "initial":    
                        lon_old = data[2]
                    
                    color_25 = self.color_selection(data[0])
                    color_10 = self.color_selection(data[1])
                    
                    self.write_kml_line(str(data[0]), str(pm_old_25), str(lon_old), str(lat_old), str(data[3]), str(data[2]), str(data[4]), fname25_line, color_25)
                    self.write_kml_line(str(data[1]), str(pm_old_10), str(lon_old), str(lat_old), str(data[3]), str(data[2]), str(data[4]), fname10_line, color_10)
                    
                    lat_old = data[3]
                    lon_old = data[2]
                
                    pm_old_25 = data[0]
                    pm_old_10 = data[1]
                    
                # discontinuous sensor read    
                self.sensor_sleep()
                time.sleep(20)
            
            # measurement done - send sensor to sleep
            self.sensor_sleep()
            
            # close kml files
            self.close_kml_file(fname25_line, "25")
            self.close_kml_file(fname10_line, "10")

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

        def is_running(self, process):
                s = subprocess.Popen(["ps","axw"],stdout=subprocess.PIPE)
                for x in s.stdout:
                        if re.search(process, x):
                                return True
                return False

        def clear_plot(self):
                self.ax.cla()
                self.ax.grid(True)
                self.ax.set_title("PM2.5 and PM10")
                self.ax.set_xlabel("Time (seconds)")
                self.ax.set_ylabel(u"PM (µg/m\u00b3)")
                self.ax.axis([0,sampletime,0,60])
                self.canvas.draw()

        def quit(self):
            root.destroy()
            
        def color_selection(self, value):
            # red
            color = "#64009614" 
            if 50 <= value <= 2000:
                color = "#641400F0"
            # orange
            elif 25 <= value <= 49:
                color = "#641478FF"
            # green
            elif 0 <= value < 25:
                color = "#64009614"     
            return color

        def write_kml_line(self, value_pm, value_pm_old, value_lon_old, value_lat_old, value_lat, value_lon, value_time, value_fname, value_color):
           pm = value_pm
           pm_old = value_pm_old
           lat_old = value_lat_old
           lon_old = value_lon_old
           lat = value_lat
           lon = value_lon
           time = value_time
           fname = value_fname
           color = value_color 
           
           with open(fname,'a+') as file:
                if os.path.exists(fname):
                    file.write("   <Placemark>\n")
                    file.write("   <name>"+ pm +"</name>\n")
                    file.write("    <description>"+ pm +"</description>\n")
                    file.write("    <Point>\n")
                    file.write("      <coordinates>" + lon + "," + lat + "," + pm + "</coordinates>\n")
                    file.write("    </Point>\n")
                    file.write("       <LineString>\n")
                    file.write("           <altitudeMode>relativeToGround</altitudeMode>\n")
                    file.write("           <coordinates>" + lon + "," + lat + "," + pm + "\n           "+ lon_old+ ","+ lat_old+ "," + pm_old + "</coordinates>\n")
                    file.write("       </LineString>\n")
                    file.write("       <Style>\n")
                    file.write("           <LineStyle>\n")
                    file.write("               <color>" + color + "</color>\n")
                    file.write("               <width>8</width>\n")
                    file.write("           </LineStyle>\n")
                    file.write("       </Style>\n")
                    file.write("   </Placemark>\n")   
                    file.close()
                    
        def write_kml_file(self, value_fname, pm_type):
            fname = value_fname
            with open(fname,'a+') as file:
                    file.write("<?xml version='1.0' encoding='UTF-8'?>\n")
                    file.write("<kml xmlns='http://earth.google.com/kml/2.1'>\n")
                    file.write("<Document>\n")
                    file.write("   <name> PM_Line_" + pm_type + "_" + datetime.datetime.now().strftime ("%Y%m%d") + ".kml </name>\n")
                    file.write('\n')
                    file.close()
                        
        # close file
        def close_kml_file(self, file_name, type):
            with open(file_name,'a+') as file:
                file.write("  </Document>\n")
                file.write("</kml>\n")  
                file.close()

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
