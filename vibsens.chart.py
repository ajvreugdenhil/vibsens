# -*- coding: utf-8 -*-
# Description: Custom vibration sensor plugin
# Author: Bangedaon | Arjan Vreugdenhil

from serial.serialutil import SerialException
from bases.FrameworkServices.SimpleService import SimpleService
import serial
import json

import Queue  # queue in python3
import threading


ORDER = [
    'frequency',
    'amplitude',
    'max_amplitude',
    'sample_count'
]

CHARTS = {
    "frequency": {
        'options': [None, "Frequency (WIP)", "Hz", "vibsens", "vibsens.freq", "line"],
        'lines': [
            ["frequency_0", "frequency", "absolute", 1, 1]
        ]},
    "amplitude": {
        'options': [None, "Amplitude", "G", "vibsens", "vibsens.ampl", "line"],
        'lines': [
            ["amplitude_x", "X", "absolute", 1, 1],
            ["amplitude_y", "Y", "absolute", 1, 1],
            ["amplitude_z", "Z", "absolute", 1, 1]
        ]},
    "max_amplitude": {
        'options': [None, "Maximum amplitude", "G", "vibsens", "vibsens.maxampl", "line"],
        'lines': [
            ["max_amplitude_x", "X", "absolute", 1, 1],
            ["max_amplitude_y", "Y", "absolute", 1, 1],
            ["max_amplitude_z", "Z", "absolute", 1, 1]
        ]},
    "sample_count": {
        'options': [None, "Sample count", "", "vibsens", "vibsens.samples", "line"],
        'lines': [
            ["sample_count", "sample_count", "absolute", 1, 1]
        ]}
}

baudRate = 115200


class Service(SimpleService):
    def __init__(self, configuration=None, name=None):
        SimpleService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.c = None
        for i in range(1, 64):
            if self.c is None:
                try:
                    port = '/dev/ttyUSB' + str(i)
                    self.c = serial.Serial(port, baudRate, timeout=0.05)
                    # TODO: verify valid data coming from uart
                    self.debug(port + " is accessible")
                except:
                    pass

    def get_data(self):
        data = dict()
        
        
        input = self.receive_raw()
        if input is None:
            return data
            
        
        if input is not None:
            data["sample_count"] = input["SC"]
            data["max_amplitude_x"] = input["MA_X"]
            data["max_amplitude_y"] = input["MA_Y"]
            data["max_amplitude_z"] = input["MA_Z"]
            data["amplitude_x"] = input["AA_X"]
            data["amplitude_y"] = input["AA_Y"]
            data["amplitude_z"] = input["AA_Z"]
            data['frequency_0'] = 12
        return data

    def check(self):
        return True

    def receive_raw(self):
        if self.c is not None:
            try:
                self.c.write(b'\n')
                while self.c.in_waiting < 1:
                    pass
                if self.c.read(1) is not b'{':
                    self.c.readline()
            except IOError:
                self.error("IOError")
                return None
            except SerialException:
                self.error("SerialException again")
                return None
            response = ""
            try:
                response = self.c.readline().decode("utf-8").strip()
                if len(response) < 2:
                    #self.error("line read but found unexpected size")
                    return None
                response = '{' + response # because we don't have a peek() function
            except:
                #self.error("Could not read data")
                return None

            try:
                json_object = json.loads(response)
                return json_object
            except:
                #print("Json Parsing Failed: " + response)
                return None
        else:
            #self.error("Connection broken")
            return None
