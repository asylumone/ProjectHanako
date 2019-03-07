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
                            HANDLERS[args]["handle"](message, self.bot)
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
    def load_modules():
        """Loading modules from module dir"""
        try:
            for importer, modname, ispkg in pkgutil.iter_modules(["modules"]):
                try:
                    HanakoModule.logger.debug(f"Found module {modname} (is module: {ispkg})")
                    isloaded = HanakoModule.load_module(modname)
                    if isloaded:
                        HanakoModule.logger.info(f"Loaded info for {modname}")
                except Exception as e:
                    HanakoModule.logger.error(f"While loading module {modname} exception occurred: {e}")
                    return False
        except Exception as e:
            HanakoModule.logger.error(f"While loading modules exception occurred: {e}")
        else:
            return True
        finally:
            HanakoModule.logger.debug(f"Ended loading handlers. Handlers: {HANDLERS.items()}")
            HanakoModule.logger.info("Modules loaded!")

    @staticmethod
    def get_modules():
        try:
            commandlist = list(HANDLERS.keys())
            loaded = []
            for module in commandlist:
                loaded.append(HANDLERS[module]['pkgname'])
        except Exception as e:
            HanakoModule.logger.error(f"Error while get modules: {e}")
            return []
        else:
            return {
                "loaded": loaded,
                "unloaded": config.module_ignorelist
            }

    @staticmethod
    def load_module(module):
        if module in config.module_ignorelist:
            HanakoModule.logger.debug(f"{module} module founded in ignore list, ignoring...")
            return False
        try:
            HANDLERS.update({
                str(getattr(modules, module).main.command): {
                    "handle": getattr(modules, module).main.handle,
                    "pkgname": module,
                    "name": getattr(modules, module).main.name,
                    "author": getattr(modules, module).main.author,
                    "description": getattr(modules, module).main.description,
                    "version": getattr(modules, module).main.version
                }
            })
        except Exception as e:
            HanakoModule.logger.error(f"While loading module {module} exception occurred: {e}")
            return False
        else:
            return True

    @staticmethod
    def remove_from_ignorelist(module):
        try:
            config.module_ignorelist.remove(module)
        except KeyError:
            return False
        else:
            return True

    @staticmethod
    def disable_module(command):
        try:
            config.module_ignorelist.append(HANDLERS[command]["pkgname"])
            HANDLERS.pop(command)
        except KeyError as e:
            HanakoModule.logger.error(f"Problems while trying to disable module: {e}")
            return False
        else:
            return True

    @staticmethod
    def get_module_info(command):
        return HANDLERS[command]

    @staticmethod
    def get_handlers():
        return HANDLERS


HANDLERS = {}

