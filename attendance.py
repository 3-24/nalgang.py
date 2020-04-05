import sqlite3
import count

conn = sqlite3.connect("./data/member.db")
c = conn.cursor()

class Member:
    def __init__(self, id_num, name="temp"):
        self.id_num = id_num
        self.name = name
        return

    def add_db(self,point=0,combo=0):
        c.execute('''INSERT INTO Members VALUES (:Id, :point, :combo)''',{"Id":self.id_num, "point":point, "combo":combo})
    
    def get_point(self):
        c.execute('''SELECT point FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = c.fetchall()
        if not P:
            self.add_db()
            return 0
        else:
            assert len(P) == 1
            return P[0][0]


    def add_point(self,p):
        prev_point = self.get_point()
        c.execute('''UPDATE Members SET point=:point WHERE id=:Id''', {"Id":self.id_num, "point":p+prev_point})
        conn.commit()
        return

    def get_combo(self):
        c.execute('''SELECT combo FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = c.fetchall()
        if not P:
            self.add_db()
            return 0
        else:
            assert len(P) == 1
            return P[0][0]

    def update_combo(self,reset=False):
        if reset:
            c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":self.id_num, "combo":0})
        else:
            combo = self.get_combo()
            c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":self.id_num, "combo":combo+1})
        conn.commit()
        return
            

    def check_attendance(self):
        c.execute('''SELECT * FROM AttendanceTable WHERE id= :Id''', {"Id": self.id_num})
        attendance = c.fetchall()
        return attendance != []
    
    def set_attendance(self):
        c.execute('''INSERT INTO AttendanceTable VALUES (:Id)''',{"Id":self.id_num})
        conn.commit()
        return

    def update_attendance_and_point(self): # returb added point, combo point
        if self.check_attendance(): return -1, 0
        self.set_attendance()
        pointmap = [20,10,3,1]
        attcount = min(count.read(),3)
        p = pointmap[attcount]
        self.add_point(p)
        cp=self.get_combo()
        # cp modify
        cp = min(cp,7)
        self.update_combo()
        self.add_point(cp)
        count.add()
        return p, cp


    def give_point(self,member,point):
        self.add_point(-point)
        member.add_point(point)
        return


def table_init():
    c.execute('''CREATE TABLE IF NOT EXISTS Members (id integer, point integer, combo integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTable (id integer)''')
    conn.commit()
    return


def combo_reset():
    c.execute('''SELECT id FROM AttendanceTable''')
    attendenceList=[i[0] for i in c.fetchall()]
    c.execute('''SELECT id FROM Members''')
    memberList=[i[0] for i in c.fetchall()]
    for member in memberList:
        if member not in attendenceList:
            m=Member(member)
            m.update_combo(True)
    c.close()
    return


def day_reset():
    combo_reset()
    c.execute('''DROP TABLE AttendanceTable''')
    conn.commit()
    table_init()
    count.save(0)
    return