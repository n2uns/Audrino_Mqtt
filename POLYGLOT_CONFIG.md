
# MQTT Nodeserver for Arduino based software

[![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/exking/udi-mqtt-poly/blob/master/LICENSE)

This Poly provides an interface between MQTT broker and [Polyglot v2](https://github.com/UniversalDevicesInc/polyglot-v2) server.

[This thread](https://forum.universal-devices.com/topic/24538-sonoff/?tab=comments#comment-244571) on UDI forums has more details, ask questions there.

Note - your Sonoff MUST run the [Sonoff-Tasmota](https://github.com/arendst/Sonoff-Tasmota) firmware in order to work with MQTT!

 1. You will need a MQTT broker running (can be on RPi running Polyglot). (Likely already running, if you are on PG3 or PG3x on eISY)
	 -  See post #1 in [this thread](https://forum.universal-devices.com/topic/24538-sonoff) on how to setup.

 2. You will need to define the following custom parameters:
	 - `mqtt_server` - defaults to 'localhost' 
	 - `mqtt_port` - defaults to 1883, the example in the thread uses 1884  
	 - `mqtt_user` - username for the MQTT broker  
	 - `mqtt_password` - MQTT user's password  
	 - `devfile` - Alternative to `devlist` option below - use the yaml file instead, start with `devices:` and then same syntax
	 - `mqtt_topic` - You will need to put a topics to listen to, for example: 'mydevice'

