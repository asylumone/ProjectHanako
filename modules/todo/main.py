import core.lib as lib
from core.lib import YAMLProvider

author = "kiriharu"
name = "TODO"
description = '''ToDo module. Requires PyYAML
/todo ["new", "add", "create", "+"] {todo text} - Creates todo with {todo text}
/todo ["remove", "delete", "del", "-", "rm"] {id} - Removes todo with id. Id must be integer and >= 0
/todo ["todo", "list", "show"] - Prints todo's.
/todo ["help", "h"] - Prints this message.'''
version = "0.1"
command = "/todo"

moduledir = lib.Utils.modulepath("modules.todo.main")
logger = lib.Log("TODO")
todo = YAMLProvider(f"{moduledir}/todo.yml", type=[])


def handle(message, bot):
    args = message.text.split(" ")
    if len(args) == 1 or args[1] in ["todo", "list", "show"]:
        print_todo(message, bot)
    elif args[1] in ["new", "add", "create", "+"]:
        new_todo(message, bot)
    elif args[1] in ["remove", "delete", "del", "-", "rm"]:
        remove_todo(message, bot)
    elif args[1] in ["help", "h"]:
        help_todo(message, bot)
    else:
        bot.send_message(message.from_user.id, "Unknown command. Try /todo help")


def new_todo(message, bot):
    data = todo.load()
    todo_msg = str(' '.join(message.text.split(' ')[2:]))
    data.append(todo_msg)
    todo.save(data)
    logger.debug(f"Saved todo: {todo_msg}")
    bot.send_message(message.from_user.id, f"Saved: {todo_msg}")


def remove_todo(message, bot):
    data = todo.load()
    todo_id = int(message.text.split(" ")[2]) - 1
    if todo_id < 0 or todo_id >= len(data):
        bot.send_message(message.from_user.id, "Invalid todo index.")
    else:
        del data[todo_id]
        todo.save(data)
        logger.debug(f"Deleted todo with id {todo_id}")
        bot.send_message(message.from_user.id, f"Deleted todo with id {todo_id + 1}")


def print_todo(message, bot):
    data = todo.load()
    msg = ""
    for i, line in enumerate(data):
        msg += f"{i + 1}: {line}\n"
    if msg == "":
        bot.send_message(message.from_user.id, "Nothing in ToDo.")
    else:
        bot.send_message(message.from_user.id, f"{msg}")


def help_todo(message, bot):
    bot.send_message(message.from_user.id, f"<pre> {description} </pre>", parse_mode='html')
