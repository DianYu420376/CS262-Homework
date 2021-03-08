from  multiprocessing  import Queue,  Process
from logicmachine import LogicMachine
import os
from utils import *
import numpy as np



if __name__ == '__main__':
        send_prob = 0.3
        (ticks1, ticks2, ticks3) = (2,4,6)
        plot_fig = True

        os.remove('1.log')
        os.remove('2.log')
        os.remove('3.log')
        queue1 = Queue()
        queue2 = Queue()
        queue3 = Queue()

        p1 = LogicMachine(1, ticks1, queue1, queue2, queue3,send_prob)
        p2 = LogicMachine(2, ticks2, queue2, queue1, queue3,send_prob)
        p3 = LogicMachine(3, ticks3, queue3, queue1, queue2,send_prob)
        p1.start()
        p2.start()
        p3.start()
        p1.join()
        p2.join()
        p3.join()

        if plot_fig:
                time_stamp_data = get_data_all_machine()
                filename=f"images/ticks-{ticks1} {ticks2} {ticks3} send_prob-{send_prob}"
                #np.savez(filename+'.npz',
                #         time_stamp_data=time_stamp_data, ticks1=ticks1,ticks2=ticks2, ticks3=ticks3, send_prob=send_prob)
                plot_time_stamp(time_stamp_data, filename+'.png',ticks1,ticks2,ticks3,send_prob)
                print(filename)