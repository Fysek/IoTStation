#!/usr/bin/python3
import busio
import digitalio
import board
import time
import logging
import collections
import adafruit_mcp3xxx.mcp3008 as MCP
from adafruit_mcp3xxx.analog_in import AnalogIn
#Only SIX ports are used on each MCP3008
#Read values 

DEBUG = 1
LOW_VALUE_BORDER = 640
UNACTIVE_CHANNEL = 0
MOVING_DIFF = 150
MOVING_BACK_DIFF = 400


def debug_message(message):
    if DEBUG:
        print(message)


class SliderScanner():
    def __init__(self, readInterval=1.0):
        self.__spi0 = busio.SPI(clock=board.SCK, MISO=board.MISO, MOSI=board.MOSI)
        self.__cs0_0 = digitalio.DigitalInOut(board.D8)
        self.__mcp0 = MCP.MCP3008(self.__spi0, self.__cs0_0)
        self.__timeInterval = readInterval
        self.__timeInterval = 10.0
        self.__channels0 = [0]*8
        self.__values = [0]*8
        self.__move = False
        self.__currentActiveChannel = 0 # Number from 1-11
        self.__lastReadingsActiveChannel = collections.deque([0,0,0,0,0,0,0,0], maxlen=8)
        self.__blockedChannel = 0
        self.__channels0[0] = AnalogIn(self.__mcp0, MCP.P0)
        self.__channels0[1] = AnalogIn(self.__mcp0, MCP.P1)
        self.__channels0[2] = AnalogIn(self.__mcp0, MCP.P2)
        self.__channels0[3] = AnalogIn(self.__mcp0, MCP.P3)
        self.__channels0[4] = AnalogIn(self.__mcp0, MCP.P4)
        self.__channels0[5] = AnalogIn(self.__mcp0, MCP.P5)
        self.__channels0[6] = AnalogIn(self.__mcp0, MCP.P6)
        self.__channels0[7] = AnalogIn(self.__mcp0, MCP.P7)

    def readValues(self):
        debug_message("-----------------")
        for i in range(8): self.__values[i] = self.__channels0[i].value
        time.sleep(self.__timeInterval)
        debug_message('All channels: ' + str(self.__values[0:2]))
       
e


mcp = SliderScanner()
while 1:
    mcp.readValues()
