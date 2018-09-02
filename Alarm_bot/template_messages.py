from balebot.models.messages import TextMessage


class Message():
    INVALID_INPUT = TextMessage("ورودی اشتباه است ... لطفا دوباره وارد کنید ")
    GET_ALARM_NAME = TextMessage("سلام و وقت بخیر :) لطفا نام هشدار را وارد نمایید :")
    GET_ALARM_MESSAGE = TextMessage("لطفا پیام هشدار را وارد کنید :")
    GET_ALARM_STOP_MESSAGE = TextMessage("لطفا یک پیام را برای متوقف کردن هشدار ارسال نمایید (یعنی اگر شما آن پیام را ارسال نمایید آن هشدار متوقف خوهاد شد)")
    GET_ALARM_PHOTO =TextMessage("یک عکس برای هشدار ارسال نمایید :")
    GET_ALARM_YEAR = TextMessage("زمان هشدار : لطفا سال هشدار را وارد نمایید : برای مثال : ‌1397")
    GET_ALARM_MONTH = TextMessage("لطفا ماه هشدار را وارد نمایید : ")
    GET_ALARM_DAY = TextMessage("لطفا روز هشدار را وارد نمایید : ")
    GET_ALARM_HOUR = TextMessage("لطفا ساعت هشدار را وارد نمایید :")
    GET_ALARM_MINUTE = TextMessage("لطفا دقیقه هشدار را وارد نمایید :")
    GET_ALARM_REPETITION_PERIOD = TextMessage("لطفا زمان تکرار هشدار را وارد نمایید (هشدار چند دقیقه یک بار تکرار شود ؟)")
    ALARM_CREATION_SUCCESS = TextMessage("هشدار با موفقیت ساخته شد ... :)")
    GET_DEBT_AMOUNT = TextMessage("ثبت بدهی ::: لطفا مبلغ را وارد نمایید :")
    GET_DEBT_CARD_NUMBER = TextMessage("لطفا شماره کارت مقصد را وارد نمایید :")
    GET_CREDITOR_NAME = TextMessage("لطفا نام شخصی که به او بدهکار هستید را وارد نمایید :")
    GET_DEBT_YEAR = TextMessage("تاریخ بدهی : لطفا سال را وارد نمایید (برای مثال 1397 ) :")
    GET_DEBT_MONTH = TextMessage("لطفا ماه را وارد نمایید :")
    GET_DEBT_DAY = TextMessage(" لطفا روز را وارد نمایید : ")
    DEBT_CREATION_SECCESS = TextMessage("بدهی ثبت شد .")
    STOP_MESSAGE_REPETIOTION = TextMessage("این پیام هشدار متعلق به یکی از هشدار های قبلیتان است . لطفا پیام دیگری وارد نمایید :")
