import core.lib as lib
import core.config as config
import telebot
import modules
import traceback
import os
import pkgutil

VERSION = "0.1 indev"

CURRENT_MODULE = ""
HANDLERS = {}


class Core:
    def __init__(self, token):
        self.logger = lib.Log(name=config.name)
        self.bot = telebot.TeleBot(token)
        self.current_module = CURRENT_MODULE

    def handler(self, messages):
        for message in messages:
            if message.from_user.id in config.users:
                if '/' == message.text[0]:
                    self.current_module = message.text[1::].split(" ")[0]
                    try:
                        self.logger.info(f"{message.text} from {message.from_user.id}")
                        args = message.text.split(" ")[0]
                        if args in HANDLERS:
                            HANDLERS[args](message.text, message, self.bot)
                    except Exception as e:
                        self.logger.error(f"Error occured while trying to load module: {e}")
                        self.logger.error(traceback.format_exc())
            else:
                self.logger.warning(f"{message.text} from unauthorized {message.from_user.id}")

    def polling(self):
        self.logger.info("Setting update listener")
        self.bot.set_update_listener(self.handler)
        self.bot.polling()

    def load_modules(self):
        try:
            for importer, modname, ispkg in pkgutil.iter_modules(["modules"]):
                try:
                    self.logger.debug(f"Found module {modname} (is module: {ispkg})")
                    HANDLERS.update({str(getattr(modules, modname).main.command): getattr(modules, modname).main.handle})
                    self.logger.info(f"Loaded handler for {modname}")
                except Exception as e:
                    self.logger.info(f"While loading module {modname} exception occurred: {e}")
        except Exception as e:
            self.logger.info(f"While loading modules exception occurred: {e}")
        finally:
            self.logger.debug(f"Ended loading handlers. Handlers: {HANDLERS.items()}")
            self.logger.debug("Modules loaded!")

    def start(self):
        self.logger.info(f"Starting loading ProjectHanako v {VERSION}. Current name: {config.name}")
        self.logger.debug(config.loadingfiglet)
        self.logger.debug(f"Current settings: Users - {config.users}, Telegram bot token - {config.tg_token}, logfile - {config.logfile}")
        self.load_modules()
        self.polling()
