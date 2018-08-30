from Alarm_bot.DataBase import Alarm
from Alarm_bot.base import session_factory

def save_alarm(alarm_from_bot):
    session = session_factory()
    alarm = Alarm(alarm_from_bot)
    session.add(alarm)
    session.commit()
    session.close()


def get_all_alarms():
    session = session_factory()
    alarm_query = session.query(Alarm)
    session.close()
    return alarm_query.all()

