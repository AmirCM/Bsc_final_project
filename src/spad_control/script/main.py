#!/usr/bin/env python

import sys, tty, termios
fd = sys.stdin.fileno()
old_settings = termios.tcgetattr(fd)
def getch():
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch
        
from dynamixel_sdk import *




# Control table address
ADDR_MX_TORQUE_ENABLE = 24
ADDR_MX_GOAL_POSITION = 30
ADDR_MX_PRESENT_POSITION = 36

PROTOCOL_VERSION = 1.0

DXL_ID = 1

TORQUE_ENABLE = 1
TORQUE_DISABLE = 0
DXL_MINIMUM_POSITION_VALUE = 0
DXL_MAXIMUM_POSITION_VALUE = 4095
DXL_MOVING_STATUS_THRESHOLD = 20

# Data Byte Length
LEN_MX_GOAL_POSITION = 4
LEN_MX_PRESENT_POSITION = 4

index = 0
dxl_goal_position = [[1149, 1700, 1404, 1937],
                     [2189, 1700, 1698, 3004],
                     [1264, 1800, 1420, 2421],
                     [1264, 2000, 1420, 2421],
                     [3200, 1100, 1400, 3200]]


packetHandler = PacketHandler(PROTOCOL_VERSION)
BAUDRATE = 1000000
DEVICENAME = '/dev/ttyUSB1'

portHandler = PortHandler(DEVICENAME)


def serialInitialize():
    global portHandler
    if portHandler.openPort():
        print("Succeeded to open the port")
    else:
        print("Failed to open the port")
        print("Press any key to terminate...")
        getch()
        quit()

    if portHandler.setBaudRate(BAUDRATE):
        print("Succeeded to change the baudrate")
    else:
        print("Failed to change the baudrate")
        print("Press any key to terminate...")
        getch()
        quit()
    pass


def setPGain(ID, kp):
    global portHandler
    comm_result, error = packetHandler.write1ByteTxRx(portHandler, ID, 28, kp)
    if comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(comm_result))
    elif error != 0:
        print("%s" % packetHandler.getRxPacketError(error))


def gotoPos(ID, pos):
    global portHandler
    comm_result, error = packetHandler.write2ByteTxRx(portHandler, ID, ADDR_MX_GOAL_POSITION,
                                                      pos)
    if comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(comm_result))
    elif error != 0:
        print("%s" % packetHandler.getRxPacketError(error))


def readPos(ID):
    global portHandler
    present_position, comm_result, error = packetHandler.read2ByteTxRx(portHandler, ID,
                                                                       ADDR_MX_PRESENT_POSITION)
    if comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(comm_result))
    elif error != 0:
        print("%s" % packetHandler.getRxPacketError(error))

    return present_position


def setSpeed(ID, speed):
    global portHandler
    comm_result, error = packetHandler.write2ByteTxRx(portHandler, ID, 32, speed)
    if comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(comm_result))
    elif error != 0:
        print("%s" % packetHandler.getRxPacketError(error))


def torqueEnable(ID, state):
    if state:
        comm_result, error = packetHandler.write1ByteTxRx(portHandler, ID, ADDR_MX_TORQUE_ENABLE, TORQUE_ENABLE)
        print("Enable")
    else:
        comm_result, error = packetHandler.write1ByteTxRx(portHandler, ID, ADDR_MX_TORQUE_ENABLE, TORQUE_DISABLE)
        print("Disable")

    if comm_result != COMM_SUCCESS:
        print("%s" % packetHandler.getTxRxResult(comm_result))
    elif error != 0:
        print("%s" % packetHandler.getRxPacketError(error))
    else:
        if state:
            print(f"Dynamixel {ID} has been successfully connected")
        else:
            print(f"Dynamixel {ID} has been successfully disconnected")


if __name__ == "__main__":

    serialInitialize()

    setPGain(1, 8)  # 3138, 1104
    setPGain(2, 8)  # 1354, 2803
    setPGain(3, 8)  # 3306, 1225
    setPGain(4, 8)  # 1095, 3520

    setSpeed(1, 300)
    setSpeed(2, 90)
    setSpeed(3, 90)
    setSpeed(4, 90)

    print("Choose for M or R")
    if getch() == 'm':
        while 1:
            pos = [0, 0, 0, 0]
            pos[0] = readPos(1)
            pos[1] = readPos(2)
            pos[2] = readPos(3)
            pos[3] = readPos(4)
            print(f"S1: {pos[0]}, S2: {pos[1]}, S3: {pos[2]}, S4: {pos[3]} press ESC to exit")

    torqueEnable(1, True)
    torqueEnable(2, True)
    torqueEnable(3, True)
    torqueEnable(4, True)
    while 1:
        print("Press any key to continue! (or press ESC to quit!)")
        if getch() == chr(0x1b):
            break

        # Write goal position
        for i in range(4):
            gotoPos(i + 1, dxl_goal_position[index][i])

        while 1:
            # Read present position
            isMoving = [True, True, True, True]
            for i in range(4):
                dxl_present_position = readPos(i + 1)
                if not abs(dxl_goal_position[index][i] - dxl_present_position) > DXL_MOVING_STATUS_THRESHOLD:
                    isMoving[i] = False

            if not (isMoving[0] and isMoving[1] and isMoving[2] and isMoving[3]):
                break

        # Change goal position
        index += 1
        if index > 4:
            index = 0

    # Disable Dynamixel Torque
    torqueEnable(1, False)
    torqueEnable(2, False)
    torqueEnable(3, False)
    torqueEnable(4, False)
    # Close port
    portHandler.closePort()
