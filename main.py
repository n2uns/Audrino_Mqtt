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


class TestNode(udi_interface.Node):
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


def node_queue(data):
    n_queue.append(data['address'])


def wait_for_node_event():
    while len(n_queue) == 0:
        time.sleep(0.1)
    n_queue.pop()


'''
Read the user entered custom parameters. In this case, it is just
the 'multiplier' value.  Save the parameters in the global 'Parameters'
'''


def parameterHandler(params):
    global Parameters

    Parameters.load(params)


'''
This is where the real work happens.  When we get a shortPoll, increment the
count, report the current count in GV0 and the current count multiplied by
the user defined value in GV1. Then display a notice on the dashboard.
'''


def poll(polltype):
    global count
    global Parameters

    if 'shortPoll' in polltype:
        if Parameters['multiplier'] is not None:
            mult = int(Parameters['multiplier'])
        else:
            mult = 4

        node = polyglot.getNode('my_address')
        if node is not None:
            count += 1

            node.setDriver('GV0', count, True, True)
            node.setDriver('GV1', (count * mult), True, True)

            # be fancy and display a notice on the polyglot dashboard
            polyglot.Notices['count'] = 'Current count is {}'.format(count)


'''
When we are told to stop, we update the node's status to False.  Since
we don't have a 'controller', we have to do this ourselves.
'''


def stop():
    nodes = polyglot.getNodes()
    for n in nodes:
        nodes[n].setDriver('ST', 0, True, True)
    polyglot.stop()

def on_disconnect(client, userdata, rc):
    mqttc.is_connected = False
    if rc != 0:
        LOGGER.warning("Poly MQTT disconnected, trying to re-connect")
        try:
            mqttc.reconnect()
        except Exception as ex:
            LOGGER.error("Error connecting to Poly MQTT broker {}".format(ex))
    else:
        LOGGER.info("Poly MQTT graceful disconnection")

def on_connect(client, none, flags, rc):
    if rc == 0:
        LOGGER.info("Poly MQTT Connected, subscribing...")
        mqttc.is_connected = True
        result = mqttc.subscribe("mydevice/status")
        if result[0] == 0:
            LOGGER.info("Topic is ght ")
            LOGGER.info(
                "Subscribed to {} ".format("status")
        )
#        else:
#            LOGGER.error("Poly MQTT Connect failed")
#            mqttc.publish("mydevice/test", "this my test", qos=0, retain=False)
    else:
        LOGGER.error("Poly MQTT Connect failed")
def on_message(client, userdata, message):
    LOGGER.info("Received message '" + str(message.payload) + "' on topic '"
        + message.topic + "' with QoS " + str(message.qos))



if __name__ == "__main__":
    try:
        polyglot = udi_interface.Interface([])
        polyglot.start()

        Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, parameterHandler)
        polyglot.subscribe(polyglot.ADDNODEDONE, node_queue)
        polyglot.subscribe(polyglot.STOP, stop)
        polyglot.subscribe(polyglot.POLL, poll)
        # ************************   need to add in MQTT watch for tpoic infomation to see what nodes to add
        # ********************* then build the device of each one mybe one node for all IO
        # Start running
        polyglot.ready()
        polyglot.setCustomParamsDoc()
        polyglot.updateProfile()
        mqttc = mqtt.Client()
        mqttc.on_connect = on_connect
        on_disconnect = on_disconnect
        # mqttc.on_message = _on_message
        mqttc.is_connected = False

        mqttc.username_pw_set("n2uns", "kevin8386")
        try:
            mqttc.connect("192.168.18.185", 1884, 60)
            mqttc.loop_start()
        except Exception as ex:
            LOGGER.error("Error connecting to Poly MQTT broker {}".format(ex))

        LOGGER.info("Start")

        '''
        Here we create the device node.  In a real node server we may
        want to try and discover the device or devices and create nodes
        based on what we find.  Here, we simply create our node and wait
        for the add to complete.
        '''
        node = TestNode(polyglot, 'my_address', 'my_address', 'Counter')
        polyglot.addNode(node)
        wait_for_node_event()

        # Just sit and wait for events
        polyglot.runForever()
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
