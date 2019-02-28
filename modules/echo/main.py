author = "kiriharu"
name = "Echo bot"
description = '''Simple echo bot. Returns the message that was sent by user'''
version = '0.1'
command = '/echo'

def handle(text, message, bot):
    bot.reply_to(message, text)
