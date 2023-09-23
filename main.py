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

# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


class Controller(udi_interface.Node):
    id = 'ctl'
    drivers = [
            {'driver': 'ST', 'value': 1, 'uom': 2},
            {'driver': 'GV0', 'value': 0, 'uom': 56},
            ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.n_queue = []

        self.Parameters = Custom(polyglot, 'customparams')

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.STOP, self.stop)
        polyglot.subscribe(polyglot.START, self.start, address)
        polyglot.subscribe(polyglot.ADDNODEDONE, self.node_queue)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    '''
    node_queue() and wait_for_node_event() create a simple way to wait
    for a node to be created.  The nodeAdd() API call is asynchronous and
    will return before the node is fully created. Using this, we can wait
    until it is fully created before we try to use it.
    '''
    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    '''
    Read the user entered custom parameters.  Here is where the user will
    configure the number of child nodes that they want created.
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)
        validChildren = False

        if self.Parameters['nodes'] is not None:
            if int(self.Parameters['nodes']) > 0:
                validChildren = True
            else:
                LOGGER.error('Invalid number of nodes {}'.format(self.Parameters['nodes']))
        else:
            LOGGER.error('Missing number of node parameter')


        if validChildren:
           # self.createChildren(int(self.Parameters['nodes']))
            self.poly.Notices.clear()
        else:
            self.poly.Notices['nodes'] = 'Please configure the number of child nodes to create.'


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
        # Not necessary to call this since profile_version is used from server.json
        self.poly.updateProfile()

