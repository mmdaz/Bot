"""
resources that should be read :

http://docs.sqlalchemy.org/en/latest/core/engines.html#database-urls

"""

from sqlalchemy import *
from DataBase.base import Base


class DataBaseAlarm(Base):
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





class DataBaseDebt(Base):
    __tablename__ = 'debts'
    id = Column(Integer, primary_key=True)
    photo_id = Column(Integer)
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
        self.photo_id = debt.photo_id

    def __repr__(self):
        return "<Debt(card-number='%s', creditor-name='%s', amount='%s', date='%s', payment-status='%s', user-id='%s', photo_id='%d' )>" % (
            self.card_number, self.creditor_name, self.amount, self.date, self.payment_status, self.user_id , self.photo_id
        )

class Photo(Base):
    __tablename__ = 'photos'
    id = Column(Integer, primary_key=True)
    file_id = Column(String)
    access_hash = Column(String)
    name = Column(String)
    file_size = Column(String)
    mime_type = Column(String)
    thumb = Column(String)
    width = Column(Integer)
    height = Column(Integer)
    ext_width = Column(Integer)
    ext_height = Column(Integer)
    file_storage_version = Column(Integer)
    caption_text = Column(String)
    checksum = Column(String)
    algorithm = Column(String)

    def __init__(self, photo_message):
        self.file_id = photo_message.file_id
        self.access_hash = photo_message.access_hash
        self.name = photo_message.name
        self.file_size = photo_message.file_size
        self.mime_type = photo_message.mime_type
        self.thumb = photo_message.thumb
        self.width = photo_message.width
        self.height = photo_message.height
        self.ext_height = photo_message.ext_height
        self.ext_width = photo_message.ext_width
        self.file_storage_version = photo_message.file_storage_version
        self.caption_text = photo_message.caption_text.text
        self.checksum = photo_message.checksum
        self.algorithm = photo_message.algorithm
