#! /usr/bin/env python

#   Copyright 2014 Jason F Nicholls
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#   This Python Script is intended to be used in conjunction with PiMame
#   More specifically Mame4All
#   However you can use it for what ever purpose you see a need
#	Basically it reads the GPIO board of the Pi, and waits for 
#   Events, if these events occur it reads 2 MCP23017 ICs for input
#   You can extend the Pi and use 8 ICs just extend this code
#   Note that ALL the pins of the ICs are setup as output.
#
#   For more information see picade.blogspot.com
#
#   Hope you have as much fun with your Pi as I have had with mine.

import RPi.GPIO as GPIO
import uinput 
import smbus
import time

# Custom Key Configuration, these keys will be mapped to your controls, below are the default MAME Controls.
DEFINED_KEYS = {
    'MCPA_A_0': uinput.KEY_5,      	 # Coin 1
    'MCPA_A_1': uinput.KEY_6,   	 # Coin 2
    'MCPA_A_2': uinput.KEY_1,  		 # Start 1
    'MCPA_A_3': uinput.KEY_2,  		 # Start 2
    'MCPA_A_4': uinput.KEY_ESC, 	 # Escape - exit the game
    'MCPA_A_5': uinput.KEY_P,  		 # Pause
    'MCPA_A_6': uinput.KEY_ENTER, 	 # Enter  
    'MCPA_A_7': uinput.KEY_TAB, 	 # Tab - Access in game menu
    'MCPA_B_0': uinput.KEY_G,  	 	 # Player 2 Right
    'MCPA_B_1': uinput.KEY_D, 	 	 # Player 2 Left
    'MCPA_B_2': uinput.KEY_F,	 	 # Player 2 Down
    'MCPA_B_3': uinput.KEY_R, 	 	 # Player 2 UP
    'MCPA_B_4': uinput.KEY_RIGHT,	 # Player 1 Right
    'MCPA_B_5': uinput.KEY_LEFT,	 # Player 1 Left
    'MCPA_B_6': uinput.KEY_DOWN,	 # Player 1 Down
    'MCPA_B_7': uinput.KEY_UP,		 # Player 1 Up
    'MCPB_A_0': uinput.KEY_LEFTCTRL,     # Player 1 Fire 1
    'MCPB_A_1': uinput.KEY_LEFTALT,	 # Player 1 Fire 2
    'MCPB_A_2': uinput.KEY_SPACE,	 # Player 1 Fire 3
    'MCPB_A_3': uinput.KEY_LEFTSHIFT,    # Player 1 Fire 4
    'MCPB_A_4': uinput.KEY_Z,	 	 # Player 1 Fire 5
    'MCPB_A_5': uinput.KEY_X,	         # Player 1 Fire 6
    'MCPB_A_6': uinput.KEY_SPACE,	 # Not used
    'MCPB_A_7': uinput.KEY_SPACE,        # Not used
    'MCPB_B_0': uinput.KEY_SPACE,	 # Not Used
    'MCPB_B_1': uinput.KEY_SPACE,	 # Not Used
    'MCPB_B_2': uinput.KEY_C,		 # C Player 2 Fire 6 // Normally Joystick 4 and is not set by default
    'MCPB_B_3': uinput.KEY_E,		 # E Player 2 Fire 5 // Normally Joystick 5 and is not set by default
    'MCPB_B_4': uinput.KEY_W,		 # W Player 2 Fire 4 // Normally Joystick 4 and is not set by default
    'MCPB_B_5': uinput.KEY_Q,		 # Q Player 2 Fire 3 // Normally Joystick 5 and is not set by default
    'MCPB_B_6': uinput.KEY_S,	 	 # S Player 2 Fire 2
    'MCPB_B_7': uinput.KEY_A,	 	 # A Player 2 Fire 1
  }

# Setup Variables and Constants
bus = smbus.SMBus(1) # Rev 2 Pi uses 1, Rev 1 Pi uses 0

# Device addresses refer to the A0-A2 Pins of the MCP23017 See the online manual
DEVICE_B = 0x20 # Device address (A0-A2 ALL GND)
DEVICE_A = 0x21 # Device B address (A0-A1 GND A2 VCC)

