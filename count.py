def read():
    try:
        with open("./data/attendance_count.txt",'r') as f:
            return int(f.readline().strip())
    except IOError:
        return 0

def save(n):
    with open("./data/attendance_count.txt",'w') as f:
        f.write(str(n))
        return

def add(): save(read() + 1)

