import paho.mqtt.client as mqtt
from struct import *

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("r/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

def on_float(client, userdata, msg):
    print(msg.topic+" "+str(format(unpack('f', msg.payload)[0], '.1f')))

def on_uint32(client, userdata, msg):
    print(msg.topic+" "+str(float(unpack('I', msg.payload)[0])/1000))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.message_callback_add("r/l/+/s/+/t", on_float)
client.message_callback_add("r/l/+/s/+/h", on_float)
client.message_callback_add("r/l/+/s/+/v", on_uint32)

client.connect("192.168.1.157", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
