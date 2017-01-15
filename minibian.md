# Setting up a Minibian system

If you want to use a smaller microSD card (2Gb, or even 1Gb) you might want to use [Minibian](https://minibianpi.wordpress.com/).

First of all (obviously) you will want to create a Minibian SD card and log into it - see the link above for instructions on this.
Once you've created the card, edit the file config.txt in /boot (or by mounting the card on a PC) and add this line:

```dtparam=i2c_arm=on```


Once booted and logged in, here are the commands you'll need before being able to run the vpower setup:

```apt-get install python
apt-get install raspi-config
apt-get install python-smbus
apt-get install i2c-tools
apt-get install python-pip
apt-get install git
apt-get install usbutils
```

Now you can go ahead and follow the instructions in README.md
