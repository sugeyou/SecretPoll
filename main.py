__author__ = 'Valery'
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from datetime import datetime, date
import os

from db import DB


def private(func):
    def wrapped(update, context, *args, **kwargs):
        if update.message.chat.type=='private':
            return func(update, context, *args, **kwargs)
        return
    return wrapped

@private
def start(update, context):
    update.message.reply_text('Чтобы создать опрос, нажмите /NewPoll')
    print('start @', update.effective_user.username)

@private
def help(update, context):
    update.message.reply_text('''
        Бот предназначен для создания секретных опросов. 
        \nНикто кроме создателя опроса не видит результат голосования.
        \nСоздание опроса:
        \n/NewPoll
        \n\nСписок созданных опросов:
        \n/MyPolls
        ''')
    print('help')

def process_msg(update, context):
    if not update.message.chat.type == 'private': return
    uid = update.effective_user.id
    #TODO
    #db = DB()
    #umode, pollid = db.get_user_mode(uid)
    umode, pollid = 'Answer', 25
    txt = update.message.text
    if umode == 'Ready':
        update.message.reply_text('Для создания опроса нажмите /NewPoll')
    if umode == 'Question':
        #TODO
        #pollid = db.create_poll(txt, uid)
        #db.set_user_mode(uid, 'Answer', pollid)
        update.message.reply_text('Записал вопрос, теперь введите первый вариант ответа')
    if umode == 'Answer':
        #TODO
        #db.add_answer(pollid, txt)
        update.message.reply_text('''Записал этот вариант ответа, введите следующий. 
        \nКогда закончите, нажмите /Done 
        \nДля отмены создания опроса нажмите /Cancel''')
    print('umode: ', umode, ', uid: ', uid, ', text: ', txt)

@private
def add_new_poll(update, context):
    uid = update.effective_user.id
    #TODO
    #db = DB()
    #umode, pollid = db.get_user_mode(uid)
    umode, pollid = 'Answer', 25
    if umode == 'Ready':
        #TODO
        #db.set_user_mode(uid, 'Question')
        update.message.reply_text('Введите вопрос')
    else:
        if umode == 'Question':
            msg = 'Введите вопрос'
        if umode == 'Answer':
            msg = 'Введите вариант ответа'
        update.message.reply_text(
            'Вы уже в процессе создания опроса, сначала завершите его. {}'.format(msg))
    print('Start new poll' if umode == 'Ready' else 'Bad try to start new poll')

@private
def get_my_polls(update, context):
    pass

@private
def done_poll(update, context):
    uid = update.effective_user.id
    #TODO
    #db = DB()
    #umode, pollid = db.get_user_mode(uid)
    umode, pollid = 'Answer', 25
    if umode == 'Ready':
        update.message.reply_text('Вы еще не начали создание опроса')
    if umode == 'Question':
        update.message.reply_text('Вы еще не ввели вопрос')
    if umode == 'Answer':
        #TODOO
        #answers = db.get_answer_list(pollid)
        answers = [['ty'], ['hj']]
        if not answers or len(answers) == 1:
            update.message.reply_text('Введите больше одного варианта ответа на опрос')
        else:
            #TODO
            #db.set_user_mode(uid, 'Ready')
            #db.set_poll_active(pollid)
            update.message.reply_text('Процесс создание опроса завершен успешно')
    print('Poll done')

@private
def cancel_poll(update, context):
    uid = update.effective_user.id
    #TODO
    #db = DB()
    #umode, pollid = db.get_user_mode(uid)
    umode, pollid = 'Answer', 25
    if umode == 'Ready':
        update.message.reply_text('Вы еще не начали создание опроса')
        return
    if umode == 'Question':
        #TODO
        #db.set_user_mode(uid, 'Ready')
        print('q')
    if umode == 'Answer':
        #TODO
        #db.set_user_mode(uid, 'Ready')
        #db.delete_poll(pollid)
        print('a')
    update.message.reply_text('Создание опроса отменено')

def main():
    print('start program')

    #TODO
    #updater=Updater(os.environ['TOKEN'])
    token = '1488057490:AAGF6YahNhc8jr5UNqfaEMuWePGFDSSAMis'
    updater=Updater(token)
    dp=updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_msg),0)
    dp.add_handler(CommandHandler('start', start),1)
    dp.add_handler(CommandHandler('help', help),1)
    dp.add_handler(CommandHandler('NewPoll', add_new_poll),1)
    dp.add_handler(CommandHandler('MyPolls', get_my_polls),1)
    dp.add_handler(CommandHandler('Done', done_poll),1)
    dp.add_handler(CommandHandler('Cancel', cancel_poll),1)
    print('handlers added')

    updater.start_polling()
    updater.idle()
    print('exit program')

main()
