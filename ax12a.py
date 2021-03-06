# -*- coding: utf-8 -*-

# Author: Marcus Jaiclin, based on example by Ryu Woon Jung (Leon)
#
################# AX-12A Class #####################
#

from dynamixel_sdk import *                    # Uses Dynamixel SDK library
from time import sleep

class AX_12A:

    instances = []

    def __init__(self, id = 1, baudRate = 1000000, devicePort='/dev/ttyUSB0', printInfo=True):
        """
        Inputs: None
        Returns: None
        Purpose: Set up variables to match technical specifications
        """
        self.id                     = id
        self.baudRate               = baudRate
        # Default devicePort assumes Linux and first USB port. Windows:"COM*" Mac:"/dev/tty.usbserial-*"
        self.devicePort             = devicePort
        self.printInfo              = printInfo
        self.connected              = False
        # These will agree with values stored in Dynamixel memory typically
        # Except in Wheel Mode, when they will store prior value for returning to Joint Mode.
        self.cwAngleLimit           = None
        self.ccwAngleLimit          = None

        # Keep a list of all instances of this class for making poses
        self.__class__.instances.append(self)

        # Control table addresses. Look up in eManual, I am using decimal not hex.
        ### EEPROM: If writing to EEPROM, put in a 250 ms delay or you risk memory corruption.
        ### All of my methods below already have this delay built in.
        #   EEPROM changes are preserved until changed again, even if powered down.
        self.ADDR_MODEL_NUMBER          = 0     # Size 2 bytes  Default Value 12            READ ONLY
        self.ADDR_FIRMWARE_VERSION      = 2     # Size 1 byte   Default Value 2             READ ONLY
        self.ADDR_ID                    = 3     # Size 1 byte   Default Value 1
        self.ADDR_BAUD_RATE             = 4     # Size 1 byte   Default Value 1 (=> 1000000 bps)
        self.ADDR_RESPONSE_DELAY        = 5     # Size 1 byte   Default Value 250 ms
        self.ADDR_CW_ANGLE_LIMIT        = 6     # Size 2 bytes  Default Value 0
        self.ADDR_CCW_ANGLE_LIMIT       = 8     # Size 2 bytes  Default Value 1023
        self.ADDR_TEMPERATURE_LIMIT     = 11    # Size 1 byte   Default Value 70 deg C
        self.ADDR_MIN_VOLTAGE           = 12    # Size 1 byte   Default Value 60 (6.0 V)
        self.ADDR_MAX_VOLTAGE           = 13    # Size 1 byte   Default Value 140 (14.0 V)
        self.ADDR_MAX_TORQUE            = 14    # Size 2 bytes  Default Value 1023
        self.ADDR_STATUS_RETURN_LEVEL   = 16    # Size 1 byte   Default Value 2
        self.ADDR_ALARM_LED             = 17    # Size 1 byte   Default Value 36
        self.ADDR_SHUTDOWN              = 18    # Size 1 byte   Default Value 36
        ### End of EEPROM
        ### RAM Area: No delay needed
        #   Writeable RAM is all reset to default when powered up.
        self.ADDR_TORQUE_ENABLE         = 24    # Size 1 byte   Default Value 0 (Disabled)
        self.ADDR_LED                   = 25    # Size 1 byte   Default Value 0 (Off)
        self.ADDR_CW_COMPLIANCE_MARGIN  = 26    # Size 1 byte   Default Value 1
        self.ADDR_CCW_COMPLIANCE_MARGIN = 27    # Size 1 byte   Default Value 1
        self.ADDR_CW_COMPLIANCE_SLOPE   = 28    # Size 1 byte   Default Value 32
        self.ADDR_CCW_COMPLIANCE_SLOPE  = 29    # Size 1 byte   Default Value 32
        self.ADDR_GOAL_POSITION         = 30    # Size 2 bytes  Default Value (unknown)
        self.ADDR_MOVING_SPEED          = 32    # Size 2 bytes  Default Value 0
        self.ADDR_TORQUE_LIMIT          = 34    # Size 2 bytes  Default Value equal to Max Torque, ADDR 14
        self.ADDR_PRESENT_POSITION      = 36    # Size 2 bytes  Default Value --            READ ONLY
        self.ADDR_PRESENT_SPEED         = 38    # Size 2 bytes  Default Value --            READ ONLY
        self.ADDR_PRESENT_LOAD          = 40    # Size 2 bytes  Default Value --            READ ONLY
        self.ADDR_PRESENT_VOLTAGE       = 42    # Size 1 byte   Default Value --            READ ONLY
        self.ADDR_PRESENT_TEMPERATURE   = 43    # Size 1 byte   Default Value --            READ ONLY
        self.ADDR_REGISTERED            = 44    # Size 1 byte   Default Value 0             READ ONLY
        self.ADDR_MOVING                = 46    # Size 1 byte   Default Value 0             READ ONLY
        self.ADDR_LOCK                  = 47    # Size 1 byte   Default Value 0 (not locked)
        self.ADDR_PUNCH                 = 48    # Size 2 bytes  Default Value 32
        ### End of RAM area
        self.PROTOCOL_VERSION           = 1.0

    def __dxlSetter(self, numBytes, memAddr, valueToSet):
        if self.connected:
            if numBytes == 1:
                thisSetter = self.packetHandler.write1ByteTxRx
            elif numBytes == 2:
                thisSetter = self.packetHandler.write2ByteTxRx
            elif numBytes == 4:
                thisSetter = self.packetHandler.write4ByteTxRx
            else:
                if self.printInfo: print ("[INTERNAL ERROR] numBytes invalid in ax-12a method __dxlSetter().")
                return 3
            dxlCommResult, dxlError = thisSetter(self.portHandler, self.id, memAddr, valueToSet)
            if dxlCommResult != COMM_SUCCESS:
                if self.printInfo: print("%s" % self.packetHandler.getTxRxResult(dxlCommResult))
                return 1
            elif dxlError != 0:
                if self.printInfo: print("%s" % self.packetHandler.getRxPacketError(dxlError))
                return 2
            else:
                return 0
        else:
            if self.printInfo: print("[ERROR] ID:", self.id, "Motor not connected. Run .connect() method.")
            return 3

    def __dxlGetter(self, numBytes, memAddr):
        if self.connected:
            if numBytes == 1:
                thisGetter = self.packetHandler.read1ByteTxRx
            elif numBytes == 2:
                thisGetter = self.packetHandler.read2ByteTxRx
            elif numBytes == 4:
                thisGetter = self.packetHandler.read4ByteTxRx
            else:
                if self.printInfo: print ("[INTERNAL ERROR] numBytes invalid in ax-12a method __dxlGetter().")
                return None, 3
            getResult, dxlCommResult, dxlError = thisGetter(self.portHandler, self.id, memAddr)
            if dxlCommResult != COMM_SUCCESS:
                if self.printInfo: print("%s" % self.packetHandler.getTxRxResult(dxlCommResult))
                return None, 1
            elif dxlError != 0:
                if self.printInfo: print("%s" % self.packetHandler.getRxPacketError(dxlError))
                return None, 2
            else:
                return getResult, 0
        else:
            if self.printInfo: print("[ERROR] ID:", self.id, "Motor not connected. Run .connect() method.")
            return 3


