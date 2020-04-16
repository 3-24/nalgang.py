from datetime import datetime
import os,sys

os.chdir(sys.path[0]) # change working dir as script dir to get fixed relative access to data
if not os.path.exists("data"): os.makedirs("data")

def count_read():
    try:
        with open("./data/attendance_count.data",'r') as f:
            return int(f.readline().strip())
    except IOError:
        count_save(0)
        return 0

def count_save(n):
    with open("./data/attendance_count.data",'w') as f:
        f.write(str(n))
        return

def count_add(): count_save(count_read() + 1)

def time_read():
    try:
        with open("./data/attendance_time.data") as f:
            return datetime.fromtimestamp(float(f.readline().strip()))
    except IOError:
        t = datetime.today()
        time_save(t)
        return t

def time_save(t):
    with open("./data/attendance_time.data",'w') as f:
        f.write(str(datetime.timestamp(t)))