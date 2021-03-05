# This test is deprecated.
import unittest
from datetime import datetime, timedelta
from attendance import Member,c, table_init, is_day_changed
import random
import os,sqlite3
import config
from functools import wraps

if not os.path.exists("data"): os.makedirs("data")

def initdata(testfunc):
    @wraps(testfunc)
    def run_test_after_init(self):
        c.execute('''DROP TABLE IF EXISTS AttendanceTable''')
        c.execute('''DROP TABLE IF EXISTS Members''')
        c.execute('''DROP TABLE IF EXISTS AttendanceTimeCount''')
        table_init()
        return testfunc(self)
    return run_test_after_init

class TddTest(unittest.TestCase):
    @initdata
    def testDayReset(self):
        time1 = datetime(2020,5,7,hour=5,minute=59,second=59)
        time2 = datetime(2020,5,7,hour=6,minute=0,second=0)
        time3 = datetime(2020,5,7,hour=6,minute=0,second=1)
        update_time_delta = timedelta(hours=6, minutes=0)
        self.assertTrue(is_day_changed(time1,time2, update_time_delta))
        self.assertFalse(is_day_changed(time2,time3,update_time_delta))
    
    @initdata
    def testDatabase(self):
        m1 = Member(None)
        m1.id = 1
        m1.name = "Alice"
        m1.guild = 2222
        m1.add_db(point=123456, combo=654321)
        self.assertEqual(m1.get_point(),123456)
        self.assertEqual(m1.get_combo(),654321)
    
    @initdata
    def testNalgang(self):
        m1 = Member(None)
        m1.id = 1
        m1.guild = 2222
        m1.name = "Alice"
        m1.add_db()
        m1.nalgang("")
        self.assertEqual(m1.get_point(), config.point_by_rank[0])
        self.assertEqual(m1.get_combo(),1)
        self.assertIsNone(m1.nalgang(""))
    
    @initdata
    def testNalgangWeekBonus(self):
        m1 = Member(None)
        m1.id = 1
        m1.name = "Alice"
        m1.guild = 2222
        m1.add_db(combo=6)
        m1.nalgang("")
        self.assertEqual(m1.get_point(),config.point_by_rank[0]+config.week_bonus)
        self.assertEqual(m1.get_combo(),7)
    
    @initdata
    def testNalgangMonthBonus(self):
        m1 = Member(None)
        m1.id = 1
        m1.name = "Alice"
        m1.guild = 2222
        m1.add_db(combo=29)
        m1.nalgang("")
        self.assertEqual(m1.get_point(),config.point_by_rank[0]+config.month_bonus)
        self.assertEqual(m1.get_combo(),30)
    
    @initdata
    def testNalgangDayReset(self):
        m1 = Member(None)
        m1.id = 1
        m1.name = "Alice"
        m1.guild = 2222
        m1.add_db()
        m1.nalgang("")
        self.assertEqual(m1.get_point(), config.point_by_rank[0])
        self.assertEqual(m1.get_combo(), 1)
        time1 = datetime.today() + timedelta(days=1)
        m1.nalgang("", time1)
        self.assertEqual(m1.get_point(), config.point_by_rank[0]*2)
        self.assertEqual(m1.get_combo(), 2)
        time2 = datetime.today() + timedelta(days=2)
        m1.nalgang("", time2)
        self.assertEqual(m1.get_point(), config.point_by_rank[0]*3)
        self.assertEqual(m1.get_combo(), 3)
    
    @initdata
    def testNalgangPreciseDayReset(self):
        m1 = Member(None)
        m1.id = 1
        m1.guild = 2222
        m1.add_db()
        m1.name = "Alice"
        m1.nalgang("", datetime(2020,5,7,hour=5,minute=59,second=59))
        self.assertEqual(m1.get_point(), config.point_by_rank[0])
        self.assertEqual(m1.get_combo(), 1)
        m1.nalgang("", datetime(2020,5,7,hour=6,minute=00,second=00))
        self.assertEqual(m1.get_point(), config.point_by_rank[0]*2)
        self.assertEqual(m1.get_combo(), 2)
    
    @initdata
    def testNalgangGuildDependent(self):
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
        self.assertEqual(m1.get_point(), config.point_by_rank[0])
        self.assertEqual(m2.get_point(), config.point_by_rank[0])

    def tearDown(self):
        print("PASSED ")

if __name__ == '__main__':
    unittest.main(verbosity=2)