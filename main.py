__author__ = 'Valery'
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, date
import os


def private(func):
    def wrapped(bot,update, *args, **kwargs):
        if update.message.chat.type=='private':
            return func(bot,update, *args, **kwargs)
        return
    return wrapped

@private
def start(bot, update):
    update.message.reply_text('Чтобы создать опрос, нажмите /NewPoll')
    print('start @', update.effective_user.username)

@private
def help(bot, update):
    update.message.reply_text('''
        Бот предназначен для создания секретных опросов. 
        Никто кроме создателя опроса не видит результат голосования.
        \nСоздание опроса:
        \n/NewPoll
        \n\nСписок созданных опросов:
        \n/MyPolls
        ''')
    print('help')

def ProcessMsg(bot, update):
    db=DB()
    db.HandleMsg(update)
    print('updated/save data of @', update.effective_user.username, ' for chat ', update.effective_chat.title)

@private
def add_new_poll(bot, update):
    pass

@private
def get_my_polls(bot, update):
    pass

def main():
    print('start program')

    #updater=Updater(os.environ['TOKEN'])
    token = '1488057490:AAGF6YahNhc8jr5UNqfaEMuWePGFDSSAMis'
    updater=Updater(token)
    dp=updater.dispatcher

    #dp.add_handler(MessageHandler(not Filters.status_update, ProcessMsg),0)
    dp.add_handler(CommandHandler('start', start),1)
    dp.add_handler(CommandHandler('help', help),1)
    dp.add_handler(CommandHandler('NewPoll', add_new_poll),1)
    dp.add_handler(CommandHandler('MyPolls', get_my_polls),1)
    print('handlers added')

    updater.start_polling()
    updater.idle()
    print('exit program')

main()
