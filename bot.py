import os, discord
from attendance import Member, day_reset, conn, table_init
from datetime import datetime, timedelta
from access_data import *

update_time_delta = timedelta(hours=6, minutes=0)
client = discord.Client()
table_init()

def check_int(s):
    try: return str(int(s)) == s
    except ValueError: return False

def is_day_changed(past_time, present_time, delta):
    past_delta = past_time - delta
    present_delta = present_time - delta
    return present_delta.day > past_delta.day or present_delta.month > past_delta.month or present_delta.year > past_delta.year 

@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))

@client.event
async def on_message(message):
    conn.commit()
    if message.author.bot: return
    
    if message.content == ('!날갱'):
        m = Member(message.author.id, message.author.display_name)
        present_time = datetime.today()
        if is_day_changed(time_read(), present_time, update_time_delta):
            day_reset()
            time_save(present_time)

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