# ANT+ Virtual Power Meter

## Overview

This project implements "virtual power" for bicycle turbo trainers where the trainer or the attached bike has an ANT+ 
speed sensor. The calculated power is broadcasted as such on ANT+ so that any head unit or app will see it as a power
meter. Currently supported trainers are the 
[Bike Technologies Advanced Training System (BT-ATS)](http://www.biketechnologies.com/bt-advanced-training-system/) 
and the [Kurt Kinetic range of fluid trainers](https://kurtkinetic.com/products/trainers/). 

![vPower unit in action on a BT-ATS trainer](https://dl.dropboxusercontent.com/u/291298/vPower%20BT-ATS-small.JPG)

It is easy to add a new trainer - just subclass `AbstractPowerCalculator` and implement the method `power_from_speed(revs_per_sec)`.
If your trainer is not there, please add it and submit a pull request.

## Introduction
Many turbos, such as the Kurt Kinetic or Bike Technologies Advanced Training System (BT-ATS) have well-known and 
consistent power curves which make it possible to calculate the power from speed.
This concept is used in several applications (Zwift, Golden Cheetah, TrainerRoad, Sufferfest) to allow the user to 
behave as if they had a power meter. 

This is great, up to a point. One issue is that the calculated power is not shown on the user's bike computer, but only 
in the app (except for TrainerRoad). Another issue is that not all apps support all trainers (e.g. Zwift doesn't support
the BT-ATS). Even when a turbo is supported, the calculated power may differ from a rider's power meter by as much as 
5-10% - this is highly significant when doing intervals in the region of threshold or VO2max.

This project is designed to be run on a Raspberry Pi with an ANT+ stick plugged in, and will broadcast the calculated 
power over ANT+ so that bike computers and apps will see it as a regular ANT+ power meter. The project is designed to be
open-source and highly configurable - for example, the BT-ATS not only allows for a correction factor so that it 
matches, say, a power2max on another bike, but also it can read from a cheap weather sensor and correct for air density.
With these corrections, the calculated power is within 1 watt of a power2max power meter for durations of 10 seconds 
or more.

If you're not bothered about the air density correction then you don't even need a Raspberry Pi - any computer running
Linux will do (even a virtual machine running in Windows is fine) - all you need is a dedicated ANT+ USB stick.

The plan is to enhance the project further so that accelerations/decelerations can be factored in, increasing the 
accuracy in the sub-10 second range and making the project useful for calculating sprint power.

It may also be possible in future to do run-down calibrations to improve the accuracy of wheel-driven trainers such as 
the Kurt Kinetic, and such calibrations may also be able to calibrate for air density so that even the BME280 sensor is 
not needed.

This project can be built very cheaply. A sample bill of materials is as follows:

| Item | Price |
|------|-------|
| Raspberry Pi Zero: | $5 |
| microSD card with Raspbian: | $8 |
| Pi Zero USB hub: | $8 |
| micro-USB cable (for power): | $5 |
| ANT+ USB Stick: | $20 |
| USB ethernet/wifi adapter: | $9 |
| BME280 temperature/pressure/humidity sensor: | $5 |

So $60 in total, of which the $9 network adapter is only used for setting up the device; the $5 BME280 is only useful
for wind-resistance trainers like the BT-ATS and Lemond Revolution - you could just get a $5 case instead.

Anyway, under $60 isn't too bad for an ANT+ power meter :-)

## Setting up the software

1. Log into the Pi

2. Run `sudo raspi-config` and tell the Pi to boot to console only (to save memory)
 and enable I2C in "Interfacing options" if you plan to use a BME280 sensor for air density correction.

3. You can clone the repo on the Pi itself (3a), or simply download the zip file and extract it to the microSD
 card from a PC (3b).  
 
3a. Clone this repo and install the required Python libraries:

    cd /boot
    sudo git clone https://github.com/dhague/vpower.git
    cd vpower
    sudo pip install -r requirements.txt

3b. Download the zip file from the "Clone or download" button above and extract it to the microSD card so that the `vpower` folder
    contains the files from the repo.

4. Copy `vpower.cfg` to its parent folder (e.g. `/boot`) and then edit the values inside - typically you'll set
`speed_sensor_id` to the ANT+ ID of your speed sensor and `speed_sensor_type` to your type of sensor. 
Next, uncomment one of the `power_calculator` lines to tell *vpower* what type of turbo you are using.
If using a wheel-driven trainer you will then want to set the `wheel circumference` value.
If you have a wind trainer (i.e. the resistance comes purely from a fan in the air) then you will want to set the
`air_density` value for better accuracy.
Set `correction_factor` to 1.0 to begin with - you can adjust it later according to your own comparative tests or perceived 
exertion.

## [optional] Setting up air density correction using a [BME280 sensor](https://www.google.co.uk/search?q=bme280+sensor)

This is just a matter of downloading and setting up the BME280 Python module.

1. From the *parent* of the vpower folder (e.g. `/boot`), run:

    `wget https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/bme280.py`

Alternatively (if using option 3b above), download the file from 
[here](https://bitbucket.org/MattHawkinsUK/rpispy-misc/raw/master/python/bme280.py) 
and put it in the root of the microSD card.

2. On the Pi, run `sudo i2cdetect -y 1`

    if 77 is shown in the output grid, then edit `bme280.py` and change `0x76` to `0x77`
    (at line 27 or thereabouts)

3. Running `python bme280.py` should output the chip's data and the current temperature, pressure & humidity

## Running the virtual power meter (manual)

1. Log into the Pi

2. `cd /boot/vpower`

3. `sudo python vpower.py ../vpower.cfg`

You should see something like this:

    Power meter ANT+ ID: 37127
    Starting ANT node
    Starting speed sensor
    Using KurtKineticPowerCalculator
    Starting power meter
    Main wait loop
    +++++

Each `+` corresponds to a power message being sent, so these will only appear once you start pedalling.
If you have a BME280 sensor attached then you will also see some data on temperature, pressure, humidity and air density
and a `o` will occasionally appear when the air density is updated.

To stop the power meter running, just do `CTRL-C` and after a few seconds everything will be shut down and you can 
unplug the Pi.

You can turn on DEBUG/diagnostic output by setting `debug` to `True` in `vpower.cfg`.

## Installing the virtual power meter as a service which starts automatically

1. From the `init.d` folder of the repo, copy the `vpower` file to `/etc/init.d`, e.g.

    `sudo cp /boot/vpower/init.d/vpower /etc/init.d`

2. Configure the service to start at boot time:

    `sudo update-rc.d vpower defaults`