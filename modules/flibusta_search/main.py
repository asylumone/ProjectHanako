from modules.flibusta_search.flibusta_api import Flibusta
from os import remove
from time import sleep
from threading import Thread

author = "cmd410"
name = "Flibusta search"
description = '''Flibusta search query'''
version = '0.0'
command = '/book' 

book_choice = {}
max_books_shown = 3

def cleanup(filename):
    sleep(5)
    remove(filename)
    print(f'file removed <{filename}>')

def handle(message, bot):
    bookname = message.text.replace('/book', '').strip()
    if bookname.isdigit():
        book_num = int(bookname)-1
        if -1<book_num<(max_books_shown+1):
            try:
                book = book_choice[message.from_user.id][book_num]
                print(f'sending book {book["title"]}')
                filename = book.load_book('fb2',str(message.from_user.id))
                with open(filename, 'rb') as bookfile:
                    bot.send_document(message.chat.id, bookfile)
                del book_choice[message.from_user.id]
                Thread(target=cleanup,args=[filename]).start()
            except KeyError:
                pass
    else:
        flint = Flibusta()
        booklist = flint.make_book_list(title=bookname)
        while len(booklist) > max_books_shown:
            booklist.pop()

        
        if len(booklist)<1:
            bot.reply_to(message, 'Похоже нет книги с таким названием..')
        else:
            book_choice[message.from_user.id] = booklist
            for book in booklist:
                bot.reply_to(message, book.make_string())
    
    