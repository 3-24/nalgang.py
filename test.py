import unittest
from bot import is_day_changed
from datetime import datetime, timedelta
from attendance import Member,c
import random
import access_data
import os,sqlite3
import config
from functools import wraps

if not os.path.exists("data"): os.makedirs("data")

def initdata(testfunc):
    @wraps(testfunc)
    def run_test_after_init(self):
        c.execute('''DROP TABLE IF EXISTS AttendanceTable''')
        c.execute('''DROP TABLE IF EXISTS Members''')
        c.execute('''CREATE TABLE IF NOT EXISTS Members (id integer, point integer, combo integer)''')
        c.execute('''CREATE TABLE IF NOT EXISTS AttendanceTable (id integer, message nvarchar)''')
        try: os.remove("./data/attendance_count.data")
        except FileNotFoundError: pass
        try: os.remove("./data/attendance_time.data")
        except FileNotFoundError: pass
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
        m1.id_num = 1
        m1.name = "Alice"
        m1.add_db(point=123456, combo=654321)
        self.assertEqual(m1.get_point(),123456)
        self.assertEqual(m1.get_combo(),654321)
    
    @initdata
    def testNalgang(self):
        m1 = Member(None)
        m1.id_num = 1
        m1.name = "Alice"
        m1.add_db()
        m1.nalgang("")
        self.assertEqual(m1.get_point(),config.point_by_rank[0])
        self.assertEqual(m1.get_combo(),1)
        self.assertIsNone(m1.nalgang(""))
    
    @initdata
    def testNalgangWeekBonus(self):
        m1 = Member(None)
        m1.id_num = 1
        m1.name = "Alice"
        m1.add_db(combo=6)
        m1.nalgang("")
        self.assertEqual(m1.get_point(),config.point_by_rank[0]+config.week_bonus)
        self.assertEqual(m1.get_combo(),7)
    
    @initdata
    def testNalgangMonthBonus(self):
        m1 = Member(None)
        m1.id_num = 1
        m1.name = "Alice"
        m1.add_db(combo=29)
        m1.nalgang("")
        self.assertEqual(m1.get_point(),config.point_by_rank[0]+config.month_bonus)
        self.assertEqual(m1.get_combo(),30)
    
    def tearDown(self):
        print("PASSED ")

if __name__ == '__main__':
    unittest.main(verbosity=2)