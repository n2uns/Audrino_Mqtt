
# MQTT Nodeserver for Arduino based software

[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/exking/udi-mqtt-poly/blob/master/LICENSE)

This Poly provides an interface between MQTT broker and [Polyglot v3](https://github.com/UniversalDevicesInc/polyglot-v2) server.

on UDI forums has more details, ask questions there.

Note - your device MUST run the library isy_Arduino in order to work with Audrino_MQTT!

 1. You will need a MQTT broker running . (Likely already running, if you are on PG3 or PG3x on eISY or Polisy)

 2. You will need to define the following custom parameters:
	 - `mqtt_server` - defaults to 'localhost' 
	 - `mqtt_port` - defaults to 1883, the example in the thread uses 1884  
	 - `mqtt_user` - username for the MQTT broker  
	 - `mqtt_password` - MQTT user's password  
	 - `mqtt_topic` - You will need to put the name you gave your device, for example: 'mydevice'

