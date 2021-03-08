import numpy as np
from matplotlib import pyplot as plt
def readlog(filename):
    file = open(filename)
    file_lines = file.readlines()
    numberOfLines = len(file_lines)
    dataArray = np.zeros((numberOfLines, 2))
    index = 0
    for line in file_lines:
        line = line.strip() # 参数为空时，默认删除开头、结尾处空白符（包括'\n', '\r',  '\t',  ' ')
        formLine = line.split(',')
        try:
            time_stamp = formLine[1]
            time_stamp = ''.join(x for x in time_stamp if x.isdigit())
            time_stamp = int(time_stamp)
            length_q = None
            dataArray[index,0] = time_stamp
            dataArray[index,1] = length_q
            index += 1
        except:
            pass
    return dataArray[:index,0]

def get_data_all_machine():
    time_stamp_data1 = readlog('1.log')
    time_stamp_data2 = readlog('2.log')
    time_stamp_data3 = readlog('3.log')
    time_stamp_data = [time_stamp_data1, time_stamp_data2, time_stamp_data3]
    return time_stamp_data

def plot_time_stamp(time_stamp_data,filename,ticks1,ticks2,ticks3,send_prob):
    plt.figure()
    plt.plot(np.linspace(0,1,len(time_stamp_data[0])), time_stamp_data[0])
    plt.plot(np.linspace(0,1,len(time_stamp_data[1])),time_stamp_data[1])
    plt.plot(np.linspace(0,1,len(time_stamp_data[2])),time_stamp_data[2])
    plt.legend([f'Machine 1 (Ticks = {ticks1})', f'Machine 2 (Ticks = {ticks2})', f'Machine 3 (Ticks = {ticks3})'])
    plt.title(f'Probability of events being external: {send_prob}', fontsize=10)
    plt.xlabel('Global Time')
    plt.ylabel('Time Stamp')
    plt.savefig(filename)

if __name__ == '__main__':
    #time_stamp_data = readlog('1.log')
    time_stamp_data = get_data_all_machine()
    plot_time_stamp(time_stamp_data, 'data/tryout.png', 4,5,6,.03)