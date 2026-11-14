# QMI8658 6-axis IMU driver with any-motion detection.
#
# Based on the Waveshare RP2040-Touch-LCD-1.28 MicroPython demo code
# (https://www.waveshare.com/wiki/RP2040-Touch-LCD-1.28), (c) Waveshare.
# Modifications (c) 2025-2026 Marcel Rebmann, MIT License:
# motion-detection configuration, CTRL9 command timeout, chip ID check,
# signed 16-bit conversion fix.
# See THIRD_PARTY_NOTICES.md for details.

import utime
import log

# General Purpose Registers
WHO_AM_I=0x00 # Device Identifier
REVISION_ID=0x01 # Device Revision
QMI8658_CHIP_ID=0x05 # Expected WHO_AM_I value

# Setup and Control Registers
CTRL1=0x02 # SPI Interface and Sensor Enable
CTRL2=0x03 # Accelerometer: Output Data Rate, Full Scale, Self-Test
CTRL3=0x04 # Gyroscope: Output Data Rate, Full Scale, Self-Test
CTRL5=0x06 # Low pass filter setting
CTRL7=0x08 # Enable Sensors
CTRL8=0x09 # Motion Detection Control
CTRL9=0x0A # Host Commands

# Host Controlled Calibration Registers (See CTRL9, Usage is Optional)
CAL1_L=0x0B # CAL1_L – lower 8 bits.
CAL1_H=0x0C # CAL1_H – upper 8 bits.
CAL2_L=0x0D
CAL2_H=0x0E
CAL3_L=0x0F
CAL3_H=0x10
CAL4_L=0x11
CAL4_H=0x12

# Status Registers
STATUSINT = 0x2D # Sensor Data Availability with the Locking mechanism, CmdDone (CTRL9 protocol bit).
STATUS0 = 0x2E # Output Data Over Run and Data Availability
STATUS1 = 0x2F # Miscellaneous Status: Any Motion, No Motion, Significant Motion, Pedometer, Tap.


# CTRL9 Commands
CTRL_CMD_ACK= 0x00 # Ctrl9 Acknowledgement. Host acknowledges to QMI8658, to end the protocol.
CTRL_CMD_RST_FIFO = 0x04 # Ctrl9 Reset FIFO from Host
CTRL_CMD_REQ_FIFO = 0x05 # Ctrl9R Get FIFO data from Device
CTRL_CMD_WRITE_WOM_SETTING = 0x08 # WCtrl9 Set up and enable Wake on Motion (WoM)
CTRL_CMD_ACCEL_HOST_DELTA_OFFSET = 0x09 # WCtrl9 Change accelerometer offset
CTRL_CMD_GYRO_HOST_DELTA_OFFSET = 0x0A # WCtrl9 Change gyroscope offset
CTRL_CMD_CONFIGURE_TAP = 0x0C # WCtrl9 Configure Tap detection
CTRL_CMD_CONFIGURE_PEDOMETER = 0x0D # WCtrl9 Configure Pedometer
CTRL_CMD_CONFIGURE_MOTION = 0x0E # WCtrl9 Configure Any Motion / No Motion / Significant Motion detection
CTRL_CMD_RESET_PEDOMETER = 0x0F # WCtrl9 Reset pedometer count (step count)
CTRL_CMD_COPY_USID = 0x10 # Ctrl9R Copy USID and FW Version to UI registers
CTRL_CMD_SET_RPU = 0x11 # WCtrl9 Configures IO pull-ups
CTRL_CMD_AHB_CLOCK_GATING = 0x12 # WCtrl9 Internal AHB clock gating switch
CTRL_CMD_ON_DEMAND_CALIBRATION = 0xA2 # WCtrl9 On-Demand Calibration on gyroscope
CTRL_CMD_APPLY_GYRO_GAINS = 0xAA # WCtrl9 Restore the saved Gyroscope gains

