from Alarm_bot.database_operations import *
import time
import jdatetime
from Alarm_bot.template_messages import Message

# date = jdatetime.datetime.now()
# s = "1397:6:2:2:2"
# s_l = s.split(":")
# print(s_l)
# print(date)
# if date.month == int(s_l[1]):
#     print("salam")


# for alarm in session_factory().query(Alarm).order_by(Alarm.id):
#     print(alarm.start_time)

def t1():
    while 1:
        print("t1")
        time.sleep(2)

def t2():
    while 1:
        print("t2")
        time.sleep(2)

# a = get_all_alarms()[0]
# print(get_all_alarms()[2])
# delete_alarm(a)
# a = Alarm.Alarm()

# print(search_alarm_for_send(jdatetime.datetime(1397, 6, 9, 23, 1 )))
a = get_all_alarms()[0]

print(check_stop_message_repetition(a.user_id, "stop-messag"))