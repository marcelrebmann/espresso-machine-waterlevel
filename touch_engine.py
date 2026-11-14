# CST816T / CST816G capacitive touch controller driver.
#
# Based on the Waveshare RP2040-Touch-LCD-1.28 MicroPython demo code
# (https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.28), (c) Waveshare.
# Modifications (c) 2025-2026 Marcel Rebmann, MIT License:
# CST816G detection, graceful fallback when no chip is found,
# I2C error handling.
# See THIRD_PARTY_NOTICES.md for details.

from machine import Pin, Timer
import time
import log

# Registers
REG_GESTURE_ID=0x01

# Gesture IDs
GESTURE_ID_NO_GESTURE = 0x00
GESTURE_ID_SLIDE_UP = 0x01
GESTURE_ID_SLIDE_DOWN = 0x02
GESTURE_ID_SLIDE_LEFT = 0x03
GESTURE_ID_SLIDE_RIGHT = 0x04
GESTURE_ID_SINGLE_CLICK = 0x05
GESTURE_ID_DOUBLE_CLICK = 0x0B
GESTURE_ID_LONG_PRESS = 0x0C


#Touch drive
class Touch_CST816T(object):
    #Initialize the touch chip
    def __init__(self, i2c, int_pin=21, rst_pin=22, address=0x15, mode=0):
        """i2c: a configured machine.I2C instance (shared with the IMU)."""
        self._bus = i2c
        self._address = address #Set slave address 
        self.int=Pin(int_pin,Pin.IN, Pin.PULL_UP)     
        self.tim = Timer()     
        self.rst=Pin(rst_pin,Pin.OUT)
        self.Reset()
        self.detected = self.WhoAmI()
        if self.detected:
            chip_name = "CST816G" if self._read_byte(0xA7) == 0xB3 else "CST816T"
            log.debug("Detected touch controller {} (revision {})".format(chip_name, self.Read_Revision()))
            self.Stop_Sleep()
            self.Mode = mode
            self.Gestures=None
            self.last_gesture=None
            self.Flag = self.Flgh =self.l = 0
            self.X_point = self.Y_point = 0
            self.int.irq(handler=self.Int_Callback,trigger=Pin.IRQ_FALLING)
        else    :
            log.warn("touch controller not detected (expected chip ID 0xB3/0xB5)")
      
    def _read_byte(self,cmd):
        try:
            rec = self._bus.readfrom_mem(int(self._address), int(cmd), 1)
            return rec[0]
        except OSError:
            return -1

    def _read_block(self, reg, length=1):
        try:
            rec = self._bus.readfrom_mem(int(self._address), int(reg), length)
            return rec
        except OSError:
            return bytes([0] * length)

    def _write_byte(self,cmd,val):
        try:
            self._bus.writeto_mem(int(self._address), int(cmd), bytes([int(val)]))
        except OSError:
            pass

    def WhoAmI(self):
        chip_id = self._read_byte(0xA7)
        # Accept both CST816G (0xB3, WaveShare board) and CST816T (0xB5)
        return chip_id in (0xB3, 0xB5)
    
    def Read_Revision(self):
        return self._read_byte(0xA9)
      
    #Stop sleeping 
    def Stop_Sleep(self):
        self._write_byte(0xFE,0x01)
    
    #Reset    
    def Reset(self):
        self.rst(0)
        time.sleep_ms(1)
        self.rst(1)
        time.sleep_ms(50)
    
    #Set mode   
    def Set_Mode(self,mode,callback_time=10,rest_time=5): 
        # mode = 0 gestures mode 
        # mode = 1 point mode 
        # mode = 2 mixed mode 
        if (mode == 1):      
            self._write_byte(0xFA,0X41)
            
        elif (mode == 2) :
            self._write_byte(0xFA,0X71)
            
        else:
            self._write_byte(0xFA,0X11)
            self._write_byte(0xEC,0X01)
     
    #Get the coordinates of the touch
    def get_point(self):
        xy_point = self._read_block(0x03,4)
        
        x_point= ((xy_point[0]&0x0f)<<8)+xy_point[1]
        y_point= ((xy_point[2]&0x0f)<<8)+xy_point[3]
        
        self.X_point=x_point
        self.Y_point=y_point
        
    def Int_Callback(self,pin):
        if self.Mode == 0 :
            gestures = self._read_byte(REG_GESTURE_ID)
            self.Gestures = gestures
            if gestures != GESTURE_ID_NO_GESTURE and self.last_gesture == None:
                self.last_gesture = gestures

        elif self.Mode == 1:           
            self.Flag = 1
            self.get_point()

    def Timer_callback(self,t):
        self.l += 1
        if self.l > 100:
            self.l = 50

    def is_touch_detected(self):
        # bit_5_mask = 0b00100000
        gesture = self.last_gesture
        self.last_gesture = None
        return gesture == GESTURE_ID_SINGLE_CLICK

