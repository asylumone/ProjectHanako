<h2>ProjectHanako – modular Telegram bot and your personal assistant.</h2>

Modular system implemented in this project allows for writing modules for various needs. 
Also, Bot already has under a dozen modules for various tasks: from TODO manager to MPD server control module.

<h3>Setup and launch</h3>
1. Clone repository or download and unpack an archive:

```
git clone https://github.com/asylumone/ProjectHanako.git
```

2.  Install dependencies:

```
pip3 install -r requirments.txt
```

3. In core/config.py change settings for your needs. By default – Bot token and user id.

```
tg_token = "our Token here"
users = [here ids of users, who have access to bot]
```

To find out user ID you should write something to bot, check out logs and copy the needed id.
<h3>PyTelegramBotApi</h3>
Bot uses <a href=https://github.com/eternnoir/pyTelegramBotAPI>pyTelegramBotAPI<a> for simplified module creation. <br>
We will probably write our own library some day, but for now its the best choice. I guess.

<h3>Module Creation</h3>

On Bot startup method ` HanakoModule.load_modules() ` is executed, this method lists modules directory and if it finds a module – tries to load it. 

File `__init__.py` indicates that a directory is a module.

Afterwards, it tries to load main.py, which MUST contain such variables as `name, author, description, version, command`. All of them are required.

`pkgname` is taken from module directory name, and `handle` from function `handle(message, bot)` in `main.py` of module.

Looking at `Core.handler` code, t appears easily understandable, that when text begining with `command`, is detected, variables message and bot are passed to handle function of module associated with command.

<h5>Module structure on the example of echo:</h5>

```
ProjectHanako/modules$ tree echo/

echo/
├── __init__.py
└── main.py
```

```
__init__.py – indicates that directory is a module
main.py – main file of module
Other files can be added. See other modules to figure out how its done.
```

<h5>Code main.py on the example of echo:</h5>

```python
author = "kiriharu" #  Author
name = "Echo bot" #  Name
description = '''Simple echo bot. Returns the message that was sent by user''' #  Description
version = '0.1' #  Version
command = '/echo' #  Trigger command


def handle(message, bot): #  Main function
    bot.reply_to(message, message.text) #  Reply to message with message.text
    # This module simply sends back a recieved message 
    # If we write /echo test, ‘/echo test’ will be returned. It's simple!
```