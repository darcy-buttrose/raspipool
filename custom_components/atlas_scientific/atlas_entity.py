from homeassistant.helpers.entity import Entity


class AtlasEntity(Entity):

    def __init__(self, name, port, offset, scale):
        """Initialize the sensor."""
        self._state = None
        self._name = name
        self._offset = offset
        # try to convert variations of TEMP_CELSIUS, C, ºC, °C to a unique format
        lowercase_scale = scale[-1].lower()
        self._scale = lowercase_scale
        self._port_name = port
        self._port_number = int(port, 0)

