import os, discord
from attendance import Member, day_reset, conn, table_init, get_all_attendance_info, scoreboard, attendance_lock
from datetime import datetime, timedelta
from access_data import time_read, time_save
from config import admin_ids

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
    
    if message.content.startswith("!날갱"):
        msg = message.content.lstrip("!날갱")
        if len(msg) > 280:
            msg = msg[:280]
        
        present_time = datetime.today()
        if is_day_changed(time_read(), present_time, update_time_delta):
            day_reset()
            time_save(present_time)

        result = member.nalgang(msg)

        if result == None:
            await message.channel.send("{:s}님은 이미 날갱되었습니다.".format(member.name))
        else:
            point, combo_point = result
            await message.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(member.name,point))
            if combo_point != 0:
                await message.channel.send("와! {:s}님이 전근으로 {:d}점을 얻었습니다!".format(member.name,combo_point))
        
        attendance_info = get_all_attendance_info()
        description = ""
        for index, info in enumerate(attendance_info):
            name = message.guild.get_member(info[0]).display_name
            msg = info[1]
            description += str(index+1) + ". " + name + ": " + msg + "\n"

        embed = discord.Embed(title="오늘의 날갱", description=description)
        await message.channel.send(embed=embed)
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
    
    if message.content == ("!순위표"):
        embed = discord.Embed(title="순위표", description=scoreboard(message.author.guild))
        await message.channel.send(embed=embed)
        return

    if message.content.startswith("!강제날갱"):
        if not (message.author.id in admin_ids):
            return
        ids = message.raw_mentions
        for Id in ids:
            member = Member(message.guild.get_member(Id))
            result = member.nalgang("강제날갱")

            if result == None:
                await message.channel.send("{:s}님은 이미 날갱되었습니다.".format(member.name))
            else:
                point, combo_point = result
                await message.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(member.name,point))
                if combo_point != 0:
                    await message.channel.send("와! {:s}님이 전근으로 {:d}점을 얻었습니다!".format(member.name,combo_point))
        return
    
    if message.content.startswith("!강제변경"):
        if not (message.author.id in admin_ids):
            return
        Id = message.raw_mentions[0]
        member = Member(message.guild.get_member(Id))
        arglist = message.content.split()
        point_after = int(arglist[2])
        combo_after = int(arglist[3])
        member.set_point(point_after)
        member.set_combo(combo_after)
        return


    if message.content == ("!초기화"):
        if not (message.author.id in admin_ids):
            return
        present_time = datetime.today()
        day_reset()
        time_save(present_time)
        await message.channel.send("날짜가 초기화되었습니다.")
        return
    
    if message.content == ("!잠금"):
        if not (message.author.id in admin_ids):
            return
        attendance_lock(message.author.guild)
        return

    if message.content == ("!도움"):
        await message.channel.send("```"+\
                "!날갱 (인사말): 날갱하기\n"+\
                "!점수 : 내 점수 확인하기\n"+\
                "!점수 @멘션 : 멘션한 계정의 점수 확인하기\n"+\
                "!보내기 @멘션 점수 : 멘션한 계정으로 점수 보내기\n"+\
                "!순위표 : 점수 순위표 출력하기\n"+\
                "!도움 : 도움말\n"+\
                "\n"+\
                "관리자 전용\n"+\
                "!강제날갱 @멘션 @멘션 : 멘션한 계정들을 날갱시키기\n"+\
                "!강제변경 @멘션 점수 콤보: 멘션한 계정의 점수와 콤보를 설정하기\n"+\
                "!초기화 : 날짜 초기화시키기\n"+\
                "!잠금 : 해당 날짜의 날갱을 막기\n"+\
                "\n"+\
                "깃허브 : https://github.com/3-24/nalgang\n"+\
                "```")
        return
    
    conn.commit()