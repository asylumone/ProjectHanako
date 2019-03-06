import core.lib as lib
from core.lib import YAMLProvider
import re
from modules.mcrcon.rcon import McRcon

author = "kiriharu"
name = "MCRcon module"
description = '''This module can send messages to RCON minecraft port. '''
version = '0.1'
command = '/mcrcon'

logger = lib.Log('MCRcon')
moduledir = lib.Utils.modulepath("modules.mcrcon.main")
config = YAMLProvider(f"{moduledir}/config.yml", type={})


def handle(message, bot):
    args = message.text.split(" ")
    if args[1] in ["add", "+", "create", "new", "set"]:
        add_server(message, bot)
    if args[1] in ["remove", "-", "delete", "del"]:
        remove_server(message, bot)
    if args[1] in ["send", "push", "s", "call", "command"]:
        send_command(message, bot)


def add_server(message, bot):
    """Add server to the config. Usage: /mcrcon add servername host port password"""
    args = message.text.split(" ")
    try:
        data = config.load()
        data.update({args[2]: {
            "host": args[3],
            "port": args[4],
            "password": args[5]
        }})
    except IndexError:
        bot.send_message(message.from_user.id, "Not enough data. Check you message.")
    else:
        config.save(data)
        bot.send_message(message.from_user.id, f"Saved server {args[2]} with args: host = {args[3]}, "
        f"port = {args[4]}, password = {args[5]}")


def remove_server(message, bot):
    """Remove server from config. Usage: /mcrcon remove servername"""
    args = message.text.split(" ")
    try:
        data = config.load()
        del data[args[2]]
    except Exception as e:
        bot.send_message(message.from_user.id, f"Exception occured: {e}")
    else:
        config.save(data)
        bot.send_message(message.from_user.id, f"Successfully deleted {args[2]}")


def send_command(message, bot):
    """Send message to RCON. Usage: /mcrcon send servername command1 command_arg1 command_arg2..."""
    args = message.text.split(" ")
    try:
        data = config.load()
        server = data[args[2]]
        rconobj = McRcon(server['host'], int(server['port']), server['password'])
        resp = send(str(' '.join(message.text.split(' ')[3:])), rconobj)
        if resp:
            bot.send_message(message.from_user.id, resp)
    except KeyError:
        bot.send_message(message.from_user.id, f"Server {args[2]} not found in config.yml.")


def send(cmd, rcon):
    resp = rcon.command(cmd)
    if resp:
        return re.sub('§.', ' ', resp)
    rcon.disconnect()
