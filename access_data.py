from datetime import datetime

attendance_count_path = "./data/attendance_count.data"
time_path = "./data/attendance_time.data"

def count_read():
    try:
        with open(attendance_count_path,'r') as f:
            return int(f.readline().strip())
    except IOError:
        count_save(0)
        return 0

def count_save(n):
    with open(attendance_count_path,'w') as f:
        f.write(str(n))
        return

def count_add(): count_save(count_read() + 1)

def time_read():
    try:
        with open(time_path,'r') as f:
            return datetime.fromtimestamp(float(f.readline().strip()))
    except IOError:
        t = datetime.today()
        time_save(t)
        return t

def time_save(t):
    with open(time_path,'w') as f:
        f.write(str(datetime.timestamp(t)))