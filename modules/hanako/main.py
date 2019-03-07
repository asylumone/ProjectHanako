from core import core
import core.lib as lib

author = "kiriharu"
name = "Hanako core module"
description = '''
This module allows you to manage modules in ProjectHanako
Commands: 

/hanako ["handlers", "get_handlers", "gethandlers", "gh"] - print HANDLERS param
/hanako ["modules", "get_modules", "getmodules", "gm"] - prints current loaded and unloaded modules
/hanako ["module_info", "get_module_info", "module", "gmi", "info"] /command - gives you info about module, what provide this command
/hanako ["reload", "restart", "reload_modules"] - reload modules
/hanako ["disable", "remove", "off"] /command - disable /command and module, what provide this command
/hanako ["rfi", "remove_from_ignorelist", "rmignore", "removeignore", "notignore"] modulename - remove module from ignorelist
/hanako ["load", "enable", "add", "on", "loadmodule", "load_module"] modulename - load module.
'''
version = '0.0.1'
command = '/hanako'

logger = lib.Log("Hanako manager")


def handle(message, bot):
    args = message.text.split(" ")
    logger.debug(f"Message: {args}")
    if len(args) == 1:
        bot.send_message(message.from_user.id, "Unknown command. Type /hanako help")
    elif args[1] in ["handlers", "get_handlers", "gethandlers", "gh"]:
        get_handlers(message, bot)
    elif args[1] in ["modules", "get_modules", "getmodules", "gm"]:
        get_modules(message, bot)
    elif args[1] in ["module_info", "get_module_info", "module", "gmi", "info"]:
        get_module_info(message, bot)
    elif args[1] in ["reload", "restart", "reload_modules"]:
        reload_modules(message, bot)
    elif args[1] in ["disable", "remove", "off"]:
        disable_module(message, bot)
    elif args[1] in ["rfi", "remove_from_ignorelist", "rmignore", "removeignore", "notignore"]:
        remove_from_ignorelist(message, bot)
    elif args[1] in ["load", "enable", "add", "on", "loadmodule", "load_module"]:
        load_module(message, bot)
    elif args[1] in ["help", "h", "givehelp", "hanako"]:
        bot.send_message(message.from_user.id, f"<pre> {description} </pre>", parse_mode='html')
    else:
        bot.send_message(message.from_user.id, "Unknown command. Type /hanako help")


def get_handlers(message, bot):
    bot.send_message(message.from_user.id, f"{core.HanakoModule.get_handlers()}")


def get_modules(message, bot):
    modules = core.HanakoModule.get_modules()
    loaded = ", ".join(modules['loaded'])
    unloaded = ", ".join(modules['unloaded'])
    bot.send_message(message.from_user.id, f"Get Modules:\nLoaded: {loaded}\nUnloaded: {unloaded}")


def get_module_info(message, bot):
    cmd = message.text.split(" ")[2]
    try:
        info = core.HanakoModule.get_module_info(cmd)
        text = f'''
Handle function: {str(info["handle"])}
PKGname: {info["pkgname"]}
Name: {info["name"]}
Author: {info["author"]}
Version: {info["version"]}

Description: {info["description"]}
        '''
    except KeyError:
        bot.send_message(message.from_user.id, f"No command found: {cmd}. Check logs.")
    else:
        bot.send_message(message.from_user.id, text)


def reload_modules(message, bot):
    state = core.HanakoModule.load_modules()
    logger.debug(f"State for reload_modules(): {state}")
    if state:
        bot.send_message(message.from_user.id, "Modules loaded.")
    else:
        bot.send_message(message.from_user.id, "Loading failed. Check logs.")


def disable_module(message, bot):
    cmd = message.text.split(" ")[2]
    state = core.HanakoModule.disable_module(cmd)
    logger.debug(f"State for disable_module(): {state}")
    if state:
        bot.send_message(message.from_user.id, f"Module {cmd} disabled successfully")
    else:
        bot.send_message(message.from_user.id, f"Something going wrong while trying to disable {cmd}"
                                               f". Check console.")


def remove_from_ignorelist(message, bot):
    module = message.text.split(" ")[2]
    state = core.HanakoModule.remove_from_ignorelist(module)
    logger.debug(f"State for remove_from_ignorelist(): {state}")
    if state:
        bot.send_message(message.from_user.id, f"Module {module} removed from ignore list")
    else:
        bot.send_message(message.from_user.id, f"Something going wrong while trying to remove from "
                                               f"ignore list {module} Check console.")


def load_module(message, bot):
    module = message.text.split(" ")[2]
    state = core.HanakoModule.load_module(module)
    logger.debug(f"State for load_module(): {state}")
    if state:
        bot.send_message(message.from_user.id, f"Module {module} loaded successfully")
    else:
        bot.send_message(message.from_user.id, f"Something going wrong while loading {module}."
                                               f" Check console.")
