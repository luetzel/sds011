#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  sds011_sleep.py
#  
#  Copyright 2017 Dr. M. Luetzelberger <webmaster@raspberryblog.de>
#  
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#  
#

import serial, time
ser = serial.Serial()
ser.port = "/dev/ttyUSB0"
ser.baudrate = 9600
ser.open()
ser.flushInput()

# xAA, 0xB4, 0x06, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0x05, 0xAB
def sensor_sleep():
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

def main(args):
    time.sleep(10)
    sensor_sleep()
    ser.flushInput()	
    ser.close()

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