################################################################################
##########                        EEPROM Area                         ##########
################################################################################

    def getModelNumber(self):
        modelNumber, modelNumberError = self.__dxlGetter(2, self.ADDR_MODEL_NUMBER)
        if modelNumberError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Model Number:", modelNumber)
            return modelNumber
        else:
            return None

    def getFirmwareVersion(self):
        firmwareVersion, firmwareVersionError = self.__dxlGetter(1, self.ADDR_FIRMWARE_VERSION)
        if firmwareVersionError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Firmware Version:", firmwareVersion)
            return firmwareVersion
        else:
            return None

    def getID(self):
        idNum, idNumError = self.__dxlGetter(1, self.ADDR_ID)
        if idNumError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "ID Read from memory:", idNum)
            return idNum
        else:
            return None

    def setID(self, idNumValue):
        idNumError = self.__dxlSetter(1, self.ADDR_ID, idNumValue)
        if idNumError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "ID set to", idNumValue)
            sleep(0.25)
            return None
        else:
            return idNumError

    def getBaudRate(self):
        baudRate, baudRateError = self.__dxlGetter(1, self.ADDR_BAUD_RATE)
        if baudRateError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Baud Rate read from memory:", baudRate)
            return baudRate
        else:
            return None

    def setBaudRate(self, baudRateValue):
        baudRateError = self.__dxlSetter(1, self.ADDR_BAUD_RATE, baudRateValue)
        if baudRateError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Baud Rate set to", baudRateValue)
            sleep(0.25)
            return None
        else:
            return baudRateError

    def getResponseDelay(self):
        responseDelay, responseDelayError = self.__dxlGetter(1, self.ADDR_RESPONSE_DELAY)
        if responseDelayError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Response Delay:", responseDelay)
            return responseDelay
        else:
            return None

    def setResponseDelay(self, responseDelayValue):
        responseDelayError = self.__dxlSetter(1, self.ADDR_RESPONSE_DELAY, responseDelayValue)
        if responseDelayError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Response Delay set to", responseDelayValue)
            sleep(0.25)
            return None
        else:
            return responseDelayError

    def getCwAngleLimit(self):
        cwAngleLimit, cwAngleLimitError = self.__dxlGetter(2, self.ADDR_CW_ANGLE_LIMIT)
        if cwAngleLimitError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CW Angle Limit:", cwAngleLimit)
            return cwAngleLimit
        else:
            return None

    def setCwAngleLimit(self, cwAngleLimitValue):
        # CW Angle Limit has to be less than CCW Angle Limit
        # Need equals to be able to enter Wheel Mode
        if cwAngleLimitValue <= self.ccwAngleLimit:
            cwAngleLimitError = self.__dxlSetter(2, self.ADDR_CW_ANGLE_LIMIT, cwAngleLimitValue)
            if cwAngleLimitError == 0:
                if self.printInfo: print("[WRITE] ID:", self.id, "CW Angle Limit set to", cwAngleLimitValue)
                self.cwAngleLimit = cwAngleLimitValue
                sleep(0.25)
                return None
            else:
                return cwAngleLimitError
        else:
            errorString = "[ERROR] ID: " + str(self.id) + " Cannot set CW Angle Limit to be greater than CCW Angle Limit."
            if self.printInfo: print(errorString)
            return errorString

    def getCcwAngleLimit(self):
        ccwAngleLimit, ccwAngleLimitError = self.__dxlGetter(2, self.ADDR_CCW_ANGLE_LIMIT)
        if ccwAngleLimitError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CCW Angle Limit:", ccwAngleLimit)
            return ccwAngleLimit
        else:
            return None

    def setCcwAngleLimit(self, ccwAngleLimitValue):
        # CCW Angle Limit has to be greater than CW Angle Limit
        # Need equals to be able to enter Wheel Mode
        if ccwAngleLimitValue >= self.cwAngleLimit:
            ccwAngleLimitError = self.__dxlSetter(2, self.ADDR_CCW_ANGLE_LIMIT, ccwAngleLimitValue)
            if ccwAngleLimitError == 0:
                if self.printInfo: print("[WRITE] ID:", self.id, "CCW Angle Limit set to", ccwAngleLimitValue)
                self.ccwAngleLimit = ccwAngleLimitValue
                sleep(0.25)
                return None
            else:
                return ccwAngleLimitError
        else:
            errorString = "[ERROR] ID: " + str(self.id) + " Cannot CCW Angle Limit to be less than CW Angle Limit."
            if self.printInfo: print(errorString)
            return errorString

    def wheelMode(self):
        # The variable localPrintInfo saves the state of self.printInfo.
        # If self.printInfo was on, this allows some work to be done silently temporarily,
        #   and a single message is printed at the end.
        localPrintInfo = self.printInfo
        if localPrintInfo: self.printInfo = False
        # Also remember Angle Limits so we can re-set them if we go back to Joint Mode.
        tmpCwAngleLimit = self.cwAngleLimit
        tmpCcwAngleLimit = self.ccwAngleLimit
        self.setCwAngleLimit(0)
        self.setCcwAngleLimit(0)
        # Both will have been set to zero, save the values that were there.
        self.cwAngleLimit = tmpCwAngleLimit
        self.ccwAngleLimit = tmpCcwAngleLimit
        if localPrintInfo:
            print("[INFO] ID:", self.id, "set to wheel mode.")
            self.printInfo = True

    def jointMode(self):
        # Check if stored values make sense.  If so, use them.
        if self.cwAngleLimit >= 0 and self.cwAngleLimit < 1023:
            if self.ccwAngleLimit > 0 and self.ccwAngleLimit <=1023:
                if self.cwAngleLimit < self.ccwAngleLimit:
                    if self.printInfo: print("[INFO] ID:", self.id, "set to joint mode.")
                    self.setCwAngleLimit(self.cwAngleLimit)
                    self.setCcwAngleLimit(self.ccwAngleLimit)
                    return
        # If they don't make sense for any reason, set to defaults.
        self.setCwAngleLimit(0)
        self.setCcwAngleLimit(1023)

    def getTemperatureLimit(self):
        temperatureLimit, temperatureLimitError = self.__dxlGetter(1, self.ADDR_TEMPERATURE_LIMIT)
        if temperatureLimitError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Temperature Limit:", temperatureLimit)
            return temperatureLimit
        else:
            return None

    def setTemperatureLimit(self, temperatureLimitValue):
        temperatureLimitError = self.__dxlSetter(1, self.ADDR_TEMPERATURE_LIMIT, temperatureLimitValue)
        if temperatureLimitError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Temperature Limit set to", temperatureLimitValue)
            sleep(0.25)
            return None
        else:
            return temperatureLimitError

    def getMinVoltage(self):
        minVoltage, minVoltageError = self.__dxlGetter(1, self.ADDR_MIN_VOLTAGE)
        if minVoltageError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Minimim Voltage:", minVoltage)
            return minVoltage
        else:
            return None

    def setMinVoltage(self, minVoltageValue):
        minVoltageError = self.__dxlSetter(1, self.ADDR_MIN_VOLTAGE, minVoltageValue)
        if minVoltageError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Minimum Voltage set to", minVoltageValue)
            sleep(0.25)
            return None
        else:
            return minVoltageError

    def getMaxVoltage(self):
        maxVoltage, maxVoltageError = self.__dxlGetter(1, self.ADDR_MAX_VOLTAGE)
        if maxVoltageError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Maximum Voltage:", maxVoltage)
            return maxVoltage
        else:
            return None

    def setMaxVoltage(self, maxVoltageValue):
        maxVoltageError = self.__dxlSetter(1, self.ADDR_MAX_VOLTAGE, maxVoltageValue)
        if maxVoltageError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Maximum Voltage set to", maxVoltageValue)
            sleep(0.25)
            return None
        else:
            return maxVoltageError

    def getMaxTorque(self):
        maxTorque, maxTorqueError = self.__dxlGetter(2, self.ADDR_MAX_TORQUE)
        if maxTorqueError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Maximum Torque:", maxTorque)
            return maxTorque
        else:
            return None

    def setMaxTorque(self, maxTorqueValue):
        maxTorqueError = self.__dxlSetter(2, self.ADDR_MAX_TORQUE, maxTorqueValue)
        if maxTorqueError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Maximum Torque set to", maxTorqueValue)
            sleep(0.25)
            return None
        else:
            return maxTorqueError

    def getStatusReturnLevel(self):
        statusReturnLevel, statusReturnLevelError = self.__dxlGetter(1, self.ADDR_STATUS_RETURN_LEVEL)
        if statusReturnLevelError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Status Return Level:", statusReturnLevel)
            return statusReturnLevel
        else:
            return None

    def setStatusReturnLevel(self, statusReturnLevelValue):
        statusReturnLevelError = self.__dxlSetter(1, self.ADDR_STATUS_RETURN_LEVEL, statusReturnLevelValue)
        if statusReturnLevelError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Status Return Level set to", statusReturnLevelValue)
            sleep(0.25)
            return None
        else:
            return statusReturnLevelError

    def getAlarmLED(self):
        alarmLED, alarmLEDError = self.__dxlGetter(1, self.ADDR_ALARM_LED)
        if alarmLEDError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Alarm LED:", alarmLED)
            return alarmLED
        else:
            return None

    def setAlarmLED(self, alarmLEDValue):
        alarmLEDError = self.__dxlSetter(1, self.ADDR_ALARM_LED, alarmLEDValue)
        if alarmLEDError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Alarm LED set to", alarmLEDValue)
            sleep(0.25)
            return None
        else:
            return alarmLEDError

    def getShutdown(self):
        shutdown, shutdownError = self.__dxlGetter(1, self.ADDR_SHUTDOWN)
        if shutdownError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Shutdown:", shutdown)
            return shutdown
        else:
            return None

    def setShutdown(self, shutdownValue):
        shutdownError = self.__dxlSetter(1, self.ADDR_SHUTDOWN, shutdownValue)
        if shutdownError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Shutdown set to", shutdownValue)
            sleep(0.25)
            return None
        else:
            return shutdownError

