"""
RFK101 is a library for receiving keycard (and keypress) information
from an IDTECK STAR RFK101 keypad/proximity card reader.  There is a
good chance that this library will work with other IDTECK STAR
products, but they have not been tested.

The device is connected to an RS232 to Ethernet adaptor (NPort) and
uses sockets for communication.

Michael Dubno - 2018 - New York
"""
from threading import Thread
import time
import socket
import select
import logging

_LOGGER = logging.getLogger(__name__)

POLLING_FREQ = 1.
MAX_BUFFER_SIZE = 80

STATE_WAIT_FOR_START = 1
STATE_WAIT_FOR_END = 2
STATE_WAIT_FOR_CHECKSUM = 3

class rfk101py(Thread):
    """Interface with IDTECK STAR RFK101 keypad/prox reader."""
    _checksum = None
    _socket = None

    def __init__(self, host, port, callback=None):
        Thread.__init__(self, target=self, name='rfk101py')
        self._host = host
        self._port = port
        self._callback = callback

        self._state = STATE_WAIT_FOR_START
        self._buffer = ''
        self._running = False

        self._connect()
        self.start()

    def _connect(self):
        # Add userID and password
        self._socket = socket.create_connection((self._host, self._port))

    def run(self):
        self._running = True
        while self._running:
            try:
                readable, _, _ = select.select([self._socket], [], [], POLLING_FREQ)
            except socket.error as err:
                raise
            if len(readable) != 0:
                self._state_machine(self._socket.recv(1))

    def close(self):
        """Close the connection."""
        self._running = False
        time.sleep(POLLING_FREQ)
        if self._socket:
            self._socket.close()
            self._socket = None

    def _state_machine(self, byte):
        byte = byte[0]
        if self._state == STATE_WAIT_FOR_START:
            if byte == 0x02:   # START
                self._buffer = ''
                self._checksum = 0x02
                self._state = STATE_WAIT_FOR_END

        elif self._state == STATE_WAIT_FOR_END:
            self._checksum ^= byte
            if byte == 0x03:   # END
                self._state = STATE_WAIT_FOR_CHECKSUM
            elif len(self._buffer) < MAX_BUFFER_SIZE:
                self._buffer += chr(byte)
            else:
                self._state = STATE_WAIT_FOR_START

        elif self._state == STATE_WAIT_FOR_CHECKSUM:
            self._checksum &= 0xff
            if byte == self._checksum:
                if self._callback:
                    self._callback(self._buffer)
            else:
                _LOGGER.error("Checksum failed for '%s' %d vs %d", self._buffer, byte, self._checksum & 0xff)

            self._state = STATE_WAIT_FOR_START