# The addresses below are all defined by the MCP23017 for more information see the online manual
# http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf
IODIRA   = 0x00 # Pin direction register
IODIRB	 = 0x01
IOPOLA   = 0x02 # Polarity
IOPOLB   = 0x03
GPINTENA = 0x04 # Interrupt on Change Manager
GPINTENB = 0x05
DEFVALA  = 0x06 # Default Value of the Register
DEFVALB  = 0x07
INTCONA  = 0x08 # Interrupt Control Register
INTCONB  = 0x09
IOCON    = 0x0A # Expander Configuration Bank, Mirrow, Sequential, Slew State, Hardware Address, Open Drain Int, Int Active High or Low
#ICON    = 0x0B # Not required
GPPUA    = 0x0C # Pull Up Register
GPPUB    = 0x0D
INTFA    = 0x0E # Flags the pin that caused the interrupt
INTFB    = 0x0F
INTCAPA  = 0x10 # The value of the pin at the time of the interrupt
INTCAPB  = 0x11
GPIOA    = 0x12 # Register for inputs
GPIOB    = 0x13
OLATA    = 0x14 #
OLATB    = 0x15

# Raspberry PI Pins will be used for interrupts
INT_PIN_B = 17
INT_PIN_A = 18

INT_PIN_D = 23
INT_PIN_C = 22

PIN_SHUTDOWN = 24 # We dont really need this, but I want to use this later to shut down the pi

DOWN_KEY  = 1 # Constant representing a push key value - required by uinput
UP_KEY    = 0 # Constant representing a release key value - required by uinput

