from Alarm_bot.DataBase import Alarm, Debt
from Alarm_bot.base import session_factory
import jdatetime

def save_alarm(alarm_from_bot):
    session = session_factory()
    alarm = Alarm(alarm_from_bot)
    session.add(alarm)
    session.commit()
    session.close()

def save_debt(debt_from_bot):
    session = session_factory()
    debt = Debt(debt_from_bot)
    session.add(debt)
    session.commit()
    session.close()


def get_all_alarms():
    session = session_factory()
    alarm_query = session.query(Alarm)
    session.close()
    return alarm_query.all()

def get_all_debts():
    session = session_factory()
    debt_query = session.query(Debt)
    session.close()
    return debt_query.all()


def search_stop_message(user_id, input_message):
    session = session_factory()
    for id , stop_message in session.query(Alarm.user_id, Alarm.stop_message):
        if id == user_id and stop_message == input_message:
            return True
    return False


def update_database(user_id, input_stop_message):
    session = session_factory()
    alarm = session.query(Alarm).filter_by(user_id=user_id, stop_message=input_stop_message).all()
    print(alarm[0].message)


def delete_alarm(alarm):
    session = session_factory().object_session(alarm)
    session.delete(alarm)
    session.commit()


def search_alarm_for_send(current_time):
        result_list=[]

        for alarm in get_all_alarms():
            alarm_time = alarm.start_time.split(":")
            print(alarm_time)
            if int(alarm_time[0]) == current_time.year and int(alarm_time[1]) == current_time.month and int(alarm_time[2]) == current_time.day and int(alarm_time[3]) == current_time.hour and int(alarm_time[4]) == current_time.minute:
                result_list.append(alarm.user_id)

        return result_list


