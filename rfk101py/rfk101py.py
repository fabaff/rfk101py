"""
RFK101 is a library for receiving keycard (and keypress) information
from an IDTECK STAR RFK101 keypad/proximity card reader.  There is a
good chance that this library will work with other IDTECK STAR
products, but they have not been tested.

The device is connected to an RS232 to Ethernet adaptor (NPort) and
uses the telnet protocols for communication.

Michael Dubno - 2018 - New York
"""

from threading import Thread
import time
import telnetlib

POLLING_FREQ = 1.

STATE_WAIT_FOR_START    = 1
STATE_WAIT_FOR_END      = 2
STATE_WAIT_FOR_CHECKSUM = 3

class rfk101py(Thread):
    """Interface with IDTECK STAR RFK101 keypad/prox reader."""

    def __init__(self,host,port,callback=None):
        Thread.__init__(self,target=self,name='rfk101py')
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
        self._telnet = telnetlib.Telnet( self._host, self._port )

    def run(self):
        self._running = True
        while self._running:
            input = self._telnet.read_until(b' ',POLLING_FREQ)
            if len(input) > 0:
                for b in input:
                    self._stateMachine(b)

    def close(self):
        self._running = False
        time.sleep(POLLING_FREQ)
        if self._telnet:
            self._telnet.close()
            self._telnet = None

    def _stateMachine(self,b):
        if self._state == STATE_WAIT_FOR_START:
            if b == 0x02:   # START
                self._buffer = ''
                self._checksum = 0x02
                self._state = STATE_WAIT_FOR_END

        elif self._state == STATE_WAIT_FOR_END:
            self._checksum ^= b
            if b == 0x03:   # END
                self._state = STATE_WAIT_FOR_CHECKSUM
            else:
                self._buffer += chr(b)
                # FIX: Add length overflow check here

        elif self._state == STATE_WAIT_FOR_CHECKSUM:
            self._checksum &= 0xff
            if b == self._checksum:
                if self._callback:
                    self._callback(self._buffer)
            # FIX: Potentially something should be done when bad data is received
            self._state = STATE_WAIT_FOR_START
