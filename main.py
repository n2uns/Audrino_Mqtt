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
import time

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
            {'driver': 'AO1', 'value': 0, 'uom': 56},
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
        self.mqtt_topic_cmd = None
        self.valid_configuration = False
        self.valid_files = False
        self.json_payload = None
        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)

        # start processing events and create add our controller node
        polyglot.ready()
        # start mqtt
        while self.valid_configuration is False:
            LOGGER.info('Waiting on valid configuration')
            time.sleep(5)
        self.mqttc = mqtt.Client()
        self.mqttc.on_connect = self.on_connect
        LOGGER.info("Start2")
        self.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.on_message
        self.mqttc.is_connected = False
        LOGGER.info("Start3")

        self.mqttc.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.mqttc.connect(self.mqtt_server, self.mqtt_port, 60)
        LOGGER.info("Start4")
        self.mqttc.loop_start()
        while self.valid_files is False:
            LOGGER.info('Waiting on valid configuration files to be made')
            time.sleep(5)

        polyglot.updateProfile()
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
        self.mqtt_topic_cmd = "{}/cmd".format(self.Parameters["mqtt_topic"])
        self.mqtt_topic_status = "{}/status".format(self.Parameters["mqtt_topic"])
        self.mqtt_topic_Discovery = "{}/Discovery".format(self.Parameters["mqtt_topic"])
        LOGGER.info("prams updted")
        self.valid_configuration = True

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
                mult = 2

            node = self.poly.getNode('controller')
            if node is not None:
                self.count += 1

                node.setDriver('AO1', self.count, True, True)
                node.setDriver('GV1', (self.count * mult), True, True)

                # be fancy and display a notice on the polyglot dashboard
                self.poly.Notices['count2'] = 'Current count is {}'.format(self.count)
            else:
                LOGGER.error('Failed to find "controller" node')


    '''
    Just to show how commands are implemented. The commands here need to
    match what is in the nodedef profile file. 
    '''
    def discover(self, command=None):
        LOGGER.info(
            "here here here i am *******************")
        result = self.mqttc.publish(self.mqtt_topic_Discovery, 1, )
        if result[0] == 0:
            LOGGER.info(
                "Subscribed to {} ".format(self.mqtt_topic_Discovery)
            )
    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': discover}
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
            result = self.mqttc.subscribe(self.mqtt_topic_status)
            if result[0] == 0:
                LOGGER.info(
                    "Subscribed to {} ".format(self.mqtt_topic_status)
            )
            result = self.mqttc.subscribe(self.mqtt_topic_cmd)
            if result[0] == 0:
                LOGGER.info(
                    "Subscribed to {} ".format(self.mqtt_topic_cmd)
            )
            result = self.mqttc.subscribe(self.mqtt_topic_Discovery)
            if result[0] == 0:
                LOGGER.info(
                    "Subscribed to {} ".format(self.mqtt_topic_Discovery)
            )
            result = self.mqttc.publish( self.mqtt_topic_Discovery, 1,)
            if result[0] == 0:
                LOGGER.info(
                    "Subscribed to {} ".format(self.mqtt_topic_Discovery)
            )
        else:
            LOGGER.error("Poly MQTT Connect failed")
    def on_message(self, client, userdata, message):
        LOGGER.info("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        self.json_payload = json.loads(payload)
        LOGGER.info("Received jason payload {} and topic {}".format(self.json_payload, topic))
#    add build profile from discovery mesg **********************
        if topic == self.mqtt_topic_Discovery:
            LOGGER.info("made it past topic")
            LOGGER.info(self.json_payload)
            if self.json_payload != 1:
                LOGGER.info("made it past payload")
                f = open("profile/nls/en_us.txt", "wt")
                f.write("ND-test-NAME = Example - MyDevice\n")
                f.write("ND-test-ICON = Output\n")
                f.write("ST-str-ST-NAME = NodeServer Online\n")
                f.write("ST-str-AO1-NAME = {}\n".format(self.json_payload["AO1"]))
                f.write("ST-str-GV1-NAME = {}\n".format(self.json_payload["DO1"]))
                f.write("CMD-str-DISCOVER-NAME = Re-Discover\n")
                f.close()
                self.valid_files = True

if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        # Create the controller node
        Controller(polyglot, 'controller', 'controller', 'Arduino MQTT')

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
