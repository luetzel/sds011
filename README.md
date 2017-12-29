# Python UI to display and read data from a nova PM2.5/PM10 sensor (SDS011)

This is a simple TKinter UI to poll and display data from a nova PM2.5/PM10
 (particulate matter) sensor. TK window size is set to 480x320 in order to
 fit onto a Waveshare 3.5" TFT (touch) display.

The script was created to build a portable PM2.5/PM10 monitoring device using a battery-powered
 Pi Zero W/ Raspberry Pi3 and 3.5" touch TFT.

![Image](https://github.com/luetzel/sds011/blob/googlemaps/raspi_mobile_sds011.jpg)

All components are attached to a Raspberry Pi via USB or using it's GPIO
header. The SDS sensor is connected through a USB-Serial-Converter, so that
PM data are retrieved from /dev/ttyUSB0. Information on how to convert sensor
 data into PM2.5 and PM10 values can be found within the [SDS011 user guide](http://www.inovafitness.com/software/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf)

Pressing the UI "Sleep" button sends the sensor into sleep mode. It disables both, fan
and laser diode in order to extend the their life-span. This feature isn't 
documented in the manufacturer's datasheet, but was already implemented in the
Windows software that is shipped with the sensor. To re-enable laser diode and fan, 
simply press the "Wake" button.

For single data recordings, press the "Read" button. It will spin-up the fan, polls the
sensor once and sends it to sleep again. 

Furthermore, a discontinuos "Auto" mode for sensor reading was implemented. The record button
 enables discontinuos sensor reading for a period of 10 minutes and writes data each 30 seconds
  into a CSV file which is located in (/home/\<username\>/data.csv). 

During data recording, a live plot PM2.5/PM10 is generated in a mathplotlib window (see screenshot).

![Image](https://github.com/luetzel/sds011/blob/googlemaps/screenshot1.png)

## Branches
The Python skript of the master branch provides only basic functionality and does not support
GPS. Both, the gpsdata and the googlemaps branch require a GPS mouse attached to your Pi.
The gpsdata branch depends on the simplekml Python module and represents sensor data
as placemarks. The googlemaps branch interconnects placemarks with colored lines.

For storing geographical data, I attached an (optional) NEO6 ublox GPS device to my Raspberry Pi.
 When a GPS signals is available, the script generates a KML file which can be imported to Google Maps
and/or GoogleEarth.

![Image](https://github.com/luetzel/sds011/blob/googlemaps/screenshot2.png)

PM values are represented as placemarks. The waypoints are interconnected by colored lines, where
green color indicates values below 25 ug/m3, orange color values above 25 < 49 ug/m3 and red color values 
above 50 ug/m3.

## UDEV Rule

To extend the sensors life-span, an udev.rule was created, which calls the Python script 
sds011_sleep.py. The 99-sds011_sensor.rules must be copied into /etc/udev/rules.d and the file 
sds011_sleep.py to /usr/local/bin.

When you plug the USB connector into your Raspberry, fan and laser diode will be disabled automatically.

## Installation

In order to run this script, python-matplotlib and python-tk must be installed on your machine.

On a Raspberry Pi do:

```
sudo apt-get install python-matplotlib python-tk
```

To connect with and read from GPS:

```
sudo apt-get install python gpsd gpsd-clients
```

For generating klm files (Google Maps Layer):

```
sudo pip install simplekml
```

## NTP and timezone
If you are going to build a portable sensor for outdoor use, you have to manually set the correct time
on your Raspberry. However, ntpd is able to retrieve the correct time from the GPS module. First, install
the ntp damon:

```
sudo apt-get install ntp
```
and add the following lines to your /etc/ntp.conf

```
server 127.127.28.0
fudge 127.127.28.0 refid GPSa
server 127.127.28.1
fudge 127.127.28.1 refid GPSp
```

## Changelog

* 2017-03-08	Initial version.
* 2017-03-11	Interconnect data points.
* 2017-03-17    New branch: Support ublox-6 GPS
                Requires installation of gps-tools
* 2017-03-18    UI improvements
                Created udev.rule and python script
                to disable fan/ diode on USB connection
* 2017-12-28    Small bugfixes, UI improvements

## Todo

* Add date time display.

## Known Bugs

* Sensor read fails sometimes for unknown reason.

## Credits

* [Köpfchen statt Kohle](koepchenstattkohle.org)
* [Luftdaten.info](http://luftdaten.info/)
* [Yet another Raspberry Blog](http://raspberryblog.de)
* [c't Make Magazine: Feinstaubmessung mit dem Raspi](https://www.heise.de/make/inhalt/2016/14/026/)
* [Raspberry Code Jam (Berlin)](http://raspberryjamberlin.de/)
* [Ingmar Stapel](https://github.com/custom-build-robots/Feinstaubsensor)
