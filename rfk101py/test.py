import time
import rfk101py

def callback(value):
    print(value)

print("Connecting to the card reader")
reader = rfk101py.rfk101py('192.168.2.55', 4008, callback)

print("Waiting 120 seconds for callbacks")
time.sleep(120)

print("Closing")
reader.close()


