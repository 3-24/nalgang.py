from datetime import datetime, timedelta
from attendance import Member, c, table_init, is_day_changed
import os
import config
from functools import wraps


def initdata(testfunc):
    @wraps(testfunc)
    def run_test_after_init():
        c.execute('''DROP TABLE IF EXISTS AttendanceTable''')
        c.execute('''DROP TABLE IF EXISTS Members''')
        c.execute('''DROP TABLE IF EXISTS AttendanceTimeCount''')
        table_init()
        return testfunc()
    return run_test_after_init


@initdata
def test_day_reset():
    time1 = datetime(2020, 5, 7, hour=5, minute=59, second=59)
    time2 = datetime(2020, 5, 7, hour=6, minute=0, second=0)
    time3 = datetime(2020, 5, 7, hour=6, minute=0, second=1)
    update_time_delta = timedelta(hours=6, minutes=0)
    assert(is_day_changed(time1, time2, update_time_delta))
    assert(not is_day_changed(time2, time3, update_time_delta))


@initdata
def test_database():
    m1 = Member(None)
    m1.id = 1
    m1.name = "Alice"
    m1.guild = 2222
    m1.add_db(point=123456, combo=654321)
    assert(m1.get_point() == 123456)
    assert(m1.get_combo() == 654321)


@initdata
def test_nalgang():
    m1 = Member(None)
    m1.id = 1
    m1.guild = 2222
    m1.name = "Alice"
    m1.add_db()
    m1.nalgang("")
    assert(m1.get_point() == config.point_by_rank[0])
    assert(m1.get_combo() == 1)
    assert(m1.nalgang("") is None)


@initdata
def test_nalgang_week_bonus():
    m1 = Member(None)
    m1.id = 1
    m1.name = "Alice"
    m1.guild = 2222
    m1.add_db(combo=6)
    m1.nalgang("")
    assert (m1.get_point() == config.point_by_rank[0]+config.week_bonus)
    assert (m1.get_combo() == 7)


@initdata
def test_nalgang_month_bonus():
    m1 = Member(None)
    m1.id = 1
    m1.name = "Alice"
    m1.guild = 2222
    m1.add_db(combo=29)
    m1.nalgang("")
    assert(m1.get_point() == config.point_by_rank[0]+config.month_bonus)
    assert(m1.get_combo() == 30)


@initdata
def test_nalgang_day_reset():
    m1 = Member(None)
    m1.id = 1
    m1.name = "Alice"
    m1.guild = 2222
    m1.add_db()
    m1.nalgang("")
    assert(m1.get_point() == config.point_by_rank[0])
    assert(m1.get_combo() == 1)
    time1 = datetime.today() + timedelta(days=1)
    m1.nalgang("", time1)
    assert(m1.get_point() == config.point_by_rank[0]*2)
    assert(m1.get_combo() == 2)
    time2 = datetime.today() + timedelta(days=2)
    m1.nalgang("", time2)
    assert(m1.get_point() == config.point_by_rank[0]*3)
    assert(m1.get_combo() == 3)


@initdata
def test_nalgang_day_rest_precise():
    m1 = Member(None)
    m1.id = 1
    m1.guild = 2222
    m1.add_db()
    m1.name = "Alice"
    m1.nalgang("", datetime(2020, 5, 7, hour=5, minute=59, second=59))
    assert(m1.get_point() == config.point_by_rank[0])
    assert(m1.get_combo() == 1)
    m1.nalgang("", datetime(2020, 5, 7, hour=6, minute=00, second=00))
    assert(m1.get_point() == config.point_by_rank[0]*2)
    assert(m1.get_combo() == 2)


@initdata
def test_nalgang_guild_dependent():
    m1 = Member(None)
    m1.id = 1
    m1.name = "Alice"
    m1.guild = 2222
    m1.add_db()
    m2 = Member(None)
    m2.id = 1
    m2.name = "Alice"
    m2.guild = 2223
    m2.add_db()
    m1.nalgang("")
    m2.nalgang("")
    assert(m1.get_point() == config.point_by_rank[0])
    assert(m2.get_point() == config.point_by_rank[0])
