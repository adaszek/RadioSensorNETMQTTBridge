import threading
import signal
import time
import redis

class MonitorThread(threading.Thread):
    def __init__(self, redis, sensor_id, terminate_flag, id):
        super().__init__()
        self.redis = redis
        self.sensor_id = sensor_id
        self.terminate_flag = terminate_flag
        self.id = id

    def run(self):
        while (not self.terminate_flag.is_set()):
            pipe = self.redis.pipeline()
            print("sensor:{sid}:temperature:timestamps".format(sid=self.sensor_id))
            pipe.zrange("sensor:{sid}:temperature:timestamps".format(sid=self.sensor_id), -1, -1)
            print(pipe.execute())
            self.terminate_flag.wait(5)

        print("killed {id}".format(id=self.id));

def get_capabilities(db):
    pipe = db.pipeline()
    pipe.smembers("sensors")
    pipe.hgetall("sensors:functions")
    pipe.hgetall("functions")
    return pipe.execute()

def main():
    flag = threading.Event()

    def do_exit(sig, stack):
        flag.set()
        raise SystemExit("Exiting - all threads are being killed")

    signal.signal(signal.SIGINT, do_exit)
    
    r = redis.StrictRedis(host='192.168.1.158', port=6379, db=0)

    print(get_capabilities(r)[1][b"55"])

    for i in range(1):
        t = MonitorThread(r, 55, flag, i)
        t.start()

    main_thread = threading.main_thread()

    for t in threading.enumerate():
        if t is not main_thread:
            t.join()

if __name__ == "__main__":
    main()


