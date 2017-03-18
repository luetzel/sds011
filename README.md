# Python UI to display and read data from nova PM2.5/PM10 sensor (SDS011)

This is a simple TKinter UI to poll and display data from a nova PM2.5/PM10
 (particulate matter) sensor. TK window size is set to 480x320 in order to fit onto a
 Raspberry Pi 3.5" TFT (touch) display.

[Link to SDS011 user guide](http://www.inovafitness.com/software/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf)

Pressing the "Sleep" button puts the sensor into sleep mode. It disables both, fan
and laser diode in order to extend the sensors's life-span. This feature wasn't 
documented in the manufacturer's datasheet.

To re-enable laser diode and fan, press the "Wake" button.

For single data recordings, press the "Read" button. It will spin-up the fan, poll the
sensor and send the sensor to sleep. 

Furthermore, a discontinuos "Auto" mode for sensor reading was implemented. The record button
 enables discontinuos sensor reading for a period of 5 minutes and writes data each 30 seconds
  into a CSV file which is located in (/home/<username>/data.csv). 

During data recording, a live plot PM2.5/PM10 is generated in a mathplotlib window (see screenshot).

![Image](https://github.com/luetzel/sds011/blob/master/screenshot.png)

The script was created to build a portable PM2.5/PM10 monitoring device using a battery-powered
 Pi Zero W and 3.5" touch TFT.

To store geographical data, I connected an (optional) NEO6 ublox GPS device. When GPS signals are received,
the script generates a KML file which can be imported to Google Maps.

## UDEV Rule

To extend the sensors life-span, an udev.rule was created, which calls sds011_sleep.py. The 99-sds011_sensor.rules
must be copied into /etc/udev/rules.d and sds011_sleep.py to /usr/local/bin.

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

## Changelog

* 2017-03-08	Initial version.
* 2017-03-11	Interconnect data points.
* 2017-03-17    New branch: Support ublox-6 GPS
                Requires installation of gps-tools
* 2017-03-18    UI improvements
                Created udev.rule and python script
                to disable fan/ diode on USB connection

## Todo

* Add date time display.

## Known Bugs

* Sensor read fails sometimes for unknown reason.

## Credits

* [Yet another Raspberry Blog](http://raspberryblog.de)
* [c't Make Magazine: Feinstaubmessung mit dem Raspi](https://www.heise.de/make/inhalt/2016/14/026/)
* [Raspberry Code Jam (Berlin)](http://raspberryjamberlin.de/)
