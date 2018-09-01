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
    name = Column(String)
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
        return "<Alarm(name='%s', user_id='%s', photo_json='%s', message='%s', stop_message='%s', start_time='%s', repeat_period='%s', activation_status'%s')>" % (
            self.name, self.user_id, self.photo_json, self.message, self.stop_message, self.start_time, self.repeat_period, self.activation_status
        )





class Debt(Base):
    __tablename__ = 'debts'
    id = Column(Integer, primary_key=True)
    user_id = Column(String)
    creditor_name = Column(String)
    card_number = Column(String)
    amount = Column(String)
    date = Column(String)
    payment_status = Column(String)


    def __init__(self, debt):
        self.user_id = debt.user_id
        self.card_number = debt.card_number
        self.date = debt.date
        self.creditor_name = debt.creditor_name
        self.amount = debt.amount
        self.payment_status = debt.payment_status


    def __repr__(self):
        return "<Debt(card-number='%s', creditor-name='%s', amount='%s', date='%s', payment-status='%s', user-id='%s' )>" % (
            self.card_number, self.creditor_name, self.amount, self.date, self.payment_status, self.user_id
        )
