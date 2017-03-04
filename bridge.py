import paho.mqtt.client as mqtt
import time
from struct import *
import redis

r = redis.StrictRedis(host='192.168.1.158', port=6379, db=0)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("r/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(time.strftime("%a, %d %b %Y %H:%M:%S")+" "+msg.topic+" "+str(msg.payload))

def on_temperature(client, userdata, msg):
    sensor_id = 'sensor:{id}'.format(id=msg.topic.split('/')[4]);
    now = int(time.time())
    pipe = r.pipeline()
    # TODO: incr is done outside transaction
    event_id = r.incr(sensor_id + ':temperature:events')
    pipe.zadd(sensor_id + ':temperature:timestamps', event_id, now)
    pipe.hset(sensor_id + ':temperature', now, str(format(unpack('f', msg.payload)[0], '.1f')))
    pipe.execute() 

def on_humidity(client, userdata, msg):
    sensor_id = 'sensor:{id}'.format(id=msg.topic.split('/')[4]);
    now = int(time.time())
    pipe = r.pipeline()
    event_id = r.incr(sensor_id + ':humidity:events')
    pipe.zadd(sensor_id + ':humidity:timestamps', event_id, now)
    pipe.hset(sensor_id + ':humidity', now, str(format(unpack('f', msg.payload)[0], '.1f')))
    pipe.execute() 

def on_voltage(client, userdata, msg):
    sensor_id = 'sensor:{id}'.format(id=msg.topic.split('/')[4]);
    now = int(time.time())
    pipe = r.pipeline()
    event_id = r.incr(sensor_id + ':voltage:events')
    pipe.zadd(sensor_id + ':voltage:timestamps', event_id, now)
    pipe.hset(sensor_id + ':voltage', now, str(float(format(unpack('I', msg.payload)[0]))/1000))
    pipe.execute() 

def on_started(client, userdata, msg):
    topic = msg.topic.split('/')
    raw_sensor_id = topic[4]
    sensor_location = topic[2]
    sensor_id = 'sensor:{id}'.format(id=raw_sensor_id);
    now = int(time.time())
    pipe = r.pipeline()
    pipe.zadd(sensor_id + ":starts", 0, now);
    pipe.hset('sensors:last_location', raw_sensor_id, sensor_location)
    pipe.hset('sensors:functions', raw_sensor_id, msg.payload)
    pipe.sadd('sensors', raw_sensor_id)
    pipe.execute() 
    print "started"

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.message_callback_add("r/l/+/s/+/t", on_temperature)
client.message_callback_add("r/l/+/s/+/h", on_humidity)
client.message_callback_add("r/l/+/s/+/v", on_voltage)
client.message_callback_add("r/l/+/s/+/a", on_started)

client.connect("192.168.1.157", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
