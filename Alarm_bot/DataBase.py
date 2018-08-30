"""
resources that should be read :

http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls

"""

from sqlalchemy import *
from Alarm_bot.base import Base

class Alarm(Base):
    __tablename__ = 'alarms'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    photo_json = Column(String)
    message = Column(String)
    stop_message = Column(String)
    start_time = Column(String)
    repeat_period = Column(String)
    activation_status = Column(String)


    def __init__(self, alarm ):
        self.user_id = alarm.user_id
        self.name = alarm.name
        self.message = alarm.message
        self.photo_json = alarm.photo
        self.stop_message = alarm.stop_message
        self.start_time = alarm.start_time
        self.repeat_period = alarm.repeat_period
        self.activation_status = str(alarm.activation_status)


    def __repr__(self):
        return "<Alarm(user_id='%s', photo_json='%s', message='%s', stop_message='%s', start_time='%s', repeat_period='%s', activation_status'%s')>" % (
            self.user_id, self.photo_json, self.message, self.stop_message, self.start_time, self.repeat_period, self.activation_status
        )




