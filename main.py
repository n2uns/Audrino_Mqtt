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
        {'driver': 'GV1', 'value': 0, 'uom': 78},
        {'driver': 'GV2', 'value': 0, 'uom': 78},
        {'driver': 'GV3', 'value': 0, 'uom': 78},
        {'driver': 'GV4', 'value': 0, 'uom': 78},
        {'driver': 'GV5', 'value': 0, 'uom': 78},
        {'driver': 'GV6', 'value': 0, 'uom': 78},
        {'driver': 'GV7', 'value': 0, 'uom': 78},
        {'driver': 'GV8', 'value': 0, 'uom': 78},
        {'driver': 'GV0', 'value': 0, 'uom': 78},
        {'driver': 'GV9', 'value': 0, 'uom': 78},
        {'driver': 'GV11', 'value': 0, 'uom': 56},
        {'driver': 'GV12', 'value': 0, 'uom': 56},
        {'driver': 'GV13', 'value': 0, 'uom': 56},
        {'driver': 'GV14', 'value': 0, 'uom': 56},
        {'driver': 'GV15', 'value': 0, 'uom': 56},
        {'driver': 'GV16', 'value': 0, 'uom': 56},
        {'driver': 'GV17', 'value': 0, 'uom': 56},
        {'driver': 'GV18', 'value': 0, 'uom': 56},
        {'driver': 'GV19', 'value': 0, 'uom': 56},
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
        self.message =None
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
        LOGGER.debug("Start2")
        self.on_disconnect = self.on_disconnect
        self.mqttc.on_message = self.on_message
        self.mqttc.is_connected = False
        LOGGER.debug("Start3")

        self.mqttc.username_pw_set(self.mqtt_user, self.mqtt_password)
        self.mqttc.connect(self.mqtt_server, self.mqtt_port, 60)
        LOGGER.debug("Start4")
        self.mqttc.loop_start()
#        while self.valid_files is False:
#            LOGGER.info('Waiting on valid configuration files to be made')
#            time.sleep(5)
#        global drivers
#        Controller.updateDrivers(self,drivers)

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
                LOGGER.debug('short poll')


    '''
    Just to show how commands are implemented. The commands here need to
    match what is in the nodedef profile file. 
    '''

    def commandAO1(self, none):
        LOGGER.debug("anilog out up date mydat")
        result = self.mqttc.publish(self.mqtt_topic_cmd, self.drivers, )
        if result[0] == 0:
            LOGGER.info(
                "pushed to {} data = {}".format(self.mqtt_topic_cmd, self.drivers)
            )

    def mycommand(self, none):
        LOGGER.debug("anilog out up date mydat")
        result = self.mqttc.publish(self.mqtt_topic_cmd, self.drivers, )
        if result[0] == 0:
            LOGGER.info(
            "pushed to {} data = {}".format(self.mqtt_topic_cmd, self.drivers)
            )
        ##    ***************************************** need to add prosses commands all 10 outputs
    def discover(self, command=None):
        LOGGER.debug(
            "here here here i am *******************")
        result = self.mqttc.publish(self.mqtt_topic_Discovery, 1, )
        if result[0] == 0:
            LOGGER.info(
                "Subscribed to {} ".format(self.mqtt_topic_Discovery)
            )
    def noop(self):
        LOGGER.info('Discover not implemented')

    commands = {'DISCOVER': discover, 'GV5': commandAO1, 'GV6': mycommand, 'GV7': mycommand, 'GV8': mycommand, 'GV9': mycommand, 'GV16': mycommand, 'GV17': mycommand, 'GV18': mycommand, 'GV19': mycommand, 'GV20': mycommand}
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
                    "published to {} ".format(self.mqtt_topic_Discovery)
            )
        else:
            LOGGER.error("Poly MQTT Connect failed")
    def on_message(self, client, userdata, message):
        LOGGER.info("Received message '" + str(message.payload) + "' on topic '"
            + message.topic + "' with QoS " + str(message.qos))
        topic = message.topic
        payload = message.payload.decode("utf-8")
        self.json_payload = json.loads(payload)
        LOGGER.debug("Received jason payload {} and topic {}".format(self.json_payload, topic))
