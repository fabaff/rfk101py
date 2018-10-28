"""
Support for reading data from an RFK101 keypad/prox card reader.

Michael Dubno - 2018 - New York
"""
import logging
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    CONF_HOST, CONF_PORT, CONF_NAME, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.entity import Entity

REQUIREMENTS = ['rfk101py==0.0.1']

_LOGGER = logging.getLogger(__name__)

DEFAULT_NAME = "RFK101"

EVENT_KEYCARD = 'keycard'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST): cv.string,
    vol.Required(CONF_PORT): cv.port,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the RFK101 platform."""
    host = config.get(CONF_HOST)
    port = config.get(CONF_PORT)
    name = config.get(CONF_NAME)

    try:
        sensor = RFK101Sensor(host, port, name)
    except OSError as error:
        _LOGGER.error("Could not connect to rfk101py. %s", error)
        return

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, sensor.stop())
    async_add_entities([sensor], True)


class RFK101Sensor(Entity):
    """Representation of an RFK101 sensor."""

    def __init__(self, host, port, name):
        """Initialize the sensor."""
        self._host = host
        self._port = port
        self._name = name
        self._state = None
        self._connection = None

    async def async_added_to_hass(self):
        """Handle when an entity is about to be added to Home Assistant."""
        from rfk101py.rfk101py import rfk101py
        self._connection = rfk101py(self._host, self._port, self._callback)

    async def _callback(self, card):
        """Send a keycard event message into HASS."""
        self.hass.bus.async_fire(EVENT_KEYCARD, {'card': card})

    async def stop(self):
        """Close resources."""
        if self._connection:
            self._connection.close()
            self._connection = None

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def should_poll(self):
        """No polling needed."""
        return False

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
