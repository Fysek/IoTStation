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
        self.__currentActiveChannel = 0 #Number from 1-11
        self.__lastReadingsActiveChannel = collections.deque([0,0,0,0,0,0,0,0], maxlen=8)
        self.__blockedChannel = 0
        #MCP3008 #1
        self.__channels0[0] = AnalogIn(self.__mcp0, MCP.P0)
        self.__channels0[1] = AnalogIn(self.__mcp0, MCP.P1)
        self.__channels0[2] = AnalogIn(self.__mcp0, MCP.P2)
        self.__channels0[3] = AnalogIn(self.__mcp0, MCP.P3)
        self.__channels0[4] = AnalogIn(self.__mcp0, MCP.P4)
        self.__channels0[5] = AnalogIn(self.__mcp0, MCP.P5)
        self.__channels0[6] = AnalogIn(self.__mcp0, MCP.P6)
        self.__channels0[7] = AnalogIn(self.__mcp0, MCP.P7)


    
    def __debug_message(self, message):
        #logging.info(message)
        if DEBUG:
            print(message)
               
    def __isMoving(self):
        """
        Deque stores new values at the end
        Comparing last and penultimate reading
        """
        if(self.__lastReadingsActiveChannel[-1] - self.__lastReadingsActiveChannel[-2] > MOVING_DIFF):
            return True
        else:
            return False
    
    def __isMovingBackwards(self):
        """
        If different between two last readings is bigger than MOVING_BACK_DIFF then user is going backwards
        """
        if(self.__lastReadingsActiveChannel[-2] - self.__lastReadingsActiveChannel[-1] > MOVING_BACK_DIFF):
            return True
        else:
            return False
      
    def __isActiveTenTimes(self):
        """
        Checks if the current channel is active for last ten measurements
        """
        if(sum(self.__lastReadingsActiveChannel) > (LOW_VALUE_BORDER * 10)):
            return True
        else:
            return False            
                           
    def readValues(self):
        self.__debug_message("-----------------")
        
        #Scanning first MCP3008
        for i in range(8): self.__values[i] = self.__channels0[i].value
        time.sleep(self.__timeInterval) 

        ### DEBUG  
        self.__debug_message('All channels: ' + str(self.__values[0:2]))
        ###
       
    def evaluateValues(self):
        """
        Return active channel; 0 if nothing is acttive
        Return move flag
        """
        # No channel assigned
        if self.__currentActiveChannel == UNACTIVE_CHANNEL:
            if self.__blockedChannel != UNACTIVE_CHANNEL:# something is blocked
                if self.__values[self.__blockedChannel-1] < LOW_VALUE_BORDER:
                    self.__blockedChannel = UNACTIVE_CHANNEL #unblock channel
            else:# scanning for a new channel only if nothing is blocked
                for i in range(11):
                    if self.__values[i] > LOW_VALUE_BORDER:
                        self.__currentActiveChannel = i+1 
                        self.__lastReadingsActiveChannel.append(self.__values[i])

        else: ## Channel already assigned
            currentReading = self.__values[self.__currentActiveChannel-1]
            self.__lastReadingsActiveChannel.append(currentReading)
            
            if (currentReading > LOW_VALUE_BORDER): #active, channel stays, move depends, moving backwards cleans the
                self.__move = self.__isMoving()
                if self.__isMovingBackwards(): 
                    self.__blockedChannel = self.__currentActiveChannel #block channel until in released
                    self.__currentActiveChannel = UNACTIVE_CHANNEL
            else: # not active
                self.__move = False
                if not self.__isActiveTenTimes():
                    self.__currentActiveChannel = UNACTIVE_CHANNEL
                 
        ### DEBUG   
        self.__debug_message("Current active channel: " + str(self.__currentActiveChannel))
        self.__debug_message("Last readings: " + str(self.__lastReadingsActiveChannel))      
        #self.__debug_message("Move: " + str(self.__move))
        #self.__debug_message("Blocked channel: " + str(self.__blockedChannel))
        ###
        
        return self.__currentActiveChannel, self.__move
        
		
mcp = SliderScanner()
while(1):
	mcp.readValues()