# Initialize PI Pins
GPIO.setmode(GPIO.BCM)
# We are not using resistors externally so setup the internal pull up resistors for the Pi GPIO Pins, this means the button will pull it down from 3.3V to 0
GPIO.setup(INT_PIN_A, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INT_PIN_B, GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(INT_PIN_C, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(INT_PIN_D, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# We could have done the same above, just put this in to show the difference, here the base is 0 and it will be pulled up to 3.3V is the button is pressed.
GPIO.setup(PIN_SHUTDOWN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Get a handle to the keyboard Python uinput, defining all the keys we will be using
keyboard_device = uinput.Device([uinput.KEY_5,uinput.KEY_6, uinput.KEY_1, 
    uinput.KEY_2, uinput.KEY_ESC, uinput.KEY_P, 
    uinput.KEY_ENTER, uinput.KEY_TAB, uinput.KEY_UP, uinput.KEY_DOWN, 
    uinput.KEY_LEFT, uinput.KEY_RIGHT, uinput.KEY_R, uinput.KEY_F, 
    uinput.KEY_D, uinput.KEY_G, uinput.KEY_LEFTCTRL, uinput.KEY_LEFTALT, 
    uinput.KEY_SPACE, uinput.KEY_LEFTSHIFT, uinput.KEY_Z, uinput.KEY_X, 
    uinput.KEY_A, uinput.KEY_S, uinput.KEY_Q, uinput.KEY_W, uinput.KEY_E, uinput.KEY_C])
    

# Method to Setup each of the MCP23017 Devices
def setup_mcp(device_address):
  #Bank 0 Configuration with Interrupt Mirror Enabled, Active Int with Active Low
  bus.write_byte_data(device_address, IOCON, 0b00100000)
  # Turn on the PULL UP Register for the first line GPA0
  bus.write_byte_data(device_address, GPPUA, 0xFF)
  bus.write_byte_data(device_address, GPPUB, 0xFF)
  # Reverse the polarity
  bus.write_byte_data(device_address, IOPOLA, 0xFF)
  bus.write_byte_data(device_address, IOPOLB, 0xFF)
  # All pins as INPUT
  bus.write_byte_data(device_address, IODIRA, 0xFF)
  bus.write_byte_data(device_address, IODIRB, 0xFF)
  # Turn on Interrupts for the pin
  bus.write_byte_data(device_address, GPINTENA, 0xFF)
  bus.write_byte_data(device_address, GPINTENB, 0xFF)
  # Set the Int on Change to 0 so that the previous value is compared
  bus.write_byte_data(device_address, INTCONA, 0x00)
  bus.write_byte_data(device_address, INTCONB, 0x00)

#Translates the device, the control line and the button into a string for lookup
#def getCode(device, intf, switch):
#   if (device == DEVICE_A):
#      code = "MCPA_"
#   else:
#      code = "MCPB_"
#   if (intf == INTFA):
#      code = code + "A_"
#   else:
#      code = code + "B_"
#  
#   if (switch & 0x01):
#      code = code + "7"
#   if (switch & 0x02):
#      code = code + "6"
#   if (switch & 0x04):
#      code = code + "5"
#   if (switch & 0x08):
#      code = code + "4"
#   if (switch & 0x10):
#      code = code + "3"
#   if (switch & 0x20):
#      code = code + "2"
#   if (switch & 0x40):
#      code = code + "1"
#   if (switch & 0x80):
#      code = code + "0" 
#   return code

def setKeys(device, intf, buttonPressed, buttonState):
  #print "set key"
  if (device == DEVICE_A):
    code = "MCPA_"
  else:
    code = "MCPB_"
  if (intf == INTFA):
    code = code + "A_"
  else:
    code = code + "B_"
   
  for x in range(0,8):
    y = 0x80 >> x  

    #print "Searching ", code , " - ", y, " pressed ", (buttonPressed & y), " up down ", (buttonState & y)
    #if (buttonPressed & y):
    upDownValue = UP_KEY
    if (buttonState & y > 0):
      upDownValue = DOWN_KEY
    keyboard_device.emit(DEFINED_KEYS[code + str(x)], upDownValue)
    
       

#Findout which button was pressed and trigger the input   
def checkButton(device, intf, intcap):
  buttonPressed = bus.read_byte_data(device, intf)
  buttonValue = bus.read_byte_data(device, intcap)
  
  setKeys(device, intf, buttonPressed, buttonValue)
  
  #if (buttonPressed > 0) :
  #  upDownValue = UP_KEY
  #  if (buttonValue & buttonPressed > 0):
  #    upDownValue = DOWN_KEY
  #  keyboard_device.emit(DEFINED_KEYS[getCode(device, intf, buttonPressed)], upDownValue)

#Event Callbacks
def eventOnPinB(channel):
  #print "on B"
  time.sleep(0.03) #Sleep to cancel out bounce
  checkButton(DEVICE_B, INTFA, INTCAPA)
  #bus.read_byte_data(DEVICE_B, INTCAPA)
  #bus.read_byte_data(DEVICE_B, INTCAPB)
def eventOnPinD(channel):
  #print "On D"
  time.sleep(0.03) #Sleep to cancel out bounce
  checkButton(DEVICE_B, INTFB, INTCAPB)
#Event Callback for Pin A
def eventOnPinA(channel):
  #print "On A"
  time.sleep(0.03) #Sleep to cancel out bounce
  checkButton(DEVICE_A, INTFA, INTCAPA)
  #bus.read_byte_data(DEVICE_A, INTCAPA)
  #bus.read_byte_data(DEVICE_A, INTCAPB)
def eventOnPinC(channel):
  #print "on C"
  time.sleep(0.03) #Sleep to cancel out bounce
  checkButton(DEVICE_A, INTFB, INTCAPB)

# Initialise the devices
setup_mcp(DEVICE_A)
setup_mcp(DEVICE_B)

# Clear any data on the interrupt lines
bus.read_byte_data(DEVICE_A, INTCAPA)
bus.read_byte_data(DEVICE_A, INTCAPB)
bus.read_byte_data(DEVICE_B, INTCAPA)
bus.read_byte_data(DEVICE_B, INTCAPB)

# Add event detection
# Not that the bounce time is set to 0 and we handle the time in the callback
# The reason is that if an even happens within the time, it will be ignored
# But the MCP23017 will flag the interrupt even though the GPIO Event Detect will ignore
# the event. No new event will ever be processed because the event INTs must be cleared
# hence making it 0, means we will always read it, but we wait in the call back just incase
GPIO.add_event_detect(INT_PIN_A, GPIO.BOTH, callback=eventOnPinA, bouncetime=0) 
GPIO.add_event_detect(INT_PIN_B, GPIO.BOTH, callback=eventOnPinB, bouncetime=0)
GPIO.add_event_detect(INT_PIN_C, GPIO.BOTH, callback=eventOnPinC, bouncetime=0) 
GPIO.add_event_detect(INT_PIN_D, GPIO.BOTH, callback=eventOnPinD, bouncetime=0)

try:
  GPIO.wait_for_edge(PIN_SHUTDOWN, GPIO.RISING) # Wait for shutdown on pin 24 
#  while 1:
#    time.sleep(0.02)
except KeyboardInterrupt:
  GPIO.cleanup()    
  
GPIO.cleanup()

print "Done"

