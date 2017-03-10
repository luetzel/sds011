# Python UI to display and read data from nova PM2.5/PM10 sensor (SDS011)

This is a simple TKinter UI to poll and display data from a
nova PM2.5/PM10 (particulate matter) sensor.

Pressing the start/stop button sends the sensor to sleep.

In order to extend life of the laser diode, a discontinuos mode
for sensor reading was implemented.

The record button enables discontinuos reading for 5 min plots
PM2.5/PM10 in a mathplotlib window and stores data in a CSV with
timestamp.

Window size is set to 480x320 to fit on a Raspberry Pi 3.5"
TFT display.

Serves as portable PM2.5/10 monitoring device using a battery-powered
Pi Zero W.

## Depends

* apt-get install python-matplotlib
* TKinter

## Changelog

2017-03-08	Initial version.

## Todo

* Add date time display.
* Connect data points with lines


## Known Bugs

* Sensor read fails in 1 out of 10 attempts for unknown reason.
