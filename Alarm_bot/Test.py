import datetime
import asyncio
from balebot.handlers import *
from balebot.filters import *
from balebot.models.messages import *
from balebot.updater import Updater
from Alarm_bot.Alarm import Alarm


# date1 = datetime.datetime(2018, 8, 28)
# date2 = datetime.datetime(2018, 8, 28)
#
# print(date1 == date2)
# is True

# print(create_time(2018, 2, 25, 12, 52, 23))

updater =  Updater(token="63d52735b75ff858191152a038d746b956ef950e", loop=asyncio.get_event_loop())
dispatcher = updater.dispatcher


p = PhotoMessage.load_from_json({"$type": "Document", "fileId": "-1577737613206681854", "accessHash": "1314892980", "fileSize": "282672", "name": "cars-3-1366x768-lightning-mcqueen-cruz-ramirez-pixar-animation-4k-10754.jpg", "mimeType": "image/jpeg", "thumb": {"width": 90, "height": 50, "thumb": "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"}, "ext": {"$type": "Photo", "width": 1366, "height": 768}, "caption": {"$type": "Text", "text": ""}, "checkSum": "checksum", "algorithm": "algorithm", "fileStorageVersion": 1}
)


