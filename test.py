import time
import datetime
import redis
import math
import functools

from collections import defaultdict

def decode_capabilities(to_parse, sensor_list, array_of_cap):
    ret_dict = {}
    for it in to_parse:
        if it in sensor_list:
            s_ret_dict = {}
            reads, writes, reports = to_parse[it].split(";")
            rkey, rcaps = reads.split(":")
            r = list(map(lambda x: array_of_cap[x] if (x in array_of_cap) else None, rcaps.split(",")))
            s_ret_dict[rkey] = r
            wkey, wcaps = writes.split(":")
            w = list(map(lambda x: array_of_cap[x] if (x in array_of_cap) else None, wcaps.split(",")))
            s_ret_dict[wkey] = w
            pkey, prep = reports.split(":")
            s_ret_dict[pkey] = prep
            ret_dict[it] = s_ret_dict
        else:
             print("There is no such device as {}".format(k))
    return ret_dict

def monitor_sensors(pipe):
    sensors = pipe.smembers("sensors")
    functions = pipe.hgetall("sensors:functions")
    map_functions = pipe.hgetall("functions")
    decoded_sensors = decode_capabilities(functions, sensors, map_functions)

    keys_to_monitor = defaultdict(list)
    
    for sensor in sensors:
        for cap in decoded_sensors[sensor]["r"]:
            if cap is not None:
                keys_to_monitor[sensor].append("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap))
        for cap in decoded_sensors[sensor]["w"]:
            if cap is not None:
                keys_to_monitor[sensor].append("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap))

    all_last_activities = {}

    while 1:
        try:
            # TODO: think how to decompose it, per sensor
            pipe.watch(keys_to_monitor.values())
            
            for sensor in sensors:
                last_measurements = []
                sensorpipe = pipe.pipeline()
                for key in keys_to_monitor[sensor]:
                    sensorpipe.zrange(key, -1, -1)
                
                last_measurements = sensorpipe.execute()
                last_activity = int(functools.reduce(lambda x,y: x[0] if (x[0] > y[0]) else y[0], last_measurements))
                print("sid\t{sid}\tlast activity {past}\tago :: {act}".format(sid=sensor, past=(datetime.datetime.now() - datetime.datetime.fromtimestamp(last_activity)), act=time.ctime(last_activity)))
                
                all_last_activities[sensor] = last_activity
                
            pipe.multi()
            pipe.hmset("sensors:last_activity", all_last_activities)
            pipe.execute()
            break;
        except WatchError:
            continue

def main():
    r = redis.StrictRedis(host='192.168.1.158', port=6379, db=0, encoding="utf-8", decode_responses=True)
    while 1:
        r.transaction(monitor_sensors, ["sensors", "sensors::functions", "functions"])
        time.sleep(5)

if __name__ == "__main__":
    main()
