PiCade
======

PiCade is a Python Script intended to be used with a MCP23017 and a Raspberry Pi, for the purpose of Control Mappings

For more information on my Pi Project see picade.blogspot.com

Configuration:
==============

My Raspberry Pi was set up by Wiring the SDA, SCL, 3.3V and GND to 2 MCP23017 ICs in parallel.
http://ww1.microchip.com/downloads/en/DeviceDoc/21952b.pdf

In addition I mapped 2 pins on the GPIO board of the Pi to the INTA pins of the MCP23017.

Buttons were connected to the MCP23017 GPA0-GPA7 and GPB0-GPB-7 and GROUND.

When the ground and the pin is connected via the button (NO and GND) an interrupt is generated by the IC and sent via INTA 
to the PI, here we intercept the interrupt and go back and read the registers to find out which button was pressed or
released. 

The code then uses a dictionary to located the configured button which is fired using the Python uinput wrapper.
http://tjjr.fi/sw/python-uinput/

The original source code can be found 
https://github.com/jan1za/PiCade

Usage:
======

Once wired up run using super user:

sudo python picade.py


Dependencies:
=============

http://tjjr.fi/sw/python-uinput/

