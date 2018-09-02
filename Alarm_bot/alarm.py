

class Alarm:

    def __init__(self, name, user_id, photo, message, stop_message, start_time, repeat_period, activation_satatus):

        self.name = str(name)
        self.user_id = str(user_id)
        self.photo = str(photo)
        self.message = str(message)
        self.stop_message = str(stop_message)
        self.start_time = str(start_time)
        self.repeat_period = str(repeat_period)
        self.activation_status = str(activation_satatus)


    def start_alarm(self):
        self.activation_status = True



    def stop_alarm(self):
        self.activation_status = False


    def send_alarm(self):
        pass