#    add build profile from discovery mesg **********************
        if topic == self.mqtt_topic_Discovery:
            LOGGER.debug("made it past topic")
            LOGGER.info(self.json_payload)
            if self.json_payload != 1:
                LOGGER.debug("made it past payload")

                f = open("profile/nls/en_us.txt", "wt")
                f.write("ND-test-NAME = Example - MyDevice\n")
                f.write("ND-test-ICON = Output\n")
                f.write("ST-str-ST-NAME = NodeServer Online\n")
                if "DI1" in self.json_payload :
                    f.write("ST-str-GV0-NAME = {}\n".format(self.json_payload["DI1"]))
                    LOGGER.debug("found DI1")
                if "DI2" in self.json_payload :
                    f.write("ST-str-GV1-NAME = {}\n".format(self.json_payload["DI2"]))
                    LOGGER.debug("found DI2")
                if "DI3" in self.json_payload :
                    f.write("ST-str-GV2-NAME = {}\n".format(self.json_payload["DI3"]))
                    LOGGER.debug("found DI3")
                if "DI4" in self.json_payload :
                    f.write("ST-str-GV3-NAME = {}\n".format(self.json_payload["DI4"]))
                    LOGGER.debug("found DI4")
                if "DI5" in self.json_payload :
                    f.write("ST-str-GV4-NAME = {}\n".format(self.json_payload["DI5"]))
                    LOGGER.debug("found AI1")
                if "DO1" in self.json_payload :
                    f.write("ST-str-GV5-NAME = {}\n".format(self.json_payload["DO1"]))
                    f.write("CMD-str-GV5-NAME = {}\n".format(self.json_payload["DO1"]))
                    LOGGER.debug("found DO1")
                if "DO2" in self.json_payload :
                    f.write("ST-str-GV6-NAME = {}\n".format(self.json_payload["DO2"]))
                    f.write("CMD-str-GV6-NAME = {}\n".format(self.json_payload["DO2"]))
                    LOGGER.debug("found DO2")
                if "DO3" in self.json_payload :
                    f.write("ST-str-GV7-NAME = {}\n".format(self.json_payload["DO3"]))
                    f.write("CMD-str-GV7-NAME = {}\n".format(self.json_payload["DO3"]))
                    LOGGER.debug("found DO3")
                if "DO4" in self.json_payload :
                    f.write("ST-str-GV8-NAME = {}\n".format(self.json_payload["DO4"]))
                    f.write("CMD-str-GV8-NAME = {}\n".format(self.json_payload["DO4"]))
                    LOGGER.debug("found DO4")
                if "DO5" in self.json_payload :
                    f.write("ST-str-GV9-NAME = {}\n".format(self.json_payload["DO5"]))
                    f.write("CMD-str-GV9-NAME = {}\n".format(self.json_payload["DO5"]))
                    LOGGER.debug("found AI1")
                if "AI1" in self.json_payload :
                    f.write("ST-str-GV11-NAME = {}\n".format(self.json_payload["AI1"]))
                    LOGGER.debug("found AI1")
                if "AI2" in self.json_payload :
                    f.write("ST-str-GV12-NAME = {}\n".format(self.json_payload["AI2"]))
                    LOGGER.debug("found AI2")
                if "AI3" in self.json_payload :
                    f.write("ST-str-GV13-NAME = {}\n".format(self.json_payload["AI3"]))
                    LOGGER.debug("found AI3")
                if "AI4" in self.json_payload :
                    f.write("ST-str-GV14-NAME = {}\n".format(self.json_payload["AI4"]))
                    LOGGER.debug("found AI4")
                if "AI5" in self.json_payload :
                    f.write("ST-str-GV15-NAME = {}\n".format(self.json_payload["AI5"]))
                    LOGGER.debug("found AI5")
                if "AO1" in self.json_payload :
                    f.write("ST-str-GV16-NAME = {}\n".format(self.json_payload["AO1"]))
                    f.write("CMD-str-GV16-NAME = {}\n".format(self.json_payload["AO1"]))
                    LOGGER.debug("found AO1")
                if "AO2" in self.json_payload :
                    f.write("ST-str-GV17-NAME = {}\n".format(self.json_payload["AO2"]))
                    f.write("CMD-str-GV17-NAME = {}\n".format(self.json_payload["AO2"]))
                    LOGGER.debug("found AO2")
                if "AO3" in self.json_payload :
                    f.write("ST-str-GV18-NAME = {}\n".format(self.json_payload["AO3"]))
                    f.write("CMD-str-GV18-NAME = {}\n".format(self.json_payload["AO3"]))
                    LOGGER.debug("found AO3")
                if "AO4" in self.json_payload :
                    f.write("ST-str-GV19-NAME = {}\n".format(self.json_payload["AO4"]))
                    f.write("CMD-str-GV19-NAME = {}\n".format(self.json_payload["AO4"]))
                    LOGGER.debug("found AO4")
                if "AO5" in self.json_payload :
                    f.write("ST-str-GV20-NAME = {}\n".format(self.json_payload["AO5"]))
                    f.write("CMD-str-GV20-NAME = {}\n".format(self.json_payload["AO5"]))
                    LOGGER.debug("found AO5")
                f.write("CMD-str-DISCOVER-NAME = Re-Discover\n")
                f.close()
                LOGGER.debug("made en_us.tx file starting node def file")

                f = open("profile/nodedef/nodedefs.xml", "wt")
                f.write('<nodeDefs>\n')
                f.write('   <nodeDef id="test" nls="str">\n')
                f.write("        <sts>\n")
                f.write('            <st id="ST" editor="bool" />\n')
                if "DI1" in self.json_payload :
                    f.write('            <st id="GV0" editor="DI" />\n')
                if "DI2" in self.json_payload :
                    f.write('            <st id="GV1" editor="DI" />\n')
                if "DI3" in self.json_payload :
                    f.write('            <st id="GV2" editor="DI" />\n')
                if "DI4" in self.json_payload :
                    f.write('            <st id="GV3" editor="DI" />\n')
                if "DI5" in self.json_payload :
                    f.write('            <st id="GV4" editor="DI" />\n')
                if "DO1" in self.json_payload :
                    f.write('            <st id="GV5" editor="DO" />\n')
                if "DO2" in self.json_payload :
                    f.write('            <st id="GV6" editor="DO" />\n')
                if "DO3" in self.json_payload :
                    f.write('            <st id="GV7" editor="DO" />\n')
                if "DO4" in self.json_payload :
                    f.write('            <st id="GV8" editor="DO" />\n')
                if "DO5" in self.json_payload :
                    f.write('            <st id="GV9" editor="DO" />\n')
                if "AI1" in self.json_payload :
                    f.write('            <st id="GV11" editor="AI" />\n')
                if "AI2" in self.json_payload :
                    f.write('            <st id="GV12" editor="AI" />\n')
                if "AI3" in self.json_payload :
                    f.write('            <st id="GV13" editor="AI" />\n')
                if "AI4" in self.json_payload :
                    f.write('            <st id="GV14" editor="AI" />\n')
                if "AI5" in self.json_payload :
                    f.write('            <st id="GV15" editor="AI" />\n')
                if "AO1" in self.json_payload :
                    f.write('            <st id="GV16" editor="AO" />\n')
                if "AO2" in self.json_payload :
                    f.write('            <st id="GV17" editor="AO" />\n')
                if "AO3" in self.json_payload :
                    f.write('            <st id="GV18" editor="AO" />\n')
                if "AO4" in self.json_payload :
                    f.write('            <st id="GV19" editor="AO" />\n')
                if "AO5" in self.json_payload :
                    f.write('            <st id="GV20" editor="AO" />\n')
                f.write('        </sts>\n')
                f.write('        <cmds>\n')
                f.write('            <sends >\n')
                if "DO1" in self.json_payload :
                    f.write('               <cmd id="GV5" >\n')
                    f.write('                   <p id="" editor="DO" init="GV5" />\n')
                    f.write('               </cmd >\n')
                if "DO2" in self.json_payload :
                    f.write('               <cmd id="GV6" >\n')
                    f.write('                   <p id="" editor="DO" init="GV6" />\n')
                    f.write('               </cmd >\n')
                if "DO3" in self.json_payload :
                    f.write('               <cmd id="GV7" >\n')
                    f.write('                   <p id="" editor="DO" init="GV7" />\n')
                    f.write('               </cmd >\n')
                if "DO4" in self.json_payload :
                    f.write('               <cmd id="GV8" >\n')
                    f.write('                   <p id="" editor="DO" init="GV8" />\n')
                    f.write('               </cmd >\n')
                if "DO5" in self.json_payload :
                    f.write('               <cmd id="GV9" >\n')
                    f.write('                   <p id="" editor="DO" init="GV9" />\n')
                    f.write('               </cmd >\n')
                if "AO1" in self.json_payload :
                    f.write('               <cmd id="GV16" >\n')
                    f.write('                   <p id="" editor="AO" init="GV16" />\n')
                    f.write('               </cmd >\n')
                if "AO2" in self.json_payload :
                    f.write('               <cmd id="GV17" >\n')
                    f.write('                   <p id="" editor="AO" init="GV17" />\n')
                    f.write('               </cmd >\n')
                if "AO3" in self.json_payload :
                    f.write('               <cmd id="GV18" >\n')
                    f.write('                   <p id="" editor="AO" init="GV18" />\n')
                    f.write('               </cmd >\n')
                if "AO4" in self.json_payload :
                    f.write('               <cmd id="GV19" >\n')
                    f.write('                   <p id="" editor="AO" init="GV19" />\n')
                    f.write('               </cmd >\n')
                if "AO5" in self.json_payload :
                    f.write('               <cmd id="GV20" >\n')
                    f.write('                   <p id="" editor="AO" init="GV20" />\n')
                    f.write('               </cmd >\n')
                f.write('           </sends>\n')
                f.write('           <accepts>\n')
                if "DO1" in self.json_payload :
                    f.write('               <cmd id="GV5" >\n')
                    f.write('                   <p id="" editor="DO" init="GV5" />\n')
                    f.write('               </cmd >\n')
                if "DO2" in self.json_payload :
                    f.write('               <cmd id="GV6" >\n')
                    f.write('                   <p id="" editor="DO" init="GV5" />\n')
                    f.write('               </cmd >\n')
                if "DO3" in self.json_payload :
                    f.write('               <cmd id="GV7" >\n')
                    f.write('                   <p id="" editor="DO" init="GV7" />\n')
                    f.write('               </cmd >\n')
                if "DO4" in self.json_payload :
                    f.write('               <cmd id="GV8" >\n')
                    f.write('                   <p id="" editor="DO" init="GV8" />\n')
                    f.write('               </cmd >\n')
                if "DO5" in self.json_payload :
                    f.write('               <cmd id="GV9" >\n')
                    f.write('                   <p id="" editor="DO" init="GV9" />\n')
                    f.write('               </cmd >\n')
                if "AO1" in self.json_payload :
                    f.write('               <cmd id="GV16" >\n')
                    f.write('                   <p id="" editor="AO" init="GV16" />\n')
                    f.write('               </cmd >\n')
                if "AO2" in self.json_payload :
                    f.write('               <cmd id="GV17" >\n')
                    f.write('                   <p id="" editor="AO" init="GV17" />\n')
                    f.write('               </cmd >\n')
                if "AO3" in self.json_payload :
                    f.write('               <cmd id="GV18" >\n')
                    f.write('                   <p id="" editor="AO" init="GV18" />\n')
                    f.write('               </cmd >\n')
                if "AO4" in self.json_payload :
                    f.write('               <cmd id="GV19" >\n')
                    f.write('                   <p id="" editor="AO" init="GV19" />\n')
                    f.write('               </cmd >\n')
                if "AO5" in self.json_payload :
                    f.write('               <cmd id="GV20" >\n')
                    f.write('                   <p id="" editor="AO" init="GV20" />\n')
                    f.write('               </cmd >\n')
                f.write('               <cmd id="DISCOVER" />\n')
                f.write('           </accepts>\n')
                f.write('       </cmds>\n')
                f.write('   </nodeDef>\n')
                f.write('</nodeDefs>\n')
                f.close()


                polyglot.updateProfile()
                self.poly.addNode(self)
                self.valid_files = True
        #        while self.valid_files is False:
        #            LOGGER.info('Waiting on valid configuration files to be made')
        #            time.sleep(5)

        # make sure node is fully up and running before we allow the status to execute ************************************************************************
        if topic == self.mqtt_topic_status:
            if self.valid_files is True:
                node = self.poly.getNode('controller')
                LOGGER.debug("updating status")
                if "DI1" in self.json_payload:
                    node.setDriver('GV0', (self.json_payload["DI1"]), True, True)
                    LOGGER.debug("found DI1")
                if "DI2" in self.json_payload:
                    node.setDriver('GV1', (self.json_payload["DI2"]), True, True)
                    LOGGER.debug("found DI2")
                if "DI3" in self.json_payload:
                    node.setDriver('GV2', (self.json_payload["DI3"]), True, True)
                    LOGGER.debug("found DI3")
                if "DI4" in self.json_payload:
                    node.setDriver('GV3', (self.json_payload["DI4"]), True, True)
                    LOGGER.debug("found DI4")
                if "DI5" in self.json_payload:
                    node.setDriver('GV4', (self.json_payload["DI5"]), True, True)
                    LOGGER.debug("found AI1")
                if "DO1" in self.json_payload :
                    node.setDriver('GV5', (self.json_payload["DO1"]), True, True)
                    LOGGER.debug("found DO1")
                if "DO2" in self.json_payload :
                    node.setDriver('GV6', (self.json_payload["DO1"]), True, True)
                    LOGGER.debug("found DO2")
                if "DO3" in self.json_payload :
                    node.setDriver('GV7', (self.json_payload["DO3"]), True, True)
                    LOGGER.debug("found DO3")
                if "DO4" in self.json_payload :
                    node.setDriver('GV8', (self.json_payload["DO4"]), True, True)
                    LOGGER.debug("found DO4")
                if "DO5" in self.json_payload :
                    node.setDriver('GV9', (self.json_payload["DO5"]), True, True)
                    LOGGER.debug("found AI1")
                if "AI1" in self.json_payload :
                    node.setDriver('GV11', (self.json_payload["AI1"]), True, True)
                    LOGGER.debug("found AI1")
                if "AI2" in self.json_payload :
                    node.setDriver('GV12', (self.json_payload["AI2"]), True, True)
                    LOGGER.debug("found AI2")
                if "AI3" in self.json_payload :
                    node.setDriver('GV13', (self.json_payload["AI3"]), True, True)
                    LOGGER.debug("found AI3")
                if "AI4" in self.json_payload :
                    node.setDriver('GV14', (self.json_payload["AI4"]), True, True)
                    LOGGER.debug("found AI4")
                if "AI5" in self.json_payload :
                   node.setDriver('GV15', (self.json_payload["AI5"]), True, True)
                   LOGGER.debug("found AI5")
                if "AO1" in self.json_payload :
                    node.setDriver('GV16', (self.json_payload["AO1"]), True, True)
                    LOGGER.debug("found AO1")
                if "AO2" in self.json_payload :
                    node.setDriver('GV17', (self.json_payload["AO2"]), True, True)
                    LOGGER.debug("found AO2")
                if "AO3" in self.json_payload :
                    node.setDriver('GV18', (self.json_payload["AO3"]), True, True)
                    LOGGER.debug("found AO3")
                if "AO4" in self.json_payload :
                    node.setDriver('GV19', (self.json_payload["AO4"]), True, True)
                    LOGGER.debug("found AO4")
                if "AO5" in self.json_payload :
                    node.setDriver('GV20', (self.json_payload["AO5"]), True, True)
                    LOGGER.debug("found AO5")


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
