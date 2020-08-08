# Dynamixel-AX-12A

Requires an install of the [Dynamixel SDK](https://github.com/ROBOTIS-GIT/DynamixelSDK) -- thank you Leon!!! I am using the Python libraries, downloaded June 19, 2020 (So, version 3.7.21), and Python 3.6.9 on Ubuntu 18.04.

I haven't tested it on anything else, but it should be pretty broadly compatible with Python 3 on any platform.

This provides complete, high-level controls in a python environment for the Dynamixel AX-12A.

I set up methods for every memory address, read any of them, write any of the writeable ones, all by name.

Notice that I have attached two AX-12A eManuals, both provided by Robotis.  The one labeled AX-12 Bioloid is obsolete -- it is actually for a different motor which predates the AX-12A, but I found it to be easier to use since it is better formatted, and not significantly different from the AX-12A.  If you are looking at the eManuals, the idea of the Dynamixel SDK and this module is to provide an interface where you don't have to understand how to assemble the packets, or know what the specific memory addresses are, or any of that.  Together, these provide a high-level object-oriented interface that allows you to not worry about all of those details.

# Documentation

I strongly recommend that you have the [Dynamixel Wizard](http://www.robotis.us/dynamixel-management/) set up on some device, and you have a physical setup with power and data hookups for one or more Dynamixels so that you can use it. For example, if you have a Dynamixel where you don't know both the ID and baud rate, you can use the Dynamixel Wizard to reset the Dynamixel firmware, and these will be reset to default values. If you are resetting the firmware, ID and/or baud rate, you should have only one Dynamixel hooked up.

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

```python
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
AX_12A.connectAll()
motor1.setGoalPosition(512)
motor2.setGoalPosition(512)
```

Here, `connectAll()` is a class method and `setGoalPosition()` is an instance method.

### Class Methods

  * [`listInstances()`](#listinstances())
  * [`connectAll()`](#connectall())

#### `listInstances()`
  * Inputs: None
  * Returns: A list of AX_12A() objects.
  * Description: To get a list of all currently assigned instances of the class. Notice that each instance is added as part of the standard `init()` method, and therefore may include motors that are not yet connected.
  
Sample code:

```python
motor1 = AX_12A(id = 1)
motor1.connect()
motor2 = AX_12A(id = 2)
l = AX_12A.listInstances()
print(l)
# output should be something like: [<>,<>]
# Notice that motor1 is connected and motor2 is not, but both appear in the list, 
# with no indication of which is connected and which is not.
```

#### `connectAll()`
  * Inputs: None
  * Returns: None
  * Description: This will run the instance method `connect()` on each instance.
  
Sample code:

```python
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
AX_12A.connectAll()
# Now both motor1 and motor2 should be ready for read/write commands.
```

#### `getAll()`
  * Inputs: `method`: A string, the name of an instance method that reads from the servo memory.
  * Returns: A list, containing the values read from each servo.
  * Description: This will run the same `getXXX()` method on all instances and assemble the values in a single list.

Sample Code:

```python
motor1.AX_12A(id = 1)
motor2.AX_12A(id = 2)
AX_12A.connectAll()
positions = AX_12A.getAll('getPresentPosition')
print(positions)
# output should be something like: [ 511, 510 ]
# This output assumes both motors are very close to centered.
```

#### `setAll()`
  * Inputs:
    * `method`: A string, the name of an instance method that writes to the servo memory.
    * `value`: The value to be written to all servos
  * Return: A list, containing the value captured by each `setXXX()` method.  These should be `None` for each motor that successfully set the value as intended.
  * Description: This will run the same `{setmethod}(value)` method on each servo.
  
Sample Code:
```python
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
AX_12A.connectAll()
errs = AX_12A.setAll('setGoalPosition', 512)
AX_12A.waitForMotors()
print(errs)
# This should center both motors and then output: [ None, None ].
```

This is a shortcut for:
```python
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
motor1.connect()
motor2.connect()
errs = []
errs.append(motor1.setGoalPosition(512))
errs.append(motor2.setGoalPosition(512))
AX_12A.waitForMotors()
print(errs)
# This should center both motors and then output: [ None, None ].
```


#### `setPose()`
  * Input: List of integers, each a Goal Position for an AX-12A.  You can substitute `None` for any servo you wish to have hold its position.
  * Returns: None
  * Description: This is designed for use with a sequence of servos assembled together into a single body; this sets the body to a new 'pose' by setting the servos to new positions.  The length of the list does *not* have to be as long as the list of all servos, it will set the positions of the first *n* servos if given a list of length *n*, and leave all servos after the first *n* in their current position.  Notice that the ordering of the list depends on the order they are declared, so I strongly recommend declaring them in some order that makes sense with your construction.

Sample Code (I used this with the [PhantomX Pincher Robot Arm](https://www.trossenrobotics.com/p/PhantomX-Pincher-Robot-Arm.aspx), replacing the Arbotix controller with a linux-based microcontroller attached using a [Robotis U2D2](http://www.robotis.us/u2d2/)):

```python
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
motor3 = AX_12A(id = 3)
motor4 = AX_12A(id = 4)
motor5 = AX_12A(id = 5)
AX_12A.connectAll()
# Set arm to a stable rest position, with pincher open
AX_12A.setPose((512, 200, 1000, 650, 200)) # Notice double parentheses because the only argument is a list.
AX_12A.waitForMotors()
# Reach out with arm, leaving pincher open
AX_12A.setPose((None, 525, 710, 625)) # Leaves motor1 at 512 and motor5 at 200
AX_12A.waitForMotors()
# Close pincher
motor5.setGoalPosition(745)
AX_12A.waitForMotors()
# Retract arm, keeping pincher closed
AX_12A.setPose((None, 200, 1000, 650)) # Leaves motor1 at 512, and motor5 at 745
```

#### `readPose()`
  * Inputs: None
  * Returns: A list of integers, the positions of all of the declared motors.
  * Description: This is intended to simplify figuring out what the positions of the servos need to be to attain a certain position. The idea (see sample code below) would be to turn torque off on all the motors, then manually move the assembly to the desired position, and read the servo positions so that this position can be duplicated without excessive trial-and-error.

Sample Code (I used this with the [PhantomX Pincher Robot Arm](https://www.trossenrobotics.com/p/PhantomX-Pincher-Robot-Arm.aspx), replacing the Arbotix controller with a linux-based microcontroller attached using a [Robotis U2D2](http://www.robotis.us/u2d2/)):
```python
from time import sleep
motor1 = AX_12A(id = 1)
motor2 = AX_12A(id = 2)
motor3 = AX_12A(id = 3)
motor4 = AX_12A(id = 4)
motor5 = AX_12A(id = 5)
AX_12A.connectAll()
# Sleep so that you have time to move your hands from the keyboard to the robotic arm
sleep(5)
# Release all the motors so you can move them manually
AX_12A.setAll('setTorqueEnable', 0) 
# Wait until the motors stop moving to read the pose
AX_12A.waitForMotors()
pose = AX_12A.readPose()
print(pose)
# If I were figuring out where the rest position was with pincher open, 
# I would get output something like: [ 510, 206, 993, 642, 211 ]
# and then round off to get values in setPose() above.
```

#### `waitForMotors()`
 * Inputs: None
 * Returns: None
 * Description: Pauses execution of the script until all of the servos stop moving. This method does not determine *why* the motors are moving, it just pauses the program until they stop moving. It will remain paused even if only one of several motors is still moving. This is important to use with any setGoalPosition (including setPose()). If you use two successive setGoalPosition() commands with the same motor without waiting in between, the first will be wiped out by the second (see sample codes below). 

Sample Codes:
  * See `setAll()` above. In this script, if you had only this sample code, you wouldn't be able to see the difference whether or not you use `waitForMotors()`, except that, if you leave it out, the output would appear in the console and the script would end before the motors finished moving (assuming they had some distance to go to get to center).  This is because, once you send the command to set the new goal position, the motor will continue to move even after the script has ended as long as the motors have power.  However, if you had some other command involving these motors after the end of the sample lines, this command would overwrite the goal position before the motor completed its movement.
  * See `setPose()` above. In this script, if you leave out all of the `waitForMotors()` commands, the arm wouldn't reach at all and `motor5` would move from 200 to 745 (opening the pincher).  This is because the starting and ending positions are the same for the other four motors, and the new positions would overwrite so fast that the other four motors wouldn't get to execute the reach movement before being asked to go back to rest position.  Putting the `waitForMotors()` in means that the motors would first complete the movement to the new pose before moving on to the next pose.
  * See `readPose()` above. In this script, the `waitForMotors()` causes the script to wait until you stop manipulating the arm before it reads the new pose.  In practice, I found, at times, that I stopped moving the arm before I intended -- the `waitForMotors()` doesn't have any delay built in, so any pause at all in the movement will cause it to end, but then I just had to re-run the script.  
  
### Most Common Instance Methods

#### `connect()`
 * Inputs: None
 * Outputs: None
 * Description: Checks the connection to the motor and turns torque on; if `connect()` runs without error, then you know the motor is ready to use.  `connect()` does all of the following:
   * Checks if the motor has already been connected, using the `.connected` attribute.
   * Initializes the port and packet handlers set up by the Dynamixel SDK.
   * Sets the baud rate for communication to the motor.
   * Attempts a sample write, which enables Torque
   * Attempts a sample read
   * Checks if in Wheel Mode or Joint Mode
   * If in Joint Mode, checks if the current position is out of the designated range from CW Limit to CCW Limit; if so, moves it to the closest end of the range.
   * Set the `.connected` attribute to `True`.
   
See also the class method `connectAll()`.
   
Sample Code:
```python
motor1 = AX_12A(id = 1)
motor1.connect()
```

#### `disableTorque()`
 * Inputs: None
 * Outputs: None
 * Description: Turns torque off. This means that the servo will stop holding its position; if an external force is applied, the motor will turn, slowed only by inertia and friction. On an AX-12A, the gear inertia is quite significant if you have no leverage.  `motor.disableTorque()` is a shortcut for `motor.setTorqueEnable(0)`, mostly for readability.
 
Sample Code:
```python
motor1 = AX_12A(id = 1)
motor1.connect()
motor1.disableTorque()
```

See readPose() in Class Methods, above for why you might want to do this.

Sample Hack:

In the `readPose()` script, you could re-write the line `AX_12A.setAll('setTorqueEnable', 0)` as `AX_12A.getAll('disableTorque')` because the `getAll()` method will run any instance method that does not have an input value.  It doesn't read well, though, so I wouldn't do it.

#### `enableTorque()`
 * Inputs: None
 * Outputs: None
 * Description: Re-enables torque in a motor where it was disabled temporarily.  All motors have torque enabled as part of their `connect()` sequence, so you should only need this if you manually disabled torque.  `motor.enableTorque()` is a shortcut for `motor.setTorqueEnable(1)` mostly for readability.
 
Sample code (see readPose() above for why you might want to do this):
```python
from time import sleep
motor1 = AX_12A(id = 1)
motor1.connect()
sleep(3)
# Relax motor so it can be moved by hand
motor1.disableTorque()
# Wait until you are done moving it
AX_12A.waitForMotors()
# Hold the new position
motor1.enableTorque()
```