################################################################################
##########                          RAM Area                          ##########
################################################################################

    def getTorqueEnable(self):
        torqueEnable, torqueEnableError = self.__dxlGetter(1, self.ADDR_TORQUE_ENABLE)
        if torqueEnableError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Torque Enable:", torqueEnable)
            return torqueEnable
        else:
            return None

    def setTorqueEnable(self, torqueEnableValue):
        torqueEnableError = self.__dxlSetter(1, self.ADDR_TORQUE_ENABLE, torqueEnableValue)
        if torqueEnableError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Torque Enable set to", torqueEnableValue)
            return None
        else:
            return torqueEnableError

    def enableTorque(self):
        return self.setTorqueEnable(1)

    def disableTorque(self):
        return self.setTorqueEnable(0)

    def getLED(self):
        ledValue, ledValueError = self.__dxlGetter(1, self.ADDR_LED)
        if ledValueError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "LED value is:", ledValue)
            return ledValue
        else:
            return None

    def setLED(self, ledValueValue):
        ledValueError = self.__dxlSetter(1, self.ADDR_LED, ledValueValue)
        if ledValueError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "LED set to", ledValueValue)
            return None
        else:
            return ledValueError

    def getCwComplianceMargin(self):
        cwComplianceMargin, cwComplianceMarginError = self.__dxlGetter(1, self.ADDR_CW_COMPLIANCE_MARGIN)
        if cwComplianceMarginError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CW Compliance Margin:", cwComplianceMargin)
            return cwComplianceMargin
        else:
            return None

    def setCwComplianceMargin(self, cwComplianceMarginValue):
        cwComplianceMarginError = self.__dxlSetter(1, self.ADDR_CW_COMPLIANCE_MARGIN, cwComplianceMarginValue)
        if cwComplianceMarginError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "CW Compliance Margin set to", cwComplianceMarginValue)
            return None
        else:
            return cwComplianceMarginError

    def getCcwComplianceMargin(self):
        ccwComplianceMargin, ccwComplianceMarginError = self.__dxlGetter(1, self.ADDR_CCW_COMPLIANCE_MARGIN)
        if ccwComplianceMarginError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CCW Compliance Margin:", ccwComplianceMargin)
            return ccwComplianceMargin
        else:
            return None

    def setCcwComplianceMargin(self, ccwComplianceMarginValue):
        ccwComplianceMarginError = self.__dxlSetter(1, self.ADDR_CCW_COMPLIANCE_MARGIN, ccwComplianceMarginValue)
        if ccwComplianceMarginError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "CCW Compliance Margin set to", ccwComplianceMarginValue)
            return None
        else:
            return ccwComplianceMarginError

    def getCwComplianceSlope(self):
        cwComplianceSlope, cwComplianceSlopeError = self.__dxlGetter(1, self.ADDR_CW_COMPLIANCE_SLOPE)
        if cwComplianceSlopeError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CW Compliance Slope:", cwComplianceSlope)
            return cwComplianceSlope
        else:
            return None

    def setCwComplianceSlope(self, cwComplianceSlopeValue):
        cwComplianceSlopeError = self.__dxlSetter(1, self.ADDR_CW_COMPLIANCE_SLOPE, cwComplianceSlopeValue)
        if cwComplianceSlopeError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "CW Compliance Slope set to", cwComplianceSlopeValue)
            return None
        else:
            return cwComplianceSlopeError

    def getCcwComplianceSlope(self):
        ccwComplianceSlope, ccwComplianceSlopeError = self.__dxlGetter(1, self.ADDR_CCW_COMPLIANCE_SLOPE)
        if ccwComplianceSlopeError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "CCW Compliance Slope:", ccwComplianceSlope)
            return ccwComplianceSlope
        else:
            return None

    def setCcwComplianceSlope(self, ccwComplianceSlopeValue):
        ccwComplianceSlopeError = self.__dxlSetter(1, self.ADDR_CCW_COMPLIANCE_SLOPE, ccwComplianceSlopeValue)
        if ccwComplianceSlopeError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "CCW Compliance Slope set to", ccwComplianceSlopeValue)
            return None
        else:
            return ccwComplianceSlopeError

    def getGoalPosition(self):
        goalPosition, goalPositionError = self.__dxlGetter(2, self.ADDR_GOAL_POSITION)
        if goalPositionError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Goal Position:", goalPosition)
            return goalPosition
        else:
            return None

    def setGoalPosition(self, goalPositionValue):
        # New goal position has to be between the angle limits.
        if goalPositionValue <= self.ccwAngleLimit and goalPositionValue >= self.cwAngleLimit:
            goalPositionError = self.__dxlSetter(2, self.ADDR_GOAL_POSITION, goalPositionValue)
            if goalPositionError == 0:
                if self.printInfo: print("[WRITE] ID:", self.id, "Goal Position set to", goalPositionValue)
                return None
            else:
                return goalPositionError
        else:
            errorString = "[ERROR] ID: " + str(self.id) + " Cannot set Goal Position " + str(goalPositionValue) + ". It is outside of Angle Limit " + str(self.cwAngleLimit) + " to " + str(self.ccwAngleLimit)
            if self.printInfo: print(errorString)
            return errorString

    def getMovingSpeed(self):
        # NOTE: This is goal speed.  For actual speed, use getPresentSpeed()
        # This returns an 11-bit value; if greater than 1023, it needs to be moved.
        # See setMovingSpeed() for more detail.
        movingSpeed, movingSpeedError = self.__dxlGetter(2, self.ADDR_MOVING_SPEED)
        if movingSpeed >=0 and movingSpeed < 1024: adjMovingSpeed = movingSpeed
        elif movingSpeed < 2048: adjMovingSpeed = -(movingSpeed - 1024)
        else:
            adjMovingSpeed = None
            if self.printInfo:
                print("[ERROR] ID:", self.id, "getMovingSpeed found value out of range:", movingSpeed)
        if movingSpeedError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Goal Moving Speed:", adjMovingSpeed)
            return adjMovingSpeed
        else:
            return None

    def setMovingSpeed(self, movingSpeed):
        # The Dynamixel stores speed as follows:
        # There are 2 bytes/16 bits available.  It uses only 10 or 11 of them.
        # The first 10 bits provide the absolute value of the speed.
        # This 10-bit integer is what is used in Joint Mode, the 11th bit is ignored.
        # Notice that, in Joint Mode, speed does not determine direction; the
        # location of the goal position determines direction.
        # The 11th bit determines direction in Wheel Mode -- 0=CCW and 1=CW.
        # So this function is set up thinking of it as an 11-bit signed integer:
        # The first ten bits are the numerical value, the 11th bit is the sign,
        # where 0=+/CCW, 1=-/CW.
        # But to write those values we need to move the input values from -1 to -1023
        # to values for writing to Dynamixel from 1025 to 2047. So we negate and add to 1024.
        # Notice eManual is incorrect: 0 & 1024 both mean stop.  The manual says 0 = full power.
        if movingSpeed > 1023 or movingSpeed < -1023:
            errorString = "[Error] ID: " + str(self.id) + " setMovingSpeed should be between -1023 and 1023, received: " + str(movingSpeed)
            if self.printInfo: print(errorString)
            return errorString
        if movingSpeed < 0: # CW movement in wheel mode
            adjMovingSpeed = 1024 + -movingSpeed
        else:
            adjMovingSpeed = movingSpeed
        movingSpeedError = self.__dxlSetter(2, self.ADDR_MOVING_SPEED, adjMovingSpeed)
        if movingSpeedError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Goal Moving Speed set to", movingSpeed)
            return None
        else:
            return movingSpeedError

    def getTorqueLimit(self):
        torqueLimit, torqueLimitError = self.__dxlGetter(2, self.ADDR_TORQUE_LIMIT)
        if torqueLimitError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Torque Limit:", torqueLimit)
            return torqueLimit
        else:
            return None

    def setTorqueLimit(self, torqueLimitValue):
        torqueLimitError = self.__dxlSetter(2, self.ADDR_TORQUE_LIMIT, torqueLimitValue)
        if torqueLimitError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Torque Limit set to", torqueLimitValue)
            return None
        else:
            return torqueLimitError

    def getPresentPosition(self):
        presentPosition, presentPositionError = self.__dxlGetter(2, self.ADDR_PRESENT_POSITION)
        if presentPositionError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Present Position:", presentPosition)
            return presentPosition
        else:
            return None

    def getPresentSpeed(self):
        # NOTE: This is actual speed, for goal speed, use getMovingSpeed()
        # Need to adjust for 11th bit (see setMovingSpeed()).
        presentSpeed, presentSpeedError = self.__dxlGetter(2, self.ADDR_PRESENT_SPEED)
        if presentSpeedError == 0:
            if presentSpeed > 1023:
                presentSpeed = -(presentSpeed - 1024)
            if self.printInfo: print("[READ] ID:", self.id, "Present Speed:", presentSpeed)
            return presentSpeed
        else:
            return None

    def getPresentLoad(self):
        presentLoad, presentLoadError = self.__dxlGetter(2, self.ADDR_PRESENT_LOAD)
        if presentLoadError == 0:
            if presentLoad > 1023:
                presentLoad = -(presentLoad - 1024)
            if self.printInfo: print("[READ] ID:", self.id, "Present Load:", presentLoad)
            return presentLoad
        else:
            return None

    def getPresentVoltage(self):
        presentVoltage, presentVoltageError = self.__dxlGetter(1, self.ADDR_PRESENT_VOLTAGE)
        if presentVoltageError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Present Voltage:", presentVoltage)
            return presentVoltage
        else:
            return None

    def getPresentTemperature(self):
        presentTemperature, presentTemperatureError = self.__dxlGetter(1, self.ADDR_PRESENT_TEMPERATURE)
        if presentTemperatureError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Present Temperature:", presentTemperature)
            return presentTemperature
        else:
            return None

    def getRegistered(self):
        registered, registeredError = self.__dxlGetter(1, self.ADDR_REGISTERED)
        if registeredError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Registered:", registered)
            return registered
        else:
            return None

    def getMoving(self):
        moving, movingError = self.__dxlGetter(1, self.ADDR_MOVING)
        if movingError == 0:
            # moving=1 only indicates that a setGoalPosition has not completed yet
            # so we also check if actual speed is zero as well.
            if moving == 0:
                if self.getPresentSpeed() != 0: moving = 1
            if self.printInfo: print("[READ] ID:", self.id, "Moving:", moving)
            return moving
        else:
            return None

    def getLock(self):
        lock, lockError = self.__dxlGetter(1, self.ADDR_LOCK)
        if lockError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Lock:", lock)
            return lock
        else:
            return None

    def setLock(self, lockValue):
        # Note: Setting Lock=True will prevent ALL write requests, including request to set Lock=False
        # until powered down and restarted.
        lockError = self.__dxlSetter(1, self.ADDR_LOCK, lockValue)
        if lockError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Lock set to", lockValue)
            return None
        else:
            return lockError

    def getPunch(self):
        punch, punchError = self.__dxlGetter(2, self.ADDR_PUNCH)
        if punchError == 0:
            if self.printInfo: print("[READ] ID:", self.id, "Punch:", punch)
            return punch
        else:
            return None

    def setPunch(self, punchValue):
        punchError = self.__dxlSetter(2, self.ADDR_PUNCH, punchValue)
        if punchError == 0:
            if self.printInfo: print("[WRITE] ID:", self.id, "Punch set to", punchValue)
            return None
        else:
            return punchError

    def connect(self):
        if not self.connected:
            # Set connected to True, reset back to False if an error occurs.
            self.connected = True

            # Initialize PortHandler instance, Set the port path
            # Get methods and members of PortHandlerLinux or PortHandlerWindows
            self.portHandler = PortHandler(self.devicePort)

            # Initialize PacketHandler instance
            # Set the protocol version
            # Get methods and members of Protocol1PacketHandler or Protocol2PacketHandler
            self.packetHandler = PacketHandler(self.PROTOCOL_VERSION)

            # Open port
            if self.portHandler.openPort():
                if self.printInfo: print("[INFO] ID:", self.id, self.devicePort, "port Opened for motor.")
            else:
                quit()

            # Set port baudrate
            if self.portHandler.setBaudRate(self.baudRate):
                if self.printInfo:
                    print("[INFO] ID:", self.id, "Set the baudrate of the port to", self.baudRate)
                    print("[INFO] ID:", self.id, "Attempting to connect to motor.")
            else:
                self.connected = False
                quit()

            # Attempt to write
            torqueEnableError = self.enableTorque()
            if torqueEnableError:
                if self.printInfo:
                    print("[ERROR] ID:", self.id, "Write attempt failed in AX-12A connect() method.")
                    self.connected = False
            else:
                if self.printInfo: print("[INFO] ID:", self.id, "Write attempt successful in AX-12A connect() method.")

            # Attempt to read
            if self.connected:
                presentPosition = self.getPresentPosition()
                if presentPosition is not None:
                    if self.printInfo: print("[INFO] ID:", self.id, "Read attempt successful in AX-12A connect() method.")
                else:
                    if self.printInfo: print("[ERROR] ID:", self.id, "Read attempt failed in AX-12A connect() method.")
                    self.connected = False
                    return

            # If both Angle Limits are zero, we're in wheel mode, otherwise, in joint mode.
            # If in Joint mode, check if Present Position is out of range.
            # If so, move to end of range.
            if self.connected:
                self.cwAngleLimit = self.getCwAngleLimit()
                self.ccwAngleLimit = self.getCcwAngleLimit()
                if self.cwAngleLimit != 0 or self.ccwAngleLimit != 0:
                    if self.cwAngleLimit > presentPosition:
                        if self.printInfo: print("[INFO] ID:", self.id, "Motor out of range. Move motor to minimum position.")
                        self.setGoalPosition(self.cwAngleLimit)
                    elif self.ccwAngleLimit < self.getPresentPosition():
                        if self.printInfo: print("[INFO] ID:", self.id, "Motor out of range. Move motor to maximum position.")
                        self.setGoalPosition(self.ccwAngleLimit)
        else:
            if self.printInfo: print("[INFO] ID:", self.id, "connect() called when motor already connected.")
            return

    @classmethod
    def listInstances(cls):
        return(cls.instances)

    @classmethod
    def connectAll(cls):
        motors = AX_12A.listInstances()
        for motor in motors:
            motor.connect()

    @classmethod
    def getAll(cls, method):
        """
        Runs the same .get...() method on all connected motors.
        Returns a list of all the values captured.
        """
        method = 'motor.' + method + '()'
        motors = AX_12A.listInstances()
        gets = []
        for motor in motors:
            gets.append(eval(method))
        return gets

    @classmethod
    def setAll(cls, method, value):
        """
        Runs the same .set...(value) method on all connected motors.
        Returns a list of all the values captured (will be 'None' for every motor
            that executes without errors).
        """
        method = 'motor.' + method + '(' + str(value) + ')'
        motors = AX_12A.listInstances()
        setErrorResults = []
        for motor in motors:
            setErrorResults.append(eval(method))
        return setErrorResults

    @classmethod
    def setPose(cls, positions):
        """
        Inputs: List of integers, each a goal position of an AX_12A() instance.
            You can avoid setting a value for one or more motors by putting 'None'
                at each location in the list that you want to skip.
            Assumes that AX_12A() has a list of instances which can be retrieved via AX_12A.listInstances()
        Returns: None
        Purpose: Given a list of length n, will set the first n AX-12A motors, in order, to those positions.
            You do not need to use all motors, but you do need to give values all of the first n motors.
        """
        motors = AX_12A.listInstances()
        for index, position in enumerate(positions):
            if position != None:
                motors[index].setGoalPosition(position)
        return

    @classmethod
    def readPose(cls):
        motors = AX_12A.listInstances()
        motorPositions = []
        for motor in motors:
            if motor.connected:
                pos = motor.getPresentPosition()
                motorPositions.append(pos)
        return motorPositions

    @classmethod
    def waitForMotors(cls):
        # The localPrintInfo list stores the current state of self.printInfo for each motor.
        # This allows for temporarily silencing the output while checking for moving status.
        # All self.printInfo values are re-set to their prior values at the end.
        localPrintInfo = []
        motors = AX_12A.listInstances()
        for motor in motors:
            localPrintInfo.append(motor.printInfo)
            motor.printInfo = False
        moving = True
        while moving:
            moving = False
            for motor in motors:
                if motor.getMoving(): moving = True
        printInfoAny = False
        for index, motor in enumerate(motors):
            motor.printInfo = localPrintInfo[index]
            if localPrintInfo:
                printInfoAny = True
        if printInfoAny:
            print("[INFO] All motors have stopped moving.")
        return
