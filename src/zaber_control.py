'''
Created on 10 Dec 2015

@author: Filip Lindau
'''

import serial
import struct
import time

class MotorCommand(object):
    def __init__(self, command, data, motor = 0):
        self.command = command
        self.data = data
        self.motor = motor
        self.cmd = struct.pack('<2Bi', motor, command, data)

class ZaberControl(object):
    def __init__(self, port):
        self.port = port
        self.device = None
        
        self.errorDict = {1: ['Cannot home', 'Home - Device has traveled a long distance without triggering the home sensor. Device may be stalling or slipping.'],
                     2: ['Device number invalid', 'Renumbering data out of range.'],
                     14: ['Voltage low', 'Power supply data too low.'],
                     15: ['Voltage high', 'Power supply data too high.'],
                     18: ['Stored position invalid', 'The position stored in the requested register is no longer valid. This is probably because the maximum range was reduced.'],
                     20: ['Absolute position invalid', 'Move Absolute - Target position out of range.'],
                     21: ['Relative position invalid', 'Move Relative - Target position out of range.'],
                     22: ['Velocity invalid', 'Constant velocity move. Velocity out of range.'],
                     36: ['Peripheral ID invalid', 'Restore Settings - peripheral id is invalid. Please use one of the peripheral ids listed in the user manual, or 0 for default.'],
                     37: ['Resolution invalid', 'Invalid microstep resolution. Resolution may only be 1, 2, 4, 8, 16, 32, 64, 128.'],
                     38: ['Run current invalid', 'Run current out of range. See command 38 for allowable values.'],
                     39: ['Hold current invalid', 'Hold current out of range. See command 39 for allowable values.'],
                     40: ['Mode invalid', 'Set Device Mode - one or more of the mode bits is invalid'],
                     41: ['Home speed invalid', 'Home speed out of range. The range of home speed is determined by the resolution.'],
                     42: ['Speed invalid', 'Target speed out of range. The range of target speed is determined by the resolution.'],
                     43: ['Acceleration invalid', 'Target acceleration out of range. The range of target acceleration is determined by the resolution'],
                     44: ['Maximum range invalid', 'The maximum range may only be set between 1 and the resolution limit of the stepper controller, which is 16,777,215.'],
                     45: ['Current position invalid', 'Current position out of range. Current position must be between 0 and the maximum range.'],
                     46: ['Maximum relative move invalid', 'Max relative move out of range. Must be between 0 and 16,777,215.'],
                     47: ['Offset invalid', 'Home offset out of range. Home offset must be between 0 and maximum range.'],
                     48: ['Alias invalid', 'Alias out of range.'],
                     49: ['Lock state invalid', 'Lock state must be 1 (locked) or 0 (unlocked).'],
                     53: ['Setting invalid', 'Return Setting - data entered is not a valid setting command number. Valid setting command numbers are the command numbers of any "Set ..." instructions.'],
                     64: ['Command invalid', 'Command number not valid in this firmware version.'],
                     255: ['Busy', 'Another command is executing and cannot be pre-empted. Either stop the previous command or wait until it finishes before trying again.'],
                     1600: ['Save position invalid', 'Save Current Position register out of range (must be 0-15).'],
                     1601: ['Save position not homed', 'Save Current Position is not allowed unless the device has been homed.'],
                     1700: ['Return position invalid', 'Return Stored Position register out of range (must be 0-15).'],
                     1800: ['Move position invalid', 'Move to Stored Position register out of range (must be 0-15).'],
                     1801: ['Move position not homed', 'Move to Stored Position is not allowed unless the device has been homed.'],
                     2146: ['Relative position limited', 'Move Relative (command 20) exceeded maximum relative move range. Either move a shorter distance, or change the maximum relative move (command 46).'],
                     3600: ['Settings locked', 'Must clear Lock State (command 49) first. See the Set Lock State command for details.'],
                     4008: ['Disable auto home invalid', 'Set Device Mode - this is a linear actuator; Disable Auto Home is used for rotary actuators only.'],
                     4010: ['Bit 10 invalid', 'Set Device Mode - bit 10 is reserved and must be 0.'],
                     4012: ['Home switch invalid', 'Set Device Mode - this device has integrated home sensor with preset polarity; mode bit 12 cannot be changed by the user.'],
                     4013: ['Bit 13 invalid', 'Set Device Mode - bit 13 is reserved and must be 0.']
                     }
        
    def connect(self, port = None):
        if port != None:
            self.port = port
        if self.device != None:
            self.close()
        try:
            self.device = serial.Serial(self.port, 9600, timeout = 0.5, parity = serial.PARITY_NONE, bytesize = 8, stopbits = serial.STOPBITS_ONE)
        except Exception, e:
            self.device =  None
            raise e
        
    
    def close(self):
        if self.device != None:
            try:
                self.device.close()
                self.device = None
            except Exception, e:
                self.device = None
                raise e
        
    
    def sendCommand(self, cmd):
        if self.device == None:
            self.connect()
        
        try:
            self.device.write(cmd.cmd)
        except serial.SerialException, e:
            print 'Error in sendCommand: cmd = ', cmd.cmd, ' error ', e
            self.device = None
        except Exception, e:
            print e
    
    def receiveData(self):
        try:
            reply = self.device.read(6)
        except serial.SerialException, e:
            print 'Serial Error in receiveData: reply = ', reply, ' error ', e
            self.device = None
        except Exception, e:
            repCmd = MotorCommand(255, 255, 0)
            print 'Error in receiveData: reply = ', repr(reply), ' error ', e
        if reply.__len__() == 6:
            motorId, motorCommand, data = struct.unpack('<2Bi', reply)
            repCmd = MotorCommand(motorCommand, data, motorId)
            if motorCommand == 255:
                errorMsg = self.errorDict[data]
                raise ValueError(''.join((errorMsg[0], ': ', errorMsg[1])))
        else:
            repCmd = None
        return repCmd
            
    def sendReceive(self, cmd):
        self.sendCommand(cmd)
        return self.receiveData()
            
