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
    #escape bot users
    if message.author.bot: return

    member = Member(message.author)
    
    if message.content == ('!날갱'):
        present_time = datetime.today()
        if is_day_changed(time_read(), present_time, update_time_delta):
            day_reset()
            time_save(present_time)

        result = member.update_attendance_and_point()

        if result == None:
            await message.channel.send("{:s}님은 이미 날갱되었습니다.".format(member.name))
        else:
            point, combo_point = result
            await message.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(member.name,point))
            if combo_point != 0:
                await message.channel.send("와! {:s}님이 전근으로 {:d}점을 얻었습니다!".format(member.name,combo_point))
        return

    if message.content.startswith("!점수"):
        ids = message.raw_mentions
        arglist = message.content.split()
        if ids != []:
            member = Member(message.guild.get_member(ids[0]))
        
        if not member.exist_db():
            await message.channel.send("등록되지 않은 사용자입니다.")
            return
        
        await message.channel.send("{:s}님의 날갱점수는 {:d}점입니다. {:d}연속 출석 중입니다.".format(member.name, member.get_point(), member.get_combo()))
        return

    if message.content.startswith("!보내기"):
        arglist = message.content.split()
        
        ids = message.raw_mentions
        
        if ids == []: return
        
        if not check_int(arglist[2]):
            await message.channel.send("점수 양식을 확인해주세요.")
            return
        
        point = int(arglist[2])

        if point <= 0:
            await message.channel.send("점수 양식을 확인해주세요.")
            return
        
        member_send = member
        member_receive = Member(message.guild.get_member(ids[0]))
        if not (member_send.exist_db() and member_receive.exist_db):
            await message.channel.send("등록되지 않은 사용자입니다.")
            return

        point = int(arglist[2])

        if member_send.get_point() < point:
            await message.channel.send("점수가 부족합니다.")
            return

        member_send.give_point(member_receive, point)
        await message.channel.send("짜잔! {:s}님이 {:s}님에게 {:d}점을 선물했습니다.".format(member_send.mention(), member_receive.mention(), point))
        return

    if message.content == ("!도움"):
        await message.channel.send("```"+\
                "!날갱 : 명령어가 곧 내용\n"+\
                "!점수 : 내 점수 확인하기\n"+\
                "!점수 @멘션 : 멘션한 계정의 점수 확인하기\n"+\
                "!보내기 @멘션 점수 : 멘션한 계정으로 점수 보내기\n"+\
                "!도움 : 도움말\n"+\
                "\n"+\
                "깃허브 : https://github.com/3-24/nalgang\n"+\
                "```")
        return
    
    conn.commit()