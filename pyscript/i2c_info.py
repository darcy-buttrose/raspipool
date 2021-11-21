import logging
import math
import time
import sys
import fcntl
from AtlasI2C import (
    AtlasI2C
)

TIMEOUT = 60

LOGGER = logging.getLogger(__name__)

def get_devices():
    device = AtlasI2C()
    device_address_list = device.list_i2c_devices()
    device_list = []

    for i in device_address_list:
        device.set_i2c_address(i)
        try:
            response = device.query("I")
            moduletype = response.split(",")[1]
            response = device.query("name,?").split(",")[1]
            device_list.append(AtlasI2C(address=i, moduletype=moduletype, name=response))
        except:
            continue
    return device_list


def print_devices(device_list, device):
    for i in device_list:
        if (i == device):
            LOGGER.info("--> " + i.get_device_info())
        else:
            LOGGER.info(" - " + i.get_device_info())


def get_device(device_list, name):
    for device in device_list:
        if (device.moduletype.lower() == name.lower()):
            return device
    return None

def calibrate(device, target):
    current = -1.0
    loop = 0
    # waiting for the reading to stabilize
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        sensor = read(device)
        time.sleep(1)
        LOGGER.info("Current value, sensor value: {:.2f} {:.2f}".format(current, sensor))
        if math.isclose(current, sensor, abs_tol=0.02):
            break
        current = sensor
        loop = loop + 1

    # clear previous calibration
    cmd = "cal,clear"
    LOGGER.info("Clearing previous calibration data... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

    # make sure calibration clear is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        response = device.query(cmd)
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 0:
                    break
        loop = loop + 1
        time.sleep(1)

    # calibrate
    if device.moduletype.lower() == "ph":
        # pH sensor require a special 3-point calibration
        # calibrate mid point
        cmd = "cal,mid,{:.2f}".format(target)
    else:
        cmd = "cal,{:.2f}".format(target)
    LOGGER.info("Calibrating: {:.3f} to target {:.3f}: {:s}".format(current, target, cmd))
    response = device.query(cmd)
    LOGGER.info(response)

    # make sure calibration clear is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        response = device.query(cmd)
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 1:
                    break
        loop = loop + 1
        time.sleep(1)

    # waiting for the read value to match the calibration target
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        sensor = read(device)
        time.sleep(1)
        if math.isclose(target, sensor, abs_tol=0.02):
            break
        LOGGER.info("Current value, target value: {:.3f}, {:.3f}".format(sensor, target))


def read(device):
    response = device.query("R")
    LOGGER.info("Sensor response: %s" % response)
    if response.startswith("Success"):
        try:
            floatVal = float(response.split(":")[1])
            LOGGER.info("OK [" + str(floatVal) + "]")
            return floatVal
        except:
            return 0.0
    else:
        return 0.0

def clear_calibration(device):
    # clear previous calibration
    cmd = "cal,clear"
    LOGGER.info("Clearing previous calibration data... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

    # make sure calibration clear is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        response = device.query(cmd)
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 0:
                    break
        loop = loop + 1
        time.sleep(1)

    LOGGER.info("clear_calibration: done!")

def display_calibration(device):
    cmd = "cal,?"
    LOGGER.info("Get previous calibration data... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

@service
def i2c_info():
    device_list = get_devices()
    device = get_device(device_list, "orp")
    display_calibration(device)