#### Command list:
    def resetMotor(self, motor = 0):
        cmd = MotorCommand(0, 0, motor)
        self.sendReceive(cmd)
        
    def homeMotor(self, motor = 0):
        cmd = MotorCommand(1, 0, motor)
        self.sendReceive(cmd)
        
    def getDeviceId(self, motor = 0):
        cmd = MotorCommand(50, 0, motor)
        devId = self.sendReceive(cmd)
        return devId.data

    def getFirmwareVersion(self, motor = 0):
        cmd = MotorCommand(51, 0, motor)
        fw = self.sendReceive(cmd)
        return fw.data
    
    def getPosition(self, motor = 0):
        cmd = MotorCommand(60, 0, motor)
        pos = self.sendReceive(cmd)
        if pos == None:
            return None
        else:
            return pos.data
    
    def setPositionAbsolute(self, pos, motor = 0):
        cmd = MotorCommand(20, int(pos), motor)
        pos = self.sendReceive(cmd)
        if pos == None:
            return None
        else:
            return pos.data
    
    def setPositionRelative(self, relPos, motor = 0):
        cmd = MotorCommand(21, int(relPos), motor)
        pos = self.sendReceive(cmd)
        if pos == None:
            return None
        else:
            return pos.data
        
    def setTargetSpeed(self, speed, motor = 0):
        cmd = MotorCommand(42, int(speed), motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def getTargetSpeed(self, motor = 0):
        cmd = MotorCommand(53, 42, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
        
    def setAcceleration(self, data, motor = 0):
        cmd = MotorCommand(43, int(data), motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def getAcceleration(self, motor = 0):
        cmd = MotorCommand(53, 43, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
        
    def setCurrentPosition(self, data, motor = 0):
        cmd = MotorCommand(45, int(data), motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def setMicrostepResolution(self, data, motor = 0):
        cmd = MotorCommand(37, int(data), motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def getMicrostepResolution(self, motor = 0):
        cmd = MotorCommand(53, 37, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
        
    def stop(self, motor = 0):
        ''' Stops motor and returns final postition
        '''
        cmd = MotorCommand(23, 0, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def setRunningCurrent(self, data, motor = 0):
        if data > 10.0/127:
            d = int(10.0/data)
        else:
            d = 0
        cmd = MotorCommand(38, d, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            if out.data == 0:
                return 0
            else:
                return 10.0/out.data

    def setRunningCurrent2(self, data, motor = 0):
        print "apa"
        print "set running current ", data
        cmd = MotorCommand(38, data, motor)
        out = self.sendReceive(cmd)
        print "current set"
        print out.data
    
    def getRunningCurrent(self, motor = 0):
        cmd = MotorCommand(53, 38, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            if out.data == 0:
                return 0
            else:
                return 10.0/out.data
        
    def setHoldCurrent(self, data, motor = 0):
        if data > 10.0/127:
            d = int(10.0/data)
        else:
            d = 0
        cmd = MotorCommand(39, d, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            if out.data == 0:
                return 0
            else:
                return 10.0/out.data
    
    def getHoldCurrent(self, motor = 0):
        cmd = MotorCommand(53, 39, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            if out.data == 0:
                return 0
            else:
                return 10.0/out.data
        
    def getStatus(self, motor = 0):
        cmd = MotorCommand(54, 0, motor)
        out = self.sendReceive(cmd)
        status = (None, None)
        if out != None:
            if out.data == 0:
                status = (0, 'idle')
            elif out.data == 1:
                status = (1, 'homing')
            elif out.data == 10:
                status = (10, 'manual move')
            elif out.data == 18:
                status = (18, 'move to stored pos')
            elif out.data == 20:
                status = (20, 'absolute move')
            elif out.data == 21:
                status = (21, 'relative move')
            elif out.data == 22:
                status = (22, 'constant move')
            elif out.data == 23:
                status = (23, 'stop')
            else:
                print out.data
                self.receiveData()
        return status

if __name__ == '__main__':
    m = ZaberControl('com4')
    m.setPositionAbsolute(1e5)
    stat = m.getStatus()
    while stat[0] != 0:
        print 'Pos: ', m.getPosition()
        stat = m.getStatus()
        print 'Status: ', stat
        print 'Pos: ', m.getPosition()
        time.sleep(0.1)