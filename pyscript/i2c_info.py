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


def print_devices(device_list):
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

def get_device_with_name(device_list, type, name):
    for device in device_list:
        if (device.moduletype.lower() == type.lower()):
            cmd = f'name,?'
            response = device.query(cmd)
            device_name = response.split(',')[1]
            if (device_name.lower() == name.lower()):
                LOGGER.info(f'Found {type}:{name}')
                return device
    LOGGER.info(f'***No*** {type}:{name}')
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

def calibrate_no_check(device, target):
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

def calibrate_without_clear(device, target):
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

def multi_point_calibration_without_clear(device, point, target):
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

    # calibrate
    cmd = f"cal,{point},{target:.2f}"
    LOGGER.info(f"Calibrating: {point:s} => {target:.3f} ... {cmd}")
    response = device.query(cmd)
    LOGGER.info(response)

    # make sure calibration is done
    loop = 0
    while True:
        if loop > TIMEOUT:
            raise TimeoutError()
        cmd = "cal,?"
        LOGGER.info(f'Calibration Checking -> {cmd}')
        response = device.query(cmd)
        LOGGER.info(f'Calibration --> {response}')
        if response.startswith("Success"):
            response_array = response.split(",")
            if len(response_array) > 1:
                is_calibrated = int(response_array[1])
                if is_calibrated == 1:
                    break
        loop = loop + 1
        time.sleep(1)

    LOGGER.info('Calibration done!')

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

def device_dispense(device, target):
    cmd = f"d,{target}"
    LOGGER.info("dispensing... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def display_name(device):
    cmd = "name,?"
    LOGGER.info("Get name... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def rename_device(device, name):
    cmd = f"name,{name}"
    LOGGER.info("Get name... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def get_output_parameters(device):
    cmd = "o,?"
    LOGGER.info("Get output parameters... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def get_probe_type(device):
    cmd = "k,?"
    LOGGER.info("Get probe type... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def set_probe_type(device, type):
    cmd = f"k,{type}"
    LOGGER.info("Set probe type... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def trust_calibration(device, target):
    cmd = f"cal,{target}"
    LOGGER.info("Trust calibration... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def trust_multi_point_calibration(device, point, target):
    cmd = f"cal,{point},{target}"
    LOGGER.info("Trust calibration... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def set_output_parameter(device, parameter, on):
    cmd = f"o,{parameter},{on}"
    LOGGER.info("Set output parameters... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

def device_change_address(device, address):
    cmd = f"i2c,{address}"
    LOGGER.info("Change address... {:s}".format(cmd))
    response = device.query(cmd)
    LOGGER.info(response)

@service
def device_calibrate(type, target):
    device_list = get_devices()
    device = get_device(device_list, type)
    calibrate(device,target)

@service
def dispence(target):
    device_list = get_devices()
    device = get_device(device_list, 'pmp')
    device_dispense(device, target)

@service
def device_calibrate_by_name(type, name, target):
    device_list = get_devices()
    device = get_device_with_name(device_list, type, name)
    calibrate_no_check(device,target)

@service
def device_info(type):
    device_list = get_devices()
    device = get_device(device_list, type)
    LOGGER.info(f"{type} --> " + device.get_device_info())
    display_calibration(device)
    display_name(device)
    sensor = read(device)
    LOGGER.info(f'{type} --> {sensor:f}')

@service
def device_info_by_name(type, name):
    device_list = get_devices()
    device = get_device_with_name(device_list, type, name)
    LOGGER.info(f"{type} --> " + device.get_device_info())
    display_calibration(device)
    display_name(device)
    sensor = read(device)
    LOGGER.info(f'{type} --> {sensor:f}')

@service
def device_rename_by_name(type, name, new_name):
    device_list = get_devices()
    device = get_device_with_name(device_list, type, name)
    rename_device(device, new_name)
    display_name(device)

@service
def rtd_rename(type, name):
    device_list = get_devices()
    device = get_device(device_list, type)
    display_name(device)
    rename_device(device, name)
    display_name(device)

@service
def all_devices():
    device_list = get_devices()
    for i in device_list:
        display_name(i)
        display_calibration(i)


@service
def type_change_address(type,address):
    device_list = get_devices()
    device = get_device(device_list, type)
    device_change_address(device, address)
    time.sleep(1)
    device_list = get_devices()
    device = get_device(device_list, type)
    LOGGER.info(f"{type} --> " + device.get_device_info())

@service
def ec_info():
    device_list = get_devices()
    device = get_device(device_list, 'ec')
    get_probe_type(device)
    get_output_parameters(device)

@service
def set_ec_parameters(param, on):
    device_list = get_devices()
    device = get_device(device_list, 'ec')
    set_output_parameter(device, param, on)
    get_output_parameters(device)

@service
def set_ec_type(type):
    device_list = get_devices()
    device = get_device(device_list, 'ec')
    set_probe_type(device, type)

@service
def set_trust_calibration(target):
    device_list = get_devices()
    device = get_device(device_list, 'ec')
    trust_calibration(device, target)

@service
def set_multi_point_trust_calibration(type, point, target):
    device_list = get_devices()
    device = get_device(device_list, type)
    trust_multi_point_calibration(device, point, target)


@service
def device_calibrate_without_clear(type, target):
    device_list = get_devices()
    device = get_device(device_list, type)
    calibrate_without_clear(device, target)

@service
def multi_point_calibration(type, point, target):
    device_list = get_devices()
    device = get_device(device_list, type)
    multi_point_calibration_without_clear(device, point, target)

@service
def clear_device_calibration(type):
    device_list = get_devices()
    device = get_device(device_list, type)
    clear_calibration(device)