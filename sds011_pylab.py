#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Author:   Dr. M. Luetzelberger
# Date:     2017-03-08
# Name:     sds011_pylab.py
# Purpose:  UI for controlling SDS011 PM sensor
# Version:  1.0.1
# Depends:  must use Python 2.7, requires matplotlib
# Changes:
# Credits:  http://raspberryblog.de  
# TODO:     Enable sleep on start
#           Add datetime to UI 

from __future__ import print_function
import serial, struct, time, pylab, csv, datetime
from Tkinter import *
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ser = serial.Serial()
#ser.port = sys.argv[1]
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600

ser.open()
ser.flushInput()

class App:
        def __init__(self, master):
            frame = Frame(master)
            frame.pack()
            Label(frame, text="PM 2.5: ", font=("Courier",10, "bold"), width=8).grid(row=0, column=0, columnspan=3)
            Label(frame, text=u"µg/m\u00b3 ", font=("Courier",10, "bold"), width=6).grid(row=0, column=3)
            Label(frame, text="PM  10: ", font=("Courier",10, "bold"), width=8).grid(row=1, column=0, columnspan=3)
            Label(frame, text=u"µg/m\u00b3 ", font=("Courier",10, "bold"),width=6).grid(row=1, column=3)
            
            self.result_pm25 = DoubleVar()
            Label(frame, textvariable=self.result_pm25, font=("Courier",10, "normal"), width=5).grid(row=0, column=2)

            self.result_pm10 = DoubleVar()
            Label(frame, textvariable=self.result_pm10, font=("Courier",10, "normal"), width=5).grid(row=1, column=2)

            button0 = Button(frame, text="Start", command=self.sensor_wake)
            button0.grid(row=2, column=0)

            button1 = Button(frame, text="Stop", command=self.sensor_sleep)
            button1.grid(row=2, column=1)

            button2 = Button(frame, text="Read", command=self.sensor_read)
            button2.grid(row=2, column=2)

            button3 = Button(frame, text="Record", command=self.sensor_live)
            button3.grid(row=2, column=3)

            button4 = Button(frame, text="Quit", command=self.quit)
            button4.grid(row=2, column=4)

            #Label(frame, text="").grid(row=3, column=3)

            fig = pylab.Figure()
            self.canvas = FigureCanvasTkAgg(fig, master=master)
            self.canvas.show()
            self.canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)

            self.ax = fig.add_subplot(111)
            self.ax.grid(True)
            self.ax.set_title("PM2.5 and PM10")
            self.ax.set_xlabel("Time (seconds)")
            self.ax.set_ylabel(u"PM (ug/m\u00b3)")
            self.ax.axis([0,300,0,60])
            
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
            '\x06', #checksum
            '\xab'] #tail

            for b in bytes:
                ser.write(b)
        
        # xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB
        def sensor_sleep(self):
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
            #dump_data(d) #debug
            r = struct.unpack('<HHxxBBB', d[2:])
            pm25 = r[0]/10.0
            pm10 = r[1]/10.0
            checksum = sum(ord(v) for v in d[2:8])%256
            #print("PM 2.5: {} μg/m^3  PM 10: {} μg/m^3 CRC={}".format(pm25, pm10, "OK" if (checksum==r[2] and r[3]==0xab) else "NOK"))
            self.result_pm25.set(pm25)
            self.result_pm10.set(pm10)
            data = [pm25, pm10]
            return data
            
        def sensor_read(self):
            byte = 0
            while byte != "\xaa":
                byte = ser.read(size=1)
                d = ser.read(size=10)
                if d[0] == "\xc0":
                    data = self.process_frame(byte + d)
                    return data

        def sensor_live(self):
            x = []
            y1 = []
            y2 = []
            for i in range(0,330,30): # change time interval here, if required
                self.sensor_wake()
                time.sleep(10)
                pm = self.sensor_read()
                if pm is not None:
                    x.append(i)
                    y1.append(pm[0])
                    y2.append(pm[1])
                    with open('/home/pi/data.csv', 'ab') as csvfile:
                        file = csv.writer(csvfile, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                        file.writerow([datetime.datetime.now().replace(microsecond=0).isoformat().replace('T', ' '), pm[0], pm[1]])
                        csvfile.close()
                    line1, = self.ax.plot(x,y1,'r-x')
                    line2, = self.ax.plot(x,y2,'b-x')
                    self.canvas.draw()
                self.sensor_sleep()
                time.sleep(20)

        def quit(self):
            root.destroy()

root = Tk()
root.wm_title("SDS011 PM Sensor")
# hide window decoration
root.overrideredirect(True)
app = App(root)
root.geometry("480x320+0+0")
root.mainloop()
