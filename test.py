import threading
import signal
import time
import redis
import math

from itertools import islice

class MonitorThread(threading.Thread):
    def __init__(self, redis, capabilities, terminate_flag):
        super().__init__()
        self.redis = redis
        self.sensor_ids = capabilities.keys()
        self.capabilities = capabilities
        self.terminate_flag = terminate_flag

    def run(self):
        while (not self.terminate_flag.is_set()):
            pipe = self.redis.pipeline()
            for sensor in self.sensor_ids:
                for cap in self.capabilities[sensor]["r"]:
                    if cap is not None: 
                        print("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap))
                        pipe.zrange("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap), -1, -1)

                for cap in self.capabilities[sensor]["w"]:
                    if cap is not None: 
                        print("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap))
                        pipe.zrange("sensor:{sid}:{cid}:timestamps".format(sid=sensor, cid=cap), -1, -1)

            print(pipe.execute())
            self.terminate_flag.wait(5)

        print("killed {sids}".format(sids=self.sensor_ids));

def get_capabilities(db):
    pipe = db.pipeline()
    pipe.smembers("sensors")
    pipe.hgetall("sensors:functions")
    pipe.hgetall("functions")
    return pipe.execute()

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

def dict_chunks(data, size):
    it = iter(data)
    for i in range(0, len(data), size):
        yield {k:data[k] for k in islice(it, size)}

def main():
    flag = threading.Event()

    def do_exit(sig, stack):
        flag.set()
        raise SystemExit("Exiting - all threads are being killed")

    signal.signal(signal.SIGINT, do_exit)
    r = redis.StrictRedis(host='192.168.1.158', port=6379, db=0, encoding="utf-8", decode_responses=True)

    max_number_of_threads = 8
    number_of_threads = 0;

    sids, caps, array_of_cap = get_capabilities(r)

    if len(sids) < max_number_of_threads:
        number_of_threads = len(sids)
    else:
        number_of_threads = max_number_of_threads

    sensors = decode_capabilities(caps, sids, array_of_cap)
    how_many_per_thread = math.ceil(len(sensors)/number_of_threads)

    print("Number of threads: {} Sensors in db: {} Sensors per thread: {}".format(number_of_threads, len(sensors), how_many_per_thread))

    for sensors_to_process in dict_chunks(sensors, how_many_per_thread):
        t = MonitorThread(r, sensors_to_process, flag)
        t.start()

    main_thread = threading.main_thread()

    for t in threading.enumerate():
        if t is not main_thread:
            t.join()

if __name__ == "__main__":
    main()
