# Python UI to display and read data from nova PM2.5/PM10 sensor (SDS011)

This is a simple TKinter UI to poll and display data from a nova PM2.5/PM10
 (particulate matter) sensor. TK window size is set to 480x320 to fit onto a Raspberry Pi 3.5"
TFT (touch) display.

[Link to SDS011 user guide](http://www.inovafitness.com/software/SDS011%20laser%20PM2.5%20sensor%20specification-V1.3.pdf)

Pressing the stop button sends the sensor to sleep mode. It disables both, fan
and laser diode in order to extend sensors's live-span. This feature wasn't 
documented in manufacturer's datasheet.

To re-enable laser diode and fan, press the start button.

Furthermore, a discontinuos mode for sensor reading was implemented. The record button
 enables discontinuos sensor reading for 5 min and writes data each 30 seconds into a
 CSV file (/home/pi/data.csv). 

During data recording, a live plot PM2.5/PM10 is presented in a mathplotlib window (see screenshot).

![Image](https://github.com/luetzel/sds011/blob/master/screenshot.png)

The script was created to build a portable PM2.5/PM10 monitoring device using
 a battery-powered Pi Zero W and 3.5" touch TFT.

## Installation

In order to run this script, python-matplotlib and python-tk must be installed. 
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

## Todo

* Add date time display.

## Known Bugs

* Sensor read fails in approx. 1 out of 10 attempts for unknown reason.

## Credits

* [Yet another Raspberry Blog](http://raspberryblog.de)
* [c't Make Magazine: Feinstaubmessung mit dem Raspi](https://www.heise.de/make/inhalt/2016/14/026/)
* [Raspberry Code Jam (Berlin)](http://raspberryjamberlin.de/)
