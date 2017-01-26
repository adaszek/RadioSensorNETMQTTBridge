import paho.mqtt.client as mqtt
import time
from struct import *
import redis

r = redis.StrictRedis(host='192.168.1.158', port=6379, db=0)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("r/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(strftime("%a, %d %b %Y %H:%M:%S")+" "+msg.topic+" "+str(msg.payload))

def on_temperature(client, userdata, msg):
    r.zadd('temperature', int(time.time()), str(format(unpack('f', msg.payload)[0], '.1f')))

def on_humidity(client, userdata, msg):
    r.zadd('humidity', int(time.time()), str(format(unpack('f', msg.payload)[0], '.1f')))

def on_voltage(client, userdata, msg):
    r.zadd('voltage', int(time.time()), str(float(format(unpack('I', msg.payload)[0]))/1000))

print(int(time.time()))


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.message_callback_add("r/l/+/s/+/t", on_temperature)
client.message_callback_add("r/l/+/s/+/h", on_humidity)
client.message_callback_add("r/l/+/s/+/v", on_voltage)

client.connect("192.168.1.157", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
