# Bot Developing tutorial and my experiences .

This is my personal project to learning of bot developing and can be a simple tutorial.


## Getting Started

At the first you need to khow python basic syntaxis and basic database kowledge for bots that needs to save information.

I am a botdeveloper at Bale Messanger now and in this project I use balebot module for python to create bot in Bale :)

### Prerequisites

So you should install balebot module with pip :

```
pip install balebot
```

You can use any database for your bot and I use postgresql and sqlallchemy (a good module for sql base databases for python). 
Because of this we need to install this with these commands :

```
pip install sqlalchemy
pip install ORM
```

and also you should declare your bot in @botfather at Bale and get token of 
it.

After getting token lets start create a bot :)

At fisrt we must create an updater object from balebot SDK:

```
from balebot.updater import Updater

updater = Updater(token="our token")
```
The duty of Updater class is transfering updates between your bot and botserver.

