'''
CS5250 Assignment 4, Scheduling policies simulator
Sample skeleton program
Author: Minh Ho
Input file:
    input.txt
Output files:
    FCFS.txt
    RR.txt
    SRTF.txt
    SJF.txt

Apr 10th Revision 1:
    Update FCFS implementation, fixed the bug when there are idle time slices between processes
    Thanks Huang Lung-Chen for pointing out
Revision 2:
    Change requirement for future_prediction SRTF => future_prediction shortest job first(SJF), the simpler non-preemptive version.
    Let initial guess = 5 time units.
    Thanks Lee Wei Ping for trying and pointing out the difficulty & ambiguity with future_prediction SRTF.
'''
import sys
import Queue
import copy

input_file = 'input.txt'

class Process:
    last_scheduled_time = 0
    processed_time = 0
    def __init__(self, id, arrive_time, burst_time):
        self.id = id
        self.arrive_time = arrive_time
        self.burst_time = burst_time
    #for printing purpose
    def __repr__(self):
        return ('[id %d : arrive_time %d,  burst_time %d]'%(self.id, self.arrive_time, self.burst_time))

def FCFS_scheduling(process_list):
    #store the (switching time, proccess_id) pair
    schedule = []
    current_time = 0
    waiting_time = 0
    for process in process_list:
        if(current_time < process.arrive_time):
            current_time = process.arrive_time
        schedule.append((current_time,process.id))
        waiting_time = waiting_time + (current_time - process.arrive_time)
        current_time = current_time + process.burst_time
    average_waiting_time = waiting_time/float(len(process_list))
    return schedule, average_waiting_time

#Input: process_list, time_quantum (Positive Integer)
#Output_1 : Schedule list contains pairs of (time_stamp, proccess_id) indicating the time switching to that proccess_id
#Output_2 : Average Waiting Time
def RR_scheduling(process_list, time_quantum ):
    RR_process_list = copy.deepcopy(process_list)
    schedule = []
    schedule_queue = Queue.Queue()
    current_process = None
    current_quantum = 0
    current_time = 0
    waiting_time = 0
    num_process = len(RR_process_list)

    while RR_process_list or not schedule_queue.empty():

        print "At time " + str(current_time)

        # Adding process to schedule_queue based on arrival time
        for process in RR_process_list:
            if (current_time == process.arrive_time):
                schedule_queue.put(process)
                RR_process_list.remove(process)
                print "\tProcess " + str(process.id) + " put in schedule_queue"

        # CPU running current_process if it has a process assigned
        if current_process is not None:
            current_process.processed_time += 1
            current_quantum += 1
        # CPU get current_process from scheduler and run current_process
        elif not schedule_queue.empty():
            current_process = schedule_queue.get()
            schedule.append((current_time,current_process.id))
            current_process.processed_time += 1
            current_quantum += 1
            print "\tContext switch in process " + str(current_process.id)
       
        # Print which process consume 1 unit of processing time and update waiting time based on the queue size
        if current_process is not None:
            print "\tProcess " + str(current_process.id) + " processed 1 unit"
        print "\tIncrement of waiting time " + str(schedule_queue.qsize())
        waiting_time += schedule_queue.qsize()


        if current_process is not None:
            # Check for done process
            if current_process.processed_time == current_process.burst_time:
                print "\tProcess " + str(current_process.id) + " completed task and removing it permanently"
                current_process = None
                current_quantum = 0
    
            # Check for time_quantum
            elif (current_quantum == time_quantum):
                print "\tProcess " + str(current_process.id) + " has to context switch"
                schedule_queue.put(current_process)
                current_process = None
                current_quantum = 0

        current_time += 1

    avg_waiting_time = waiting_time / float(num_process)

    return schedule, avg_waiting_time

