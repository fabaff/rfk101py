# RFK101 Package

Package to receive proximity card and keypad data from an RFK101
reader from IDTECK.  The RFK101 RS232 connection is done through
an Ethernet adaptor (NPort).

# Example:

    from time import sleep
    from pencompy import pencompy
    
    def callback(data):
        print("Received:",data)

    rfk = rfk101py( 'host.test.com', 4008, callback )

    # Sleep for 10 seconds waiting for a callback
    sleep(10.)

    # Close the interface
    rfk.close()
