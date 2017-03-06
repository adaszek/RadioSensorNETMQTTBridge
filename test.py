import threading
import signal
import time

class MonitorThread(threading.Thread):
    def __init__(self, terminate_flag, id):
        super().__init__()
        self.terminate_flag = terminate_flag
        self.id = id

    def run(self):
        while (not self.terminate_flag.is_set()):
            print("dupa {id}".format(id=self.id));
            self.terminate_flag.wait(1)

        print("killed {id}".format(id=self.id));


def main():
    flag = threading.Event()

    def do_exit(sig, stack):
        flag.set()
        raise SystemExit("Exiting - all threads are being killed")

    signal.signal(signal.SIGINT, do_exit)

    for i in range(20):
        t = MonitorThread(flag, i)
        t.start()

    main_thread = threading.main_thread()

    for t in threading.enumerate():
        if t is not main_thread:
            t.join()

if __name__ == "__main__":
    main()