def SRTF_scheduling(process_list):
    SRTF_process_list = copy.deepcopy(process_list)
    schedule = []
    schedule_queue = Queue.PriorityQueue()
    current_process = None
    current_time = 0
    waiting_time = 0
    num_process = len(SRTF_process_list)

    while SRTF_process_list or not schedule_queue.empty():

        print "At time " + str(current_time)
        # Adding process to scheudle queue based on arrival time (adding burst_time as first priority and arrival_time as second priority)
        for process in SRTF_process_list:
            if (current_time == process.arrive_time):
                schedule_queue.put((process.burst_time,process.arrive_time,process))
                SRTF_process_list.remove(process)
                print "\tProcess " + str(process.id) + " put in schedule_queue"

        # Compare with the schedule_queue
        if current_process is not None and not schedule_queue.empty():

            compare_process = schedule_queue.get()
            if compare_process[0] < (current_process.burst_time-current_process.processed_time):
                print "\tCurrent process " + str(current_process.id) + " left with processing time " + str(current_process.burst_time-current_process.processed_time) + " which is more than " + str(compare_process[0]) + "(ID:" + str(compare_process[2].id) + ")"
                print "\tContext switch in Process " + str(compare_process[2].id)
                schedule_queue.put((current_process.burst_time-current_process.processed_time,current_process.arrive_time,current_process))
                current_process = compare_process[2]
                schedule.append((current_time, current_process.id))
            else:
                schedule_queue.put(compare_process)

        # CPU not assigned any process, get from schedule_queue
        elif not schedule_queue.empty():
            current_process = schedule_queue.get()[2]
            schedule.append((current_time, current_process.id))
            print "\tContext switch process " + str(current_process.id)

        waiting_time += schedule_queue.qsize()
        print "\tIncrement of waiting time " + str(schedule_queue.qsize())

        if current_process is not None:
            current_process.processed_time += 1

            # Check for done process
            if current_process.processed_time == current_process.burst_time:
                print "\tProcess " + str(current_process.id) + " completed task and removing it permanently"
                current_process = None


        current_time += 1

    avg_waiting_time = waiting_time / float(num_process)
    

    return schedule, avg_waiting_time

def SJF_scheduling(process_list, alpha):
    SJF_process_list = copy.deepcopy(process_list)
    schedule = []
    schedule_queue = Queue.PriorityQueue()
    current_process = None
    current_time = 0
    waiting_time = 0
    num_process = len(SJF_process_list)
    predicted_dict = {}
    initial_guess = 5

    # Initialize predicted_dict
    for process in SJF_process_list:
        predicted_dict[process.id] = initial_guess

    while SJF_process_list or not schedule_queue.empty():

        print "At time " + str(current_time)

        # Adding process to scheudle queue based on arrival time (adding predicted_burst_time as first priority and arrival_time as second priority)
        for process in SJF_process_list:
            if (current_time == process.arrive_time):
                schedule_queue.put((predicted_dict[process.id],process.arrive_time,process))
                SJF_process_list.remove(process)
                print "\tProcess " + str(process.id) + " put in schedule_queue with predicted burst time of " + str(predicted_dict[process.id])

        # Check whether process is done
        if current_process is None and not schedule_queue.empty():
            current_process = schedule_queue.get()[2]
            schedule.append((current_time,current_process.id))
            print "\tContext switch Process " + str(current_process.id)
        
        waiting_time += schedule_queue.qsize()
        print "\tIncrement of waiting time " + str(schedule_queue.qsize())

        # Start process current process
        if current_process is not None:
            current_process.processed_time += 1

            # Check for done process
            if current_process.processed_time == current_process.burst_time:
                predicted_dict[current_process.id] = predictor(alpha, current_process.burst_time, predicted_dict[current_process.id])
                print "\tProcess " + str(current_process.id) + " completed task and have new predicted burst of " + str(predicted_dict[current_process.id])
                current_process = None
                

        current_time += 1

    avg_waiting_time = waiting_time / float(num_process)

    return schedule,avg_waiting_time

# Formula to get the predicted of burst_time
def predictor(alpha, actual_burst, prev_predicted_value):
    return alpha*actual_burst + (1-alpha)*prev_predicted_value

def read_input():
    result = []
    with open(input_file) as f:
        for line in f:
            array = line.split()
            if (len(array)!= 3):
                print ("wrong input format")
                exit()
            result.append(Process(int(array[0]),int(array[1]),int(array[2])))
    return result
def write_output(file_name, schedule, avg_waiting_time):
    with open(file_name,'w') as f:
        for item in schedule:
            f.write(str(item) + '\n')
        f.write('average waiting time %.2f \n'%(avg_waiting_time))


def main(argv):
    process_list = read_input()
    print ("printing input ----")
    for process in process_list:
        print (process)
    print ("simulating FCFS ----")
    FCFS_schedule, FCFS_avg_waiting_time =  FCFS_scheduling(process_list)
    write_output('FCFS.txt', FCFS_schedule, FCFS_avg_waiting_time )
    print ("simulating RR ----")
    RR_schedule, RR_avg_waiting_time =  RR_scheduling(process_list,time_quantum = 2)
    write_output('RR.txt', RR_schedule, RR_avg_waiting_time )
    print ("simulating SRTF ----")
    SRTF_schedule, SRTF_avg_waiting_time =  SRTF_scheduling(process_list)
    write_output('SRTF.txt', SRTF_schedule, SRTF_avg_waiting_time )
    print ("simulating SJF ----")
    SJF_schedule, SJF_avg_waiting_time =  SJF_scheduling(process_list, alpha = 0.5)
    write_output('SJF.txt', SJF_schedule, SJF_avg_waiting_time )

if __name__ == '__main__':
    main(sys.argv[1:])
