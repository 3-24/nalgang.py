import sqlite3
from access_data import *
from config import point_by_rank, week_bonus, month_bonus

conn = sqlite3.connect("./data/member.db")
c = conn.cursor()

class Member:
    def __init__(self, user):
        self.id_num = user.id
        self.name = user.display_name
        self.user = user
        return
    
    def mention(self):
        return self.user.mention
    
    def exist_db(self):
        c.execute('''SELECT id FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = c.fetchone()
        if P == None: return False
        else: return True

    def add_db(self,point=0,combo=0):
        c.execute('''INSERT INTO Members VALUES (:Id, :point, :combo)''',{"Id":self.id_num, "point":point, "combo":combo})
    

    def get_point(self):
        c.execute('''SELECT point FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = c.fetchone()
        if P == None: return None
        else: return P[0]

    def add_point(self,point):
        prev_point = self.get_point()
        c.execute('''UPDATE Members SET point=:point WHERE id=:Id''', {"Id":self.id_num, "point":prev_point+point})
        return
    
    def set_point(self,point):
        c.execute('''UPDATE Members SET point=:point WHERE id=:Id''', {"Id":self.id_num, "point":point})
        return

    def get_combo(self):
        c.execute('''SELECT combo FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = c.fetchone()
        if P == None: return None
        else: return P[0]
    
    def set_combo(self,combo):
        c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":self.id_num, "combo":combo})
        return

    def add_combo(self, combo):
        self.set_combo(self.get_combo()+combo)
    
    def check_attendance(self):
        c.execute('''SELECT * FROM AttendanceTable WHERE id= :Id''', {"Id": self.id_num})
        attendance = c.fetchone()
        return attendance != None
    
    def set_attendance(self, msg):
        c.execute('''INSERT INTO AttendanceTable VALUES (:Id, :message)''',{"Id":self.id_num, "message":msg})
        return
    
    def give_attendance_point(self):
        point = point_by_rank[min(count_read(),len(point_by_rank)-1)]
        self.add_point(point)
        return point
    
    def give_attendance_event_point(self):
        event_point = 0
        if self.get_combo() % 7 == 0:
            event_point += week_bonus
        if self.get_combo() % 30 = 0:
            event_point += month_bonus
        self.add_point(event_point)
        return event_point

    def nalgang(self,msg):
        if self.check_attendance(): return None
        self.set_attendance(msg)
        if not self.exist_db():
            self.add_db()
        
        point = self.give_attendance_point()
        event_point = self.give_attendance_event_point()

        self.add_combo(1)
        count_add()
        return point, event_point

    def give_point(self,member,point):
        assert self.get_point() >= point >= 0
        self.add_point(-point)
        member.add_point(point)
        return


def table_init():
    c.execute('''CREATE TABLE IF NOT EXISTS Members (id integer, point integer, combo integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTable (id integer, message nvarchar)''')
    return


def combo_reset():
    c.execute('''SELECT id FROM AttendanceTable''')
    attendenceList=[i[0] for i in c.fetchall()]
    c.execute('''SELECT id FROM Members''')
    memberList=[i[0] for i in c.fetchall()]
    for Id in memberList:
        if Id not in attendenceList:
            c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":Id, "combo":0})
    return


def day_reset():
    combo_reset()
    c.execute('''DROP TABLE AttendanceTable''')
    table_init()
    count_save(0)
    return

def get_all_attendance_info():
    c.execute('''SELECT * FROM AttendanceTable''')
    return c.fetchall()

def scoreboard(guild):
    c.execute('''SELECT id, point FROM Members ORDER BY point DESC''')
    s=''
    point=float('inf')
    rank, count = 1,1
    for Id, Point in c.fetchall():
        member=guild.get_member(Id)
        if member==None: continue
        if point != Point:
            rank = count
            point = Point
        s+="{:d}. {:d}점 {:s}\n".format(rank,Point,member.name)
        count += 1
    return s

def attendance_lock(guild):
    c.execute('''SELECT id FROM Members''')
    for Id in c.fetchall():
        user = guild.get_member(Id[0])
        if user == None: continue
        member = Member(user)
        member.set_attendance("")
    return
        
