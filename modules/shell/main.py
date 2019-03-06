import modules.shell.config as config
import core.lib as lib
import subprocess
from telebot import util

author = "kiriharu"
name = "Shell module"
description = '''This module execute shell commands. Use with caution! '''
version = '0.1'
command = '/shell'

logger = lib.Log('Shell Module')


class CommandCheckError(Exception):
    pass


class CallException(Exception):
    pass


class RestrictedCommandException(Exception):
    pass


def handle(message, bot):
    try:
        args = message.text.split(" ")
        output = shell_command(' '.join(args[1:]))
        logger.info(f"{message.from_user.id} executed {message.text}")
        if output:
            try:
                bot.reply_to(message, output)
            except:
                splited_text = util.split_string(output, 3000)
                for text in splited_text:
                    bot.send_message(message.from_user.id, text)
        else:
            bot.reply_to(message, "Empty output")
    except CommandCheckError:
        logger.warning("Shell access is not true")
        bot.reply_to(message, "Shell access is not true")
    except CallException as e:
        logger.error(f"{message.from_user.id} try to use {message.text} but exception occurred: {e}")
        bot.reply_to(message, e)
    except RestrictedCommandException:
        bot.reply_to(message, "Command restricted.")


def shell_command(cmd):
    if config.shell:
        try:
            args = cmd.split(" ")
            for part in args:
                if part in config.restrictedArgs:
                    logger.warning(f"Found restricted part in command: {part}. Full command: {cmd}")
                    raise RestrictedCommandException
            output = subprocess.check_output([cmd], encoding='UTF-8', shell=True,
                                             stderr=subprocess.STDOUT)
            return output
        except subprocess.CalledProcessError as e:
            raise CallException(e.output)
    else:
        raise CommandCheckError("Shell access is not True.")
