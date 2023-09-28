#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys
import paho.mqtt.client as mqtt
import json

LOGGER = udi_interface.LOGGER

Custom = udi_interface.Custom

'''
Controller is interfacing with both Polyglot and the device. In this
case the device is just a count that has two values, the count and the count
multiplied by a user defined multiplier. These get updated at every
shortPoll interval.
'''
class Controller(udi_interface.Node):
    id = 'test'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            {'driver': 'GV1', 'value': 0, 'uom': 56},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []

        self.Parameters = Custom(polyglot, 'customparams')
        self.mqtt_server = "localhost"
        self.mqtt_port = 1883
        self.mqtt_user = None
        self.mqtt_password = None
        self.devlist = None
        self.INFO1 = None
        self.setup = 0
        self.mqtt_topic = None

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)

        # start processing events and create add our controller node
        polyglot.ready()
        # start mqtt
        polyglot.updateProfile()
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        LOGGER.info("Start2")
        self.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.on_message
        self.mqttc.is_connected = False
        LOGGER.info("Start3")

        self.mqttc.username_pw_set("n2uns", "kevin8386")
        self.mqttc.connect("192.168.18.185", 1884, 60)
        LOGGER.info("Start4")
        self.mqttc.loop_start()
        self.poly.addNode(self)

    '''
    Read the user entered custom parameters. In this case, it is just
    the 'multiplier' value.  Save the parameters in the global 'Parameters'
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.mqtt_server = self.Parameters["mqtt_server"] or 'localhost'
        self.mqtt_port = int(self.Parameters["mqtt_port"] or 1883)
        if self.Parameters["mqtt_user"] is None:
            LOGGER.error("mqtt_user must be configured")
        if self.Parameters["mqtt_password"] is None:
            LOGGER.error("mqtt_password must be configured")

        self.mqtt_user = self.Parameters["mqtt_user"]
        self.mqtt_password = self.Parameters["mqtt_password"]
        # ***************************************    read in the topic from config
        self.mqtt_topic = self.Parameters["mqtt_topic"]
        LOGGER.info("prams updted")
    '''
    This is called when the node is added to the interface module. It is
    run in a separate thread.  This is only run once so you should do any
    setup that needs to be run initially.  For example, if you need to
    start a thread to monitor device status, do it here.

    Here we load the custom parameter configuration document and push
    the profiles to the ISY.
    '''
    def start(self):
        self.poly.setCustomParamsDoc()
        self.poly.updateProfile()


    '''
    This is where the real work happens.  When we get a shortPoll, increment the
    count, report the current count in GV0 and the current count multiplied by
    the user defined value in GV1. Then display a notice on the dashboard.
    '''
    def poll(self, polltype):

        if 'shortPoll' in polltype:
            if self.Parameters['multiplier'] is not None:
                mult = int(self.Parameters['multiplier'])
            else:
                mult = 1

            node = self.poly.getNode('controller')
            if node is not None:
                self.count += 1

                node.setDriver('GV0', self.count, True, True)
                node.setDriver('GV1', (self.count * mult), True, True)

                # be fancy and display a notice on the polyglot dashboard
                self.poly.Notices['count2'] = 'Current count is {}'.format(self.count)
            else:
                LOGGER.error('Failed to find "controller" node')


    '''
    Just to show how commands are implemented. The commands here need to
    match what is in the nodedef profile file. 
    '''
    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}
    def on_disconnect(self, client, userdata, rc):
        self.mqttc.is_connected = False
        if rc != 0:
            LOGGER.warning("Poly MQTT disconnected, trying to re-connect")
            try:
                self.mqttc.reconnect()
            except Exception as ex:
                LOGGER.error("Error connecting to Poly MQTT broker {}".format(ex))
        else:
            LOGGER.info("Poly MQTT graceful disconnection")

    def on_connect(self, client, none, flags, rc):
        if rc == 0:
            LOGGER.info("Poly MQTT Connected, subscribing...")
            self.mqttc.is_connected = True
            result = self.mqttc.subscribe("mydevice/status")
            if result[0] == 0:
                LOGGER.info(
                    "Subscribed to {} ".format("status")
            )
        else:
            LOGGER.error("Poly MQTT Connect failed")
    def on_message(client, userdata, message):
        LOGGER.info("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))




if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        # Create the controller node
        Controller(polyglot, 'controller', 'controller', 'Counter')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
