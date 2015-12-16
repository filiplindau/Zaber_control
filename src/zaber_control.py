'''
Created on 10 Dec 2015

@author: Filip Lindau
'''

import serial
import struct

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
        
    def connect(self):
        if self.device != None:
            self.close()
        try:
            self.device = serial.Serial(self.port, 9600, timeout = 0.2, parity = serial.PARITY_NONE, bytesize = 8, stopbits = serial.STOPBITS_ONE)
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
                raise ValueError(''.join(('Error sending command ', str(repCmd.command), ', code ', str(data))))
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
        cmd = MotorCommand(20, pos, motor)
        pos = self.sendReceive(cmd)
        if pos == None:
            return None
        else:
            return pos.data
    
    def setPositionRelative(self, relPos, motor = 0):
        cmd = MotorCommand(21, relPos, motor)
        pos = self.sendReceive(cmd)
        if pos == None:
            return None
        else:
            return pos.data
        
    def setTargetSpeed(self, speed, motor = 0):
        cmd = MotorCommand(42, speed, motor)
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
        cmd = MotorCommand(43, data, motor)
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
        cmd = MotorCommand(45, data, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def setMicrostepResolution(self, data, motor = 0):
        cmd = MotorCommand(37, data, motor)
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
        
    def stop(self, data, motor = 0):
        ''' Stops motor and returns final postition
        '''
        cmd = MotorCommand(23, data, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return out.data
    
    def setRunningCurrent(self, data, motor = 0):
        cmd = MotorCommand(38, data, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return 10.0/out.data
    
    def getRunningCurrent(self, motor = 0):
        cmd = MotorCommand(53, 38, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return 10.0/out.data
        
    def setHoldCurrent(self, data, motor = 0):
        cmd = MotorCommand(39, data, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return 10.0/out.data
    
    def getHoldCurrent(self, motor = 0):
        cmd = MotorCommand(53, 39, motor)
        out = self.sendReceive(cmd)
        if out == None:
            return None
        else:
            return 10.0/out.data
        
    def getStatus(self, motor = 0):
        cmd = MotorCommand(54, 0, motor)
        out = self.sendReceive(cmd)
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
            status = None
        return status

if __name__ == '__main__':
    m = ZaberControl('com4')