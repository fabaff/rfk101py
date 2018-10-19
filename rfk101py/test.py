import rfk101py
import time

def callback(value):
    print(value)

print("Connecting to the card reader")
reader = rfk101py.rfk101py('192.168.2.55',4008,callback)
#reader = rfk101py.rfk101py('linux2.dubno.com',23,callback)

print("Waiting 10 seconds for callbacks")
time.sleep(10)

print("Closing")
reader.close()


