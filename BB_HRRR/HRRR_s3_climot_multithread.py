# Brian Blaylock
# March 27, 2017                                 One week until I go to Boston!

import numpy as np
from queue import Queue
from threading import Thread
from datetime import datetime, timedelta

import sys
sys.path.append('/uufs/chpc.utah.edu/common/home/u0553130/pyBKB_v2')
sys.path.append('B:\pyBKB_v2')
from BB_downloads.HRRR_S3 import *
from BB_basemap.draw_maps import draw_CONUS_HRRR_map

# --- Stuff you may want to change --------------------------------------------
DATE = datetime(2016, 11, 1)
eDATE = datetime(2016, 11, 7)

variable = 'TMP:2 m'
# -----------------------------------------------------------------------------

days = (eDATE - DATE).days
DATES = [DATE + timedelta(days=x) for x in range(0, days)]

date_list = []

def worker():
    """
    This is what the thread will do when called and given input.
    """
    while True:
        item = q.get()
        print "\nWork on hour:", item

        # Download the file for every hour between the time period
        for D in DATES:
            DateHour = datetime(D.year, D.month, D.day, item)
            H = get_hrrr_variable(DateHour, variable, fxx=0, model='hrrr', field='sfc')
            global date_list
            date_list.append(DateHour)
        # Do something with the data in that file
        q.task_done()

timer1 = datetime.now()

# Hour list 
hour_list = range(0,24)



Ps = range(1, 32)
Ts = range(5, 10)
RESULT = np.zeros([len(Ps),len(Ts)])
RESULT = np.zeros([32,10])

for i in Ps:
    for j in Ts:
        q = Queue()
        # import multiprocessing #:)
        def do_this(hour_list):
            # Set up number of threads
            num_of_threads = j
            # Initalize a queue for each thread. The Thread will do the "worker" function
            for i in range(num_of_threads):
                t = Thread(target=worker)
                t.daemon = True
                t.start()

            # Add a task to the queue
            for item in hour_list:
                q.put(item)

            q.join()       # block until all tasks are done
            return 

        # Create a list to iterate over. 
        # (Note: Multiprocessing only accepts one item at a time)
        some_list = [range(0,3), range(3,6), range(6,9), range(9,12), range(12, 15), range(15, 18), range(18, 21), range(21,24)]
        some_list = [[i] for i in range(24)]

        # Multiprocessing :)
        num_proc = multiprocessing.cpu_count() # use all processors
        num_proc = i                          # specify number to use (to be nice)
        p = multiprocessing.Pool(num_proc)
        result = p.map(do_this, some_list)

        print result

        seconds = (datetime.now() - timer1).seconds
        print "Time to download operational HRRR (Threads):", seconds, 'seconds'
        print "count: %s of %s" % (len(date_list), len(DATES)*24)

        minutes_completed = 365*2/days * seconds/60
        print minutes_completed, 'mins'
        RESULT[i-1, j-1] = minutes_completed
        print RESULT