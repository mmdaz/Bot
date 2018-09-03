from Alarm_bot.DataBase import Alarm, Debt
from Alarm_bot.base import session_factory
import jdatetime
from balebot.models.messages import TextMessage

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
    session.expire_on_commit = False
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




def delete_alarm(alarm):
    session = session_factory().object_session(alarm)
    session.delete(alarm)
    session.commit()


def search_alarm_for_send(current_time):
        result_list=[]

        for alarm in get_all_alarms():
            alarm_time = alarm.start_time.split(":")
            print(alarm_time)
            if int(alarm_time[0]) == current_time.year and int(alarm_time[1]) == current_time.month and int(alarm_time[2]) == current_time.day and int(alarm_time[3]) == current_time.hour and int(alarm_time[4]) == current_time.minute and str(alarm.activation_status) == "true":
                result_list.append(alarm)

        return result_list



def update_alarm_time(alarm):
    session = session_factory().object_session(alarm)
    target_alarm = session.query(Alarm).filter_by(id=alarm.id).first()
    temp_time = target_alarm.start_time.split(":")
    date_time = jdatetime.datetime(int(temp_time[0]), int(temp_time[1]), int(temp_time[2]), int(temp_time[3]), int(temp_time[4]))
    date_time = date_time + jdatetime.timedelta(minutes=int(alarm.repeat_period))
    target_alarm.start_time = "{}:{}:{}:{}:{}".format(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute)
    session.commit()
    session.close()


def update_alarm_activation(user_id, stop_message):
    session = session_factory()
    target_alarm = session.query(Alarm).filter_by(user_id=user_id, stop_message=stop_message).first()
    session = session.object_session(target_alarm)
    deactive_message = TextMessage("هشدار {} متوقف شد .".format(target_alarm.name))
    if target_alarm.activation_status == "true":
        target_alarm.activation_status = False
        session.commit()
        session.close()

    return deactive_message





def check_stop_message_repetition(user_id, stop_message):
    session = session_factory()
    target_alarms = session.query(Alarm).filter_by(user_id=user_id)
    for alarm in target_alarms:
        if alarm.stop_message == stop_message:
            return True
    return False

