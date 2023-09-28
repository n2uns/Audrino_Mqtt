#!/usr/bin/env python3
"""
Polyglot v3 node server Example 2
Copyright (C) 2021 Robert Paauwe

MIT License
"""
import udi_interface
import sys

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

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        polyglot.subscribe(polyglot.POLL, self.poll)
        polyglot.subscribe(polyglot.START, self.start, address)

        # start processing events and create add our controller node
        polyglot.ready()
        self.poly.addNode(self)

    '''
    Read the user entered custom parameters. In this case, it is just
    the 'multiplier' value.  Save the parameters in the global 'Parameters'
    '''
    def parameterHandler(self, params):
        self.Parameters.load(params)


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
