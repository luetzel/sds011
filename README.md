# Python UI to display and read data from nova PM2.5/PM10 sensor (SDS011)

This is a simple TKinter UI to poll and display data from a
nova PM2.5/PM10 (particulate matter) sensor.

[SDS011](http://inovafitness.com/en/Laser-PM2-5-Sensor-SDS011-35.html)

Pressing the start/stop button wakes/sends the sensor from/to sleep mode.

In order to extend life of the laser diode, a discontinuos mode
for sensor reading was implemented.

The record button enables discontinuos reading for 5 min and writes 
data into a CSV. 

A Live plot PM2.5/PM10 is presented in a mathplotlib window
 (see screenshot).

TK window size is set to 480x320 to fit onto a Raspberry Pi 3.5"
TFT (touch) display.

Serves as portable app for PM2.5/PM10 monitoring using a battery-powered
Pi Zero W.

## Depends

In order to use this script, python-matplotlib and python-tk must be installed. 
On a Raspberry Pi do:

```
sudo apt-get install python-matplotlib python-tk
```

## Changelog

* 2017-03-08	Initial version.
* 2017-03-11	Interconnect data points.

## Todo

* Add date time display.

## Known Bugs

* Sensor read fails in 1 out of 10 attempts for unknown reason.

## Credits

* Raspberry Code Jam (Berlin)


