import sqlite3
from config import point_by_rank, week_bonus, month_bonus
import os
import discord
from datetime import datetime, timedelta
import logging

conn = sqlite3.connect("./data/db.sqlite3", check_same_thread = False)
c = conn.cursor()
update_time_delta = timedelta(hours=6, minutes=0)
logger = logging.getLogger(__name__)

class Member:
    def __init__(self, user: discord.Member):
        if (user != None):
            self.id = user.id
            self.name = user.display_name
            self.user = user
            self.guild = user.guild.id
        return

    def mention(self):
        return self.user.mention
    
    def exist_db(self):
        c.execute('''SELECT id FROM Members WHERE id=? AND guild=?''', (self.id, self.guild))
        P = c.fetchone()
        return (False if P is None else True)

    def add_db(self,point=0,combo=0):
        c.execute('''INSERT INTO Members (id, guild, point, combo) VALUES (?, ?, ?, ?)''', (self.id, self.guild, point, combo))
        conn.commit()

    def get_point(self):
        c.execute('''SELECT point FROM Members WHERE id=? AND guild=?''', (self.id, self.guild))
        P = c.fetchone()
        return (None if P is None else P[0])
    
    def set_point(self, point):
        c.execute('''UPDATE Members SET point=? WHERE id=? AND guild=?''', (point, self.id, self.guild))
        conn.commit()
        return

    def add_point(self, point):
        self.set_point(self.get_point()+point)
        return
    
    def get_combo(self):
        c.execute('''SELECT combo FROM Members WHERE id=? AND guild=?''', (self.id, self.guild))
        P = c.fetchone()
        return (None if P is None else P[0])
    
    def set_combo(self,combo):
        c.execute('''UPDATE Members SET combo=? WHERE id=? AND guild=?''', (combo, self.id, self.guild))
        conn.commit()
        return

    def add_combo(self, combo):
        self.set_combo(self.get_combo()+combo)
    
    def check_attendance(self):
        c.execute('''SELECT * FROM AttendanceTable WHERE id=? AND guild=?''', (self.id, self.guild))
        return c.fetchone() != None
    
    def set_attendance(self, msg):
        c.execute('''INSERT INTO AttendanceTable (id, guild, message) VALUES (?, ?, ?)''', (self.id, self.guild, msg))
        conn.commit()
        return

    def give_attendance_point(self, rank: int):
        point = point_by_rank[min(rank,len(point_by_rank)-1)]
        self.add_point(point)
        return point
    
    def give_attendance_event_point(self):
        event_point = 0
        if self.get_combo() % 7 == 0:
            event_point += week_bonus
        if self.get_combo() % 30 == 0:
            event_point += month_bonus
        if self.get_combo() % 365 == 0:
            event_point += year_bonus
        self.add_point(event_point)
        return event_point
    
    def nalgang(self, msg, present_time = None):
        if present_time is None:
            present_time = datetime.today()
        c.execute('''SELECT count, time FROM AttendanceTimeCount WHERE guild=?''', (self.guild,))
        _ = c.fetchone()

        if _ is None:
            c.execute('''INSERT INTO AttendanceTimeCount (guild, count, time) VALUES (?,?,?)''', (self.guild, 1, datetime.timestamp(present_time)))
            count = 0
        else:
            count, table_time = _
            table_time = datetime.fromtimestamp(table_time)
            if is_day_changed(table_time, present_time, update_time_delta):
                day_reset()
                c.execute('''INSERT INTO AttendanceTimeCount (guild, count, time) VALUES (?,?,?)''', (self.guild, 1, datetime.timestamp(present_time)))
                count = 0
            else:
                if self.check_attendance(): return None
                c.execute('''UPDATE AttendanceTimeCount SET count=? WHERE guild=?''', (count+1, self.guild))
        conn.commit()

        self.set_attendance(msg)
        self.add_combo(1)
        point = self.give_attendance_point(count)
        event_point = self.give_attendance_event_point()

        return point, event_point

    def give_point(self, member, point):
        assert self.get_point() >= point >= 0
        self.add_point(-point)
        member.add_point(point)
        return



def table_init():
    c.execute('''CREATE TABLE IF NOT EXISTS Members (id integer, guild integer, point integer, combo integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTable (id integer, guild integer, message nvarchar)''')
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTimeCount (guild integer, count integer, time float)''')
    conn.commit()
    return


def combo_reset():
    logger.info("Updating whole combos...")
    c.execute('''SELECT id FROM AttendanceTable''')
    attendenceList=[i[0] for i in c.fetchall()]
    c.execute('''SELECT id FROM Members''')
    memberList=[i[0] for i in c.fetchall()]
    for Id in memberList:
        if Id not in attendenceList:
            c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":Id, "combo":0})
    conn.commit()
    logger.info("Combos updated.")
    return


def day_reset():
    combo_reset()
    c.execute('''DROP TABLE AttendanceTable''')
    c.execute('''DROP TABLE AttendanceTimeCount''')
    c.execute('''CREATE TABLE AttendanceTable (id integer, guild integer, message nvarchar)''')
    c.execute('''CREATE TABLE AttendanceTimeCount (guild integer, count integer, time float)''')
    conn.commit()
    return

def get_all_attendance_info(guild):
    c.execute('''SELECT id, message FROM AttendanceTable WHERE guild=?''', (guild,))
    return c.fetchall()

def scoreboard(guild):
    c.execute('''SELECT id, point FROM Members WHERE guild=? ORDER BY point DESC''', (guild.id,))
    s=''
    point = float('inf')
    rank, count = 1,1
    for Id, Point in c.fetchall():
        user =guild.get_member(Id)
        if user == None: continue
        if point != Point:
            rank = count
            point = Point
        s+="{:d}. {:d}점 {:s}\n".format(rank, Point, user.display_name)
        count += 1
        if count > 10:
            break
    return s

def is_day_changed(past_time, present_time, delta):
    past_delta = past_time - delta
    present_delta = present_time - delta
    return present_delta.day > past_delta.day or present_delta.month > past_delta.month or present_delta.year > past_delta.year