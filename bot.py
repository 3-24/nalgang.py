import os, discord
from attendance import Member, day_reset, conn, table_init, get_all_attendance_info, scoreboard, attendance_lock
from datetime import datetime, timedelta
from access_data import time_read, time_save
from discord.ext import commands

update_time_delta = timedelta(hours=6, minutes=0)
intents = discord.Intents(messages=True, guilds=True, members=True)
client = commands.Bot(command_prefix='!', description="도움말 명령어는 !도움", intents=intents)
client.remove_command('help')
table_init()

@client.event
async def on_ready():
    activity = discord.CustomActivity("도움말 명령어는 !도움")
    await client.change_presence(activity=activity)
    print("NalgangBot is ready.")

def check_int(s):
    try: return str(int(s)) == s
    except ValueError: return False

def is_day_changed(past_time, present_time, delta):
    past_delta = past_time - delta
    present_delta = present_time - delta
    return present_delta.day > past_delta.day or present_delta.month > past_delta.month or present_delta.year > past_delta.year

@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@client.check
async def globally_block_bot(ctx):
    role = discord.utils.find(lambda r: r.name == 'NalgangAPIClient', ctx.message.guild.roles)
    if role in ctx.author.roles:
        return True
    return not (ctx.author.bot)


@client.command(name="날갱")
async def nalgang(ctx, *, arg=""):
    member = Member(ctx.author)
    msg = arg
    if len(msg) > 280: msg = msg[:280]
        
    present_time = datetime.today()
    if is_day_changed(time_read(), present_time, update_time_delta):
        day_reset()
        time_save(present_time)

    result = member.nalgang(msg)

    if result == None:
        await ctx.channel.send("{:s}님은 이미 날갱되었습니다.".format(member.name))
    else:
        point, combo_point = result
        await ctx.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(member.name,point))
        if combo_point != 0:
            await ctx.channel.send("와! {:s}님이 전근으로 {:d}점을 얻었습니다!".format(member.name,combo_point))
    
    attendance_info = get_all_attendance_info()
    description = ""
    for index, info in enumerate(attendance_info):
        name = ctx.guild.get_member(info[0]).display_name
        msg = info[1]
        description += str(index+1) + ". " + name + ": " + msg + "\n"

    embed = discord.Embed(title="오늘의 날갱", description=markdown_escape(description))
    await ctx.channel.send(embed=embed)
    return

@client.command(name="점수")
async def point(ctx, arg=None):
    if arg == None: user = ctx.author
    else: user = await commands.MemberConverter().convert(ctx,arg)
    
    member = Member(user)
    
    if not member.exist_db():
        await ctx.channel.send("등록되지 않은 사용자입니다.")
        return
    
    await ctx.channel.send("{:s}님의 날갱점수는 {:d}점입니다. {:d}연속 출석 중입니다.".format(member.name, member.get_point(), member.get_combo()))
    return

@client.command(name="보내기")
async def give_point(ctx, user:discord.Member, point:int):
    if point <= 0: return
    
    member_send = Member(ctx.author)
    member_receive = Member(user)
    if not (member_send.exist_db() and member_receive.exist_db()):
        await ctx.channel.send("등록되지 않은 사용자입니다.")
        return

    if member_send.get_point() < point:
        await ctx.channel.send("점수가 부족합니다.")
        return

    member_send.give_point(member_receive, point)
    await ctx.channel.send("짜잔! {:s}님이 {:s}님에게 {:d}점을 선물했습니다.".format(member_send.mention(), member_receive.mention(), point))
    return

@client.command(name="순위표")
async def send_ranking(ctx):
    embed = discord.Embed(title="순위표", description=markdown_escape(scoreboard(ctx.author.guild)))
    await ctx.send(embed=embed)
    return

@client.command(name="도움")
async def help_message(ctx):
    await ctx.author.send("```"+\
            "기본\n"+\
            "!날갱 (인사말): 날갱하기\n"+\
            "!점수 : 내 점수 확인하기\n"+\
            "!점수 @멘션 : 멘션한 계정의 점수 확인하기\n"+\
            "!보내기 @멘션 점수 : 멘션한 계정으로 점수 보내기\n"+\
            "!순위표 : 점수 순위표 출력하기\n"+\
            "!도움 : 도움말\n"+\
            "\n"+\
            "날갱관리자 역할\n"+\
            "!강제날갱 @멘션 @멘션 : 멘션한 계정들을 날갱시키기\n"+\
            "!강제변경 @멘션 점수 콤보: 멘션한 계정의 점수와 콤보를 설정하기\n"+\
            "!초기화 : 날짜 초기화시키기\n"+\
            "!잠금 : 해당 날짜의 날갱을 막기\n"+\
            "\n"+\
            "NalgangAPIClient 역할\n"+\
            "!점수추가 @멘션 점수 : 계정의 점수를 입력한 점수만큼 추가하기\n"+\
            "\n"+\
            "깃허브 : https://github.com/3-24/nalgang\n"+\
            "```")
    return


@client.command(name="강제날갱")
@commands.has_role('날갱관리자')
async def force_nalgang(ctx):
    ids = ctx.message.raw_mentions
    for Id in ids:
        member = Member(ctx.guild.get_member(Id))
        result = member.nalgang("강제날갱")

        if result == None:
            await ctx.channel.send("{:s}님은 이미 날갱되었습니다.".format(member.name))
        else:
            point, combo_point = result
            await ctx.channel.send("{:s}님이 날갱해서 {:d}점을 얻었습니다!".format(member.name,point))
            if combo_point != 0:
                await ctx.channel.send("와! {:s}님이 전근으로 {:d}점을 얻었습니다!".format(member.name,combo_point))
    return

@client.command(name="강제변경")
@commands.has_role('날갱관리자')
async def force_setup(ctx, user : discord.Member, point, combo):
    member = Member(user)
    prev_point = member.get_point()
    prev_combo = member.get_combo()
    member.set_point(point)
    member.set_combo(combo)
    await ctx.send("{:s}'s point and combo changed: {:d}, {:d} -> {:d}, {:d}".format(member.name,prev_point, prev_combo, point, combo))
    return

@client.command(name="초기화")
@commands.has_role('날갱관리자')
async def force_day_reset(ctx):
    present_time = datetime.today()
    day_reset()
    time_save(present_time)
    await ctx.send("Successfully reset today's attendance list")
    return

@client.command(name="잠금")
@commands.has_role('날갱관리자')
async def force_lock(ctx):
    attendance_lock(ctx.author.guild)
    await ctx.send("Successfully locked today's attendance")
    return

@client.command(name="점수추가")
@commands.has_role('NalgangAPIClient')
async def api_point_add(ctx, user: discord.Member, delta:int):
    member = Member(user)
    prev_point = member.get_point()
    if (prev_point + delta < 0):
        await ctx.send("점수가 부족합니다.")
        return
    member.set_point(prev_point+delta)
    if (delta >= 0):
        await ctx.send(f"{user.display_name}에게 {delta}점이 추가되었습니다. 이제 {member.get_point()}점입니다.")
    else:
        await ctx.send(f"{user.display_name}이 {-delta}점 잃었습니다. 이제 {member.get_point()}점입니다.")
    return


def markdown_escape(string):
    return string.replace('_','\\_').replace('`','\\`').replace('*','\\*').replace('~','\\~')
