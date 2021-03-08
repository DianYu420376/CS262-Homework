from  multiprocessing  import Queue,  Process
from queue import Empty

from datetime import datetime
import random
import time

class LogicMachine(Process):
    def __init__(self,id, ticks, inqueue, outque1,outque2,send_prob):
        super(LogicMachine,self).__init__()
        self.id = id
        self.inqueue = inqueue
        self.outq1 = outque1
        self.outq2 = outque2
        self.ticks = ticks
        self.timestamp = 0
        self.send_prob = send_prob
        with open(f"{self.id}.log",'a') as f:
            f.write(f"Ticks: {self.ticks}\n")


    def run(self):
        #only run 10 second for testing now
        for i in range(60):
            for tick in range(self.ticks):
                try:
                    msg = self.inqueue.get_nowait()
                    self.timestamp = max(self.timestamp, msg[0])+1
                    with open(f"{self.id}.log",'a') as f:
                        now = datetime.now()
                        current_time = now.strftime("%H:%M:%S")
                        f.write(f"Received at global time: {current_time}, logical time: {self.timestamp}, length of message queue: {self.inqueue.qsize()}\n")
                except Empty:
                    code = random.uniform(0,10)
                    self.send_msg(code)
            time.sleep(1)
                
        
    def send_msg(self,code):
        send_prob = self.send_prob
        if code <= send_prob/3*10:
            self.outq1.put((self.timestamp,"Hello from {}".format(self.id)))
            self.timestamp += 1
            with open(f"{self.id}.log",'a') as f:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                f.write(f"Send to 1 at {current_time}, logical time: {self.timestamp}, length of message queue: {self.inqueue.qsize()}\n")

        elif code <= 2*send_prob/3*10:
            self.outq2.put((self.timestamp,"Hello from {}".format(self.id)))
            self.timestamp += 1
            with open(f"{self.id}.log",'a') as f:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                f.write(f"Send to 2 at {current_time}, logical time: {self.timestamp}, length of message queue: {self.inqueue.qsize()}\n")
        elif code <= send_prob*10:
            self.outq1.put((self.timestamp,"Hello from {}".format(self.id)))
            self.outq2.put((self.timestamp,"Hello from {}".format(self.id)))
            self.timestamp += 1
            with open(f"{self.id}.log",'a') as f:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                f.write(f"Send to both at {current_time}, logical time: {self.timestamp}, length of message queue: {self.inqueue.qsize()}\n")
        else:
            self.timestamp += 1
            with open(f"{self.id}.log",'a') as f:
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                f.write(f"internal event at {current_time}, logical time: {self.timestamp}, length of message queue: {self.inqueue.qsize()}\n")




if __name__ == '__main__':
    queue1 = Queue()
    queue2 = Queue()
    queue3 = Queue()

    send_prob = .6
    ticks1 = 2
    ticks2 = 4
    ticks3 = 6
    p1 = LogicMachine(1,ticks1, queue1, queue2,queue3,send_prob)
    p2 = LogicMachine(2,ticks2, queue2,queue1, queue3,send_prob)
    p3 = LogicMachine(3,ticks3, queue3, queue1,queue2,send_prob)
    p1.start()
    p2.start()
    p3.start()
    p1.join()
    p2.join()
    p3.join()

    