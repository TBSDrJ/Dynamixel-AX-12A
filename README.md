# Dynamixel-AX-12A

Requires an install of the [Dynamixel SDK](https://github.com/ROBOTIS-GIT/DynamixelSDK) -- thank you Leon!!! I am using the Python libraries, downloaded June 19, 2020 (So, version 3.7.21), and Python 3.6.9 on Ubuntu 18.04.

I haven't tested it on anything else, but it should be pretty broadly compatible with Python 3 on any platform.

This provides complete, high-level controls in a python environment for the Dynamixel AX-12A.

I set up methods for every memory address, read any of them, write any of the writeable ones, all by name.

Notice that I have attached two AX-12A eManuals, both provided by Robotis.  The one labeled AX-12 Bioloid is obsolete -- it is actually for a different motor which predates the AX-12A, but I found it to be easier to use since it is better formatted, and not significantly different from the AX-12A.

# Documentation

I strongly recommend that you have the [Dynamixel Wizard](http://www.robotis.us/dynamixel-management/) set up on some device, and you have a physical setup with power and data hookups for one or more Dynamixels so that you can use it. For example, if you have a Dynamixel where you don't know both the ID and baud rate, you can reset the Dynamixel firmware, and these will be reset to default values. If you are resetting the firmware, ID and/or baud rate, you should have only one Dynamixel hooked up.

This library contains one class: `AX_12A()`, and no functions.

## Class `AX_12A()`

### New Instances

Setting up a new instance of the class takes zero to four keyword arguments:
* `id`: default = `1` (matches factory default). The ID number of your smart servo. This can be set using the [Dynamixel Wizard](http://www.robotis.us/dynamixel-management/) or this library.  **If you are changing the ID of a Dynamixel, make sure you have only that one Dynamixel hooked up.**
* `baudRate`: default = `1000000` (matches factory default). This is equivalent to setting the value in the smart servo memory to 1.
* `devicePort`: default = '`/dev/ttyUSB0`'. This is the value if you are on a Linux system, and the USB-to-Serial device that you are using to connect to the Dynamixel is the first detected USB device. The last digit will change if it is not the first detected USB device; if you have multiple USB devices attached at bootup, the sequence may change unpredictably from one bootup to the next. If you are on a Windows system, this should take the form '`COM*`' and on a Mac, it will take the form '`/dev/tty.usbserial-*`'.
* `printInfo`: default = `True`. This flag determines if this library will output messages to console or not as it runs.  Note that any methods will return the appropriate value even if this is set to `False`, this only controls console output.

### Attributes

Each of the keyword arguments, above, is also an attribute for each instance.  In addition:
* `connected`: default = `False`. Set to `True` after the Dynamixel is connected (see `connect()` method below).
* Each memory address is also a constant attribute in the form `ADDR_XXX` (e.g. `ADDR_ID` or `ADDR_GOAL_POSITION)`.  I followed Leon's names as he set them up in the Dynamixel SDK, which occasionally differ slightly from the eManuals.  The complete list can be seen in the source code.

The class itself has one attribute:
* `AX_12A.instances`: default = `[]`. This is a list of all instances of the class, automatically added by the `init()` method. Notice that this means that instances could be in this list even though the associated motors have not been connected. This is intended for internal use, the method `AX_12A.listInstances()` will return this list.

## Methods

Notice that there are both instance methods and class methods. An instance method applies to a single instance of the `AX_12A` class; a class method applies to the entire class (and uses the `instances` attribute to apply to each instance).  For example:

`motor1 = AX_12A(id = 1)`
`motor2 = AX_12A(id = 2)`
`AX_12A.connectAll()`
`motor1.setGoalPosition(512)`
`motor2.setGoalPosition(512)`

Here, `connectAll()` is a class method and `setGoalPosition()` is an instance method.
