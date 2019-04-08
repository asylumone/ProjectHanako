from modules.flibusta_search.flibusta_api import Flibusta, load_config
from os import remove
from time import sleep
from threading import Thread

author = "cmd410"
name = "Flibusta search"
description = '''Flibusta search query'''
version = '0.0'
command = '/book' 


module_path = __file__[:__file__.rfind('\\')+1]
book_choice = {}
config = load_config(module_path+'config.txt')

def cleanup(filename):
    sleep(5)
    remove(filename)
    print(f'file removed <{filename}>')

def handle(message, bot):
    bookname = message.text.replace('/book', '').strip()
    if bookname.isdigit():
        book_num = int(bookname)-1
        if -1<book_num<(config['book_limit']+1):
            try:
                book = book_choice[message.from_user.id][book_num]
                print(f'sending book {book["title"]}')
                filename = book.load_book(str(message.from_user.id))
                if filename != 'book blocked':
                    with open(filename, 'rb') as bookfile:
                        bot.send_document(message.chat.id, bookfile)
                    del book_choice[message.from_user.id]
                    Thread(target=cleanup,args=[filename]).start()
                else:
                    bot.reply_to(message, 'К сожалению эта книга заблокирована по требованию правообладателя.')
            except KeyError:
                pass
    else:
        flint = Flibusta(config=config)
        booklist = flint.make_book_list(title=bookname, limit=config['book_limit'])
        if len(booklist)<1:
            bot.reply_to(message, 'Похоже нет книги с таким названием..')
        else:
            book_choice[message.from_user.id] = booklist
            count = 1
            for book in booklist:
                bot.reply_to(message, str(count)+'. '+book.make_string())
                count+=1