class QMI8658(object):
    def __init__(self, i2c, address=0x6B):
        """i2c: a configured machine.I2C instance (shared with the touch controller)."""
        self._address = address
        self._bus = i2c
        chip_id = self._read_byte(WHO_AM_I)
        self.detected = chip_id == QMI8658_CHIP_ID
        if not self.detected:
            # Keep configuring anyway: skipping Config_apply() leaves motion detection unconfigured
            log.warn("unexpected QMI8658 ID 0x{:02X} (expected 0x{:02X})".format(chip_id, QMI8658_CHIP_ID))
        self.Read_Revision()
        self.Config_apply()

    def _read_byte(self,cmd):
        rec=self._bus.readfrom_mem(int(self._address),int(cmd),1)
        return rec[0]
    
    def _read_block(self, reg, length=1):
        rec=self._bus.readfrom_mem(int(self._address),int(reg),length)
        return rec
    
    def _read_u16(self,cmd):
        LSB = self._bus.readfrom_mem(int(self._address),int(cmd),1)
        MSB = self._bus.readfrom_mem(int(self._address),int(cmd)+1,1)
        return (MSB[0] << 8) + LSB[0]
    
    def _write_byte(self,cmd,val):
        self._bus.writeto_mem(int(self._address),int(cmd),bytes([int(val)]))
        
    def WhoAmI(self):
        bRet=False
        if QMI8658_CHIP_ID == self._read_byte(WHO_AM_I):
            bRet = True
        return bRet
    
    def Read_Revision(self):
        return self._read_byte(0x01)
    
    def Config_apply(self):
        # REG CTRL1
        self._write_byte(CTRL1, 0x60)
        # REG CTRL2 : QMI8658AccRange_8g  and QMI8658AccOdr_1000Hz
        self._write_byte(CTRL2, 0x23)
        # REG CTRL3 : QMI8658GyrRange_512dps and QMI8658GyrOdr_1000Hz
        self._write_byte(CTRL3, 0x53)
        # REG CTRL4 : No
        self._write_byte(0x05,0x00)
        # REG CTRL5 : Enable Gyroscope And Accelerometer Low-Pass Filter 
        self._write_byte(CTRL5, 0x11)
        # REG CTRL6 : Disables Motion on Demand.
        self._write_byte(0x07,0x00)
        # REG CTRL7 : Enable Gyroscope And Accelerometer
        # self._write_byte(CTRL7,0x03)
        self._write_byte(CTRL7,0b00000000)

    def Read_Raw_XYZ(self):
        xyz=[0,0,0,0,0,0]
        raw_timestamp = self._read_block(0x30,3)
        raw_acc_xyz=self._read_block(0x35,6)
        raw_gyro_xyz=self._read_block(0x3b,6)
        raw_xyz=self._read_block(0x35,12)
        timestamp = (raw_timestamp[2]<<16)|(raw_timestamp[1]<<8)|(raw_timestamp[0])
        for i in range(6):
            # xyz[i]=(raw_acc_xyz[(i*2)+1]<<8)|(raw_acc_xyz[i*2])
            # xyz[i+3]=(raw_gyro_xyz[((i+3)*2)+1]<<8)|(raw_gyro_xyz[(i+3)*2])
            xyz[i] = (raw_xyz[(i*2)+1]<<8)|(raw_xyz[i*2])
            if xyz[i] > 32767:
                xyz[i] = xyz[i]-65536
        return xyz
    
    def Read_XYZ(self):
        xyz=[0,0,0,0,0,0]
        raw_xyz=self.Read_Raw_XYZ()  
        #QMI8658AccRange_8g
        acc_lsb_div=(1<<12)
        #QMI8658GyrRange_512dps
        gyro_lsb_div = 64
        for i in range(3):
            xyz[i]=raw_xyz[i]/acc_lsb_div#(acc_lsb_div/1000.0)
            xyz[i+3]=raw_xyz[i+3]*1.0/gyro_lsb_div
        return xyz
    

    def write_ctrl9_command(self,cmd):
        self._write_byte(CTRL9,cmd)

    def _wait_cmd_done(self, timeout_ms=1000):
        # STATUSINT bit 7 = CmdDone (CTRL9 protocol)
        start = utime.ticks_ms()
        while self._read_byte(STATUSINT) & 0b10000000 == 0:
            if utime.ticks_diff(utime.ticks_ms(), start) > timeout_ms:
                log.warn("QMI8658 CTRL9 command timed out")
                return False
            utime.sleep_ms(10)
        log.debug("QMI8658: confirmation received")
        return True

    def configure_motion_detection(self, threshold_g=0.25, window_samples=10):
        """Enable any-motion detection.

        threshold_g: acceleration per axis that counts as motion (0.03 - 7.9 g).
        window_samples: consecutive samples above the threshold before motion is reported.
        """
        # Threshold registers use the U3.5 format: value = g * 32
        threshold = max(1, min(255, round(threshold_g * 32)))
        window = max(1, min(255, int(window_samples)))

        self._write_byte(CAL1_L,threshold)  # AnyMotionXThreshold
        self._write_byte(CAL1_H,threshold)  # AnyMotionYThreshold
        self._write_byte(CAL2_L,threshold)  # AnyMotionZThreshold
        self._write_byte(CAL2_H,0b00000000) # NoMotionXThreshold
        self._write_byte(CAL3_L,0b00000000) # NoMotionYThreshold
        self._write_byte(CAL3_H,0b00000000) # NoMotionZThreshold
        self._write_byte(CAL4_L,0b00000111) # MOTION_MODE_CTRL
        self._write_byte(CAL4_H,0x01)# first set of params
        self.write_ctrl9_command(CTRL_CMD_CONFIGURE_MOTION)
        log.debug("Configuring motion detection: part 1 sent, waiting for confirmation...")

        # Wait for the command to be processed
        self._wait_cmd_done()

        # Acknowledge the command
        self.write_ctrl9_command(CTRL_CMD_ACK)
        log.debug("QMI8658: acknowledged")
        utime.sleep_ms(10)

        self._write_byte(CAL1_L,window)  # AnyMotionWindow: consecutive samples above threshold
        self._write_byte(CAL1_H,0b00100000) # NoMotionWindow
        self._write_byte(CAL2_L,0b00100000) # SigMotionWaitWindow[7:0]
        self._write_byte(CAL2_H,0b00100000) # SigMotionWaitWindow [15:8]
        self._write_byte(CAL3_L,0b00100000) # SigMotionConfirmWindow[7:0]
        self._write_byte(CAL3_H,0b00100000) # SigMotionConfirmWindow[15:8]
        # self._write_byte(CAL4_L,0x00000111) # MOTION_MODE_CTRL
        self._write_byte(CAL4_H,0x02)# second set of params
        self.write_ctrl9_command(CTRL_CMD_CONFIGURE_MOTION)
        log.debug("Configuring motion detection: part 2 sent, waiting for confirmation...")

        # Wait for the command to be processed
        self._wait_cmd_done()

        # Acknowledge the command
        self.write_ctrl9_command(CTRL_CMD_ACK)
        log.debug("QMI8658: acknowledged")
        utime.sleep_ms(10)

        # Enable Motion Detection. Event on INT1
        self._write_byte(CTRL8,0b01000110)
        # Enable Accelerometer and Gyroscope
        self._write_byte(CTRL7,0b00000011)

    def is_any_motion_detected(self):
        bit_5_mask = 0b00100000
        readout = self._read_byte(STATUS1)
        return readout & bit_5_mask != 0
        