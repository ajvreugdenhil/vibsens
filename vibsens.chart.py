# -*- coding: utf-8 -*-
# Description: Custom vibration sensor plugin
# Author: Bangedaon | Arjan Vreugdenhil

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
        for i in range(64):
            if self.c is None:
                try:
                    port = '/dev/ttyUSB' + str(i)
                    self.c = serial.Serial(port, baudRate, timeout=0.1)
                    # TODO: verify valid data coming from uart
                    self.debug(port + " is accessible")
                except:
                    pass
        self.queue_lock = threading.Lock()
        self.queue = Queue.Queue()  # queue in python3
        self.listener = serialListener(self.queue, self.queue_lock, self.c)
        self.listener.start()

    def get_data(self):
        data = dict()
        raw_data = None
        self.queue_lock.acquire()
        if self.queue.qsize() < 1:
            return None

        batch_data = []
        while not self.queue.empty():
            batch_data.append(self.queue.get())
        self.queue_lock.release()

        data["sample_count"] = len(batch_data)

        data["max_amplitude_x"] = batch_data[0][0]
        data["max_amplitude_y"] = batch_data[0][1]
        data["max_amplitude_z"] = batch_data[0][2]
        for d in batch_data:
            if abs(d[0]) > abs(data["max_amplitude_x"]):
                data["max_amplitude_x"] = d[0]
            if abs(d[1]) > abs(data["max_amplitude_y"]):
                data["max_amplitude_x"] = d[1]
            if abs(d[2]) > abs(data["max_amplitude_z"]):
                data["max_amplitude_x"] = d[2]

        total_x = 0
        total_y = 0
        total_z = 0
        for d in batch_data:
            total_x += d[0]
            total_y += d[1]
            total_z += d[2]
        data["amplitude_x"] = total_x / len(batch_data)
        data["amplitude_y"] = total_y / len(batch_data)
        data["amplitude_z"] = total_z / len(batch_data)

        data['frequency_0'] = 12

        return data

    def check(self):
        return True


class serialListener (threading.Thread):
    def __init__(self, q, queueLock, c):
        threading.Thread.__init__(self)
        self.q = q
        self.c = c
        self.queueLock = queueLock
        self.running = False

    def run(self):
        self.running = True
        while (self.running):
            data = self.receive_raw()
            if data is not None:
                self.queueLock.acquire()
                self.q.put(data)
                self.queueLock.release()

    def exit(self):
        self.running = False

    def receive_raw(self):
        if self.c is not None:

            while self.c.in_waiting < 1:
                pass
            if self.c.read(1) is not b'[':
                self.c.readline()

            response = ""
            try:
                response = self.c.readline().decode("utf-8").strip()
                # because we don't have a peek() function
                response = '[' + response
            except:
                return None

            try:
                json_object = json.loads(response)
                if len(json_object) == 3:
                    return json_object
                else:
                    return None
            except:
                print("Json Parsing Failed: " + response)
                return None
        else:
            return None
