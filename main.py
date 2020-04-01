#/usr/bin/env/python3
import discord, os, sys,sqlite3, count, time
from datetime import datetime, timedelta

os.chdir(sys.path[0]) # changed working dir as script dir to get fixed relative access to data
TOKEN = os.environ["nalgang_TOKEN"]
client = discord.Client()

class Member:
    conn = sqlite3.connect("./data/member.db")
    c = conn.cursor()
    def __init__(self, id_num, name="temp"):
        self.id_num = id_num
        self.name = name
        return

    def add_db(self,point=0,combo=0):
        Member.c.execute('''INSERT INTO Members VALUES (:Id, :point, :combo)''',{"Id":self.id_num, "point":point, "combo":combo})
    
    def get_point(self):
        Member.c.execute('''SELECT point FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = Member.c.fetchall()
        if not P:
            self.add_db()
            return 0
        else:
            assert len(P) == 1
            return P[0][0]


    def add_point(self,p):
        prev_point = self.get_point()
        Member.c.execute('''UPDATE Members SET point=:point WHERE id=:Id''', {"Id":self.id_num, "point":p+prev_point})
        Member.conn.commit()
        return

    def get_combo(self):
        Member.c.execute('''SELECT combo FROM Members WHERE id=:Id''', {"Id":self.id_num})
        P = Member.c.fetchall()
        if not P:
            self.add_db()
            return 0
        else:
            assert len(P) == 1
            return P[0][0]

    def update_combo(self,reset=False):
        if reset:
            Member.c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":self.id_num, "combo":0})
            Member.conn.commit()
            return
        else:
            combo = self.get_combo()
            Member.c.execute('''UPDATE Members SET combo=:combo WHERE id=:Id''', {"Id":self.id_num, "combo":combo+1})
            Member.conn.commit()
            return
            

    def check_attendance(self):
        Member.c.execute('''SELECT * FROM AttendanceTable WHERE id= :Id''', {"Id": self.id_num})
        attendance = Member.c.fetchall()
        return attendance != []
    
    def set_attendance(self):
        Member.c.execute('''INSERT INTO AttendanceTable VALUES (:Id)''',{"Id":self.id_num})
        Member.conn.commit()
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


def sql_access(func):
    def access_table_wrapper(*args, **kwargs):
        kwargs['conn'] = sqlite3.connect("./data/member.db")
        kwargs['c'] = kwargs['conn'].cursor()
        r = func(*args, **kwargs)
        kwargs['conn'].close()
        return r
    return access_table_wrapper

@sql_access
def table_init(c,conn):
    c.execute('''CREATE TABLE IF NOT EXISTS Members (id integer, point integer, combo integer)''')
    c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTable (id integer)''')
    conn.commit()
    c.close()
    return


@sql_access
def combo_reset(c,conn):
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


@sql_access
def day_reset(c,conn):
    combo_reset()
    c.execute('''DROP TABLE AttendanceTable''')
    conn.commit()
    table_init()
    count.save(0)
    return


def check_int(s):
    try:
        return str(int(s)) == s
    except ValueError:
        return False

table_init()
update_time = None
update_time_delta = timedelta(hours=6, minutes=0)

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    global update_time

    if message.author.bot: return
    if message.content == ('!날갱'):
        m = Member(message.author.id, message.author.display_name)
        if update_time == None:
            update_time=datetime.today() - update_time_delta
        else:
            c = datetime.today() - update_time_delta
            if c.day > update_time.day or c.month > update_time.month or c.year > update_time.year:
                day_reset()
                update_time = c

        p,cp = m.update_attendance_and_point()
        
        if p == -1:
            await message.channel.send("{:s}님은 이미 날갱되었습니다. ({:d}연속 출석 중)".format(m.name,m.get_combo()))
            return
        else:
            if m.get_combo()>1:
                await message.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다! {:d}연속 출석으로 {:d}점을 추가로 얻었습니다!".format(m.name,p,m.get_combo(),cp))
            else:
                await message.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(m.name,p))
    
    if message.content.startswith("!날갱점수"):
        arglist = message.content.split()
        if len(arglist) >= 3:
            await message.channel.send("잘못된 입력입니다.")
            return
        elif len(arglist) == 1:
            m = Member(message.author.id, message.author.display_name)
        else:
            if not check_int(arglist[1]):
                await message.channel.send("잘못된 입력입니다.")
                return
            
            id_num = int(arglist[1])
            
            mu = client.get_user(id_num)
            if mu is None:
                await message.channel.send("찾을 수 없는 계정입니다.")
                return
            m = Member(id_num, mu.display_name)
        
        await message.channel.send("{:s}님의 날갱점수는 {:d}점입니다. {:d}연속 출석 중입니다.".format(m.name, m.get_point(), m.get_combo()))

    if message.content == "!id":
        await message.channel.send("{:d}".format(message.author.id))

    if message.content.startswith("!점수보내기"):
        arglist = message.content.split()
        if len(arglist) != 3:
            await message.channel.send("잘못된 입력입니다.")
            return
        else:
            if not check_int(arglist[1]):
                await message.channel.send("아이디 양식을 확인해주세요.")
                return
            if not check_int(arglist[2]):
                await message.channel.send("점수 양식을 확인해주세요.")
                return

            if int(arglist[2]) < 0:
                await message.channel.send("음수 점수를 보내지마세요!")
                return

            id_num = int(arglist[1])
            mu = client.get_user(id_num)
            if mu is None:
                await message.channel.send("찾을 수 없는 계정입니다.")
                return
            
            m0 = Member(message.author.id, message.author.display_name)
            m1 = Member(id_num, mu.display_name)
            point = int(arglist[2])

            if m0.get_point() < point:
                await message.channel.send("점수가 부족합니다.")
                return

            m0.give_point(m1, point)
            await message.channel.send("짜잔! {:s}님이 {:s}님에게 {:d}점을 선물했습니다.".format(m0.name,m1.name,point))

    if message.content == ("!날갱도움"):
        await message.channel.send("```"+\
                "!날갱 : 명령어가 곧 내용\n"+\
                "!날갱점수 : 내 점수 확인하기\n"+\
                "!id : 나의 $id 확인하기\n"+\
                "!날갱점수 $id : $id의 점수 확인하기\n"+\
                "!점수보내기 $id $pt : $id를 가진 계정으로 $pt만큼의 점수 보내기\n"+\
                "!날갱도움 : 도움말\n"+\
                "```")

client.run(TOKEN)
