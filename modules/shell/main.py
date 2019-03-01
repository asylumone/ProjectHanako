import modules.shell.config as config
import core.lib as lib
import subprocess

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


def handle(message, bot):
    # TODO: Add restricted commands
    try:
        args = message.text.split(" ")
        output = shellcommand(' '.join(args[1:]))
        logger.info(f"{message.from_user.id} executed {message.text}: {output}")
        if output:
            bot.reply_to(message, output)
        else:
            bot.reply_to(message, "Empty output")
    except CommandCheckError:
        logger.warning("Shell access is not true")
        bot.reply_to(message, "Shell access is not true")
    except CallException as e:
        logger.error(f"{message.from_user.id} try to use {message.text} but exception occurred: {e}")
        bot.reply_to(message, e)


def shellcommand(command):
    if config.shell:
        try:
            output = subprocess.check_output([command], encoding='UTF-8', shell=True,
                                             stderr=subprocess.STDOUT)
            return output
        except subprocess.CalledProcessError as e:
            raise CallException(e.output)
    else:
        raise CommandCheckError("Shell access is not True.")
