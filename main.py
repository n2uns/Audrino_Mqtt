#!/usr/bin/env python3
from typing import Dict, List

import udi_interface
import sys
import logging
import paho.mqtt.client as mqtt
import json
import yaml
import time

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom

polyglot = None
Parameters = None
n_queue = []
count = 0

'''
TestNode is the device class.  Our simple counter device
holds two values, the count and the count multiplied by a user defined
multiplier. These get updated at every shortPoll interval
'''


class TestNode( udi_interface.Node):
    id = 'test'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 56},
        {'driver': 'GV1', 'value': 0, 'uom': 56},
    ]

    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': noop}


'''
node_queue() and wait_for_node_event() create a simple way to wait
for a node to be created.  The nodeAdd() API call is asynchronous and
will return before the node is fully created. Using this, we can wait
until it is fully created before we try to use it.
'''


def node_queue(self, data):
    self.n_queue.append(data['address'])


def wait_for_node_event():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()


'''
Read the user entered custom parameters. In this case, it is just
the 'multiplier' value.  Save the parameters in the global 'Parameters'
'''


def parameterHandler(self, params):
    self.name = "My Device"
    self.address = "mqctrl"
    self.mqtt_server = "localhost"
    self.mqtt_port = 1883
    self.mqtt_user = None
    self.mqtt_password = None
    self.mqtt_topic = None

    self.poly.Notices.clear()
    self.Parameters.load(params)


    self.mqtt_server = Parameters["mqtt_server"] or 'localhost'
    self.mqtt_port = int(Parameters["mqtt_port"] or 1883)
    if Parameters["mqtt_user"] is None:
        LOGGER.error("mqtt_user must be configured")
    if Parameters["mqtt_password"] is None:
        LOGGER.error("mqtt_password must be configured")

    self.mqtt_user = Parameters["mqtt_user"]
    self.mqtt_password = Parameters["mqtt_password"]
# ***************************************    read in the topic from config
    self.mqtt_topic = Parameters["mqtt_topic"]


'''
This is where the real work happens.  When we get a shortPoll, increment the
count, report the current count in GV0 and the current count multiplied by
the user defined value in GV1. Then display a notice on the dashboard.
'''


def poll(self, polltype):
    global count
    global Parameters

    if 'shortPoll' in polltype:
        if self.Parameters['multiplier'] is not None:
            mult = int(self.Parameters['multiplier'])
        else:
            mult = 4

        self.node = self.polyglot.getNode('my_address')
        if self.node is not None:
            count += 1

            self.node.setDriver('GV0', count, True, True)
            self.node.setDriver('GV1', (count * mult), True, True)

            # be fancy and display a notice on the polyglot dashboard
            self.polyglot.Notices['count'] = 'Current count is {}'.format(count)


'''
When we are told to stop, we update the node's status to False.  Since
we don't have a 'controller', we have to do this ourselves.
'''


def stop():
    nodes = polyglot.getNodes()
    for n in nodes:
        nodes[n].setDriver('ST', 0, True, True)
    polyglot.stop()

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


        def __init__(self, polyglot, primary, address, name):

            self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
            self.polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
            self.polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
            self.polyglot.subscribe(polyglot.STOP, stop)
            self.polyglot.subscribe(polyglot.POLL, poll)
        # ************************   need to add in MQTT watch for tpoic infomation to see what nodes to add
        # ********************* then build the device of each one mybe one node for all IO
        # Start running
            self.polyglot.ready()
            self.polyglot.setCustomParamsDoc()
            self.LOGGER.info("Start1")
            self.polyglot.updateProfile()
            self.mqttc = mqtt.Client()
            self.mqttc.on_connect = self.on_connect
            self.LOGGER.info("Start2")
            self.on_disconnect = self.on_disconnect
            self.mqttc.on_message = self.on_message
            self.mqttc.is_connected = False
            self.LOGGER.info("Start3")

            self.mqttc.username_pw_set("n2uns", "kevin8386")
            self.mqttc.connect("192.168.18.185", 1884, 60)
            self.LOGGER.info("Start4")
            self.mqttc.loop_start()
            node = TestNode(polyglot, 'my_address', 'my_address', 'Counter')
            self.LOGGER.info("Start5")
            self.polyglot.addNode(node)
            self.LOGGER.info("Start6")
            wait_for_node_event()

            self.LOGGER.info("Start7")
        polyglot.runForever()

        '''
        Here we create the device node.  In a real node server we may
        want to try and discover the device or devices and create nodes
        based on what we find.  Here, we simply create our node and wait
        for the add to complete.
        '''

        # Just sit and wait for events
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
