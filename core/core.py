import core.lib as lib
import core.config as config
import telebot
import modules
import traceback
import os
import pkgutil


class Core:
    def __init__(self, token):
        self.logger = lib.Log(name=config.name)
        self.bot = telebot.TeleBot(token)

    def handler(self, messages):
        """Handler for messages"""
        for message in messages:
            if message.from_user.id in config.users:
                if message.text:  # if message is command...
                    try:
                        self.logger.info(f"{message.from_user.id} sended command: {message.text}")
                        args = message.text.split(" ")[0]
                        if args in HANDLERS:
                            HANDLERS[args](message, self.bot)
                        else:
                            self.logger.info(f"{message.from_user.id} sended unknown command: {message.text}")
                            self.bot.send_message(message.from_user.id, "Unknown command.")
                    except Exception:
                        self.logger.error(traceback.format_exc())
            else:
                self.logger.warning(f"{message.text} from unauthorized {message.from_user.id}")

    def polling(self):
        """Telegram bot polling"""
        self.logger.info("Setting update listener")
        self.bot.set_update_listener(self.handler)
        self.bot.polling()

    def start(self):
        """Start bot (call load_modules() and polling() methods"""
        self.logger.info(f"Starting loading ProjectHanako v {config.version}. Current name: {config.name}")
        self.logger.debug(config.loadingfiglet)
        self.logger.debug(f"Current settings: Users - {config.users}, Telegram bot token - "
                          f"{config.tg_token}, logfile - {config.logfile}")
        HanakoModule.load_modules()
        if config.proxy:
            self.logger.debug(f"Loading proxy {config.proxy}")
            telebot.apihelper.proxy = config.proxy
        else:
            self.logger.debug("Loading without proxy.")
        self.polling()


class HanakoModule:
    """Module for manage HanakoProject"""

    logger = lib.Log(name="Hanako Module")

    @staticmethod
    def handler(message, bot):

        """Message handler"""
        command = message.text.split(" ")[1]
        if len(command) == 1:
            bot.send_message(message.from_user.id, "Sended empty message.")
        elif command == "get_modules":
            HanakoModule.get_modules(message, bot)
        elif command == "disable_module":
            HanakoModule.disable_module(message, bot)
        elif command == 'load_modules':
            HanakoModule.load_modules()
        elif command == 'get_module_info':
            HanakoModule.get_module_info(message, bot)
        else:
            bot.send_message(message.from_user.id, "Sended unknown message")

    @staticmethod
    def load_modules():
        #  TODO: Rewrite
        """Loading modules from module dir"""
        try:
            for importer, modname, ispkg in pkgutil.iter_modules(["modules"]):
                try:
                    HanakoModule.logger.debug(f"Found module {modname} (is module: {ispkg})")
                    if modname in config.module_ignorelist:
                        HanakoModule.logger.debug(f"{modname} module founded in ignore list, ignoring...")
                    else:
                        HANDLERS.update({str(getattr(modules, modname).main.command): getattr(modules, modname).main.handle})
                        HanakoModule.logger.info(f"Loaded handler for {modname}")
                except Exception as e:
                    HanakoModule.logger.error(f"While loading module {modname} exception occurred: {e}")
        except Exception as e:
            HanakoModule.logger.error(f"While loading modules exception occurred: {e}")
        finally:
            HanakoModule.logger.debug(f"Ended loading handlers. Handlers: {HANDLERS.items()}")
            HanakoModule.logger.info("Modules loaded!")

    @staticmethod
    def get_modules(message, bot):
        """Returns loaded modules"""
        modules = "Loaded modules: \n"
        for module in HANDLERS.keys():
            modules += module + "\n"
        modules += "Unloaded or ignored modules: \n"
        for module in config.module_ignorelist:
            modules += module + "\n"
        print(config.module_ignorelist)
        bot.send_message(message.from_user.id, modules)

    @staticmethod
    def disable_module(message, bot):
        """Remove modules from HANDLER"""
        module = message.text.split(" ")[2]
        try:
            del HANDLERS[module]
            config.module_ignorelist.append(module[1::])
        except KeyError:
            bot.send_message(message.from_user.id, f"No module found {module}")
            HanakoModule.logger.error(f"No module found {module}")
        else:
            bot.send_message(message.from_user.id, f"Removed {module}")

    @staticmethod
    def get_module_info(message, bot):
        module = message.text.split(" ")[2]
        try:
            info = f'''
            Name: {str(getattr(modules, module).main.name)}\n
Author: {str(getattr(modules, module).main.author)}\n
Command: {str(getattr(modules, module).main.command)}\n
Descriprion: {str(getattr(modules, module).main.description)}\n
Version: {str(getattr(modules, module).main.version)}'''
            bot.send_message(message.from_user.id, info)
        except Exception:
            HanakoModule.logger.error(traceback.format_exc())


HANDLERS = {"/hanako": HanakoModule.handler, }
