__author__ = 'Valery'
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, date
import os
from uuid import uuid4

from db import DB


def private(func):
    def wrapped(update, context, *args, **kwargs):
        if update.message.chat.type == 'private':
            return func(update, context, *args, **kwargs)
        return
    return wrapped

def check_ready(func):
    def wrapped(update, context, *args, **kwargs):
        uid = update.effective_user.id
        db = DB()
        umode, _ = db.get_user_mode(uid)
        if umode == 'Ready':
            return func(update, context, *args, **kwargs)
        else:
            update.message.reply_text('Сначала завершите создание опроса')
        return
    return wrapped

def check_poll_creator(func):
    def wrapped(update, context, *args, **kwargs):
        uid = update.effective_user.id
        pollid = update.callback_query.data.split('_')[-1]
        db = DB()
        creator = db.get_creator(pollid)
        if creator == uid:
            return func(update, context, *args, **kwargs)
        else:
            update.message.reply_text('У вас нет прав для этого действия')
            update.callback_query.answer()
        return
    return wrapped

def check_poll_exists(func):
    def wrapped(update, context, *args, **kwargs):
        uid = update.effective_user.id
        pollid = update.callback_query.data.split('_')[-1]
        db = DB()
        if not db.poll_exists(pollid):
            update.callback_query.message.reply_text('Такого опроса не обнаружено')
            update.callback_query.answer()
            return
        return func(update, context, *args, **kwargs)
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

@private
def process_msg(update, context):
    if not update.message.chat.type == 'private': return
    uid = update.effective_user.id
    db = DB()
    umode, pollid = db.get_user_mode(uid)
    txt = update.message.text
    if umode == 'Ready':
        update.message.reply_text('Для создания опроса нажмите /NewPoll')
    if umode == 'Question':
        pollid = db.create_poll(txt, uid)
        db.set_user_mode(uid, 'Answer', pollid)
        update.message.reply_text('Записал вопрос, теперь введите первый вариант ответа')
    if umode == 'Answer':
        db.add_answer(pollid, txt)
        update.message.reply_text('''Записал этот вариант ответа, введите следующий. 
        \nКогда закончите, нажмите /Done 
        \nДля отмены создания опроса нажмите /Cancel''')
    print('umode: ', umode, ', uid: ', uid, ', text: ', txt)

@private
def add_new_poll(update, context):
    uid = update.effective_user.id
    db = DB()
    umode, pollid = db.get_user_mode(uid)
    if umode == 'Ready':
        db.set_user_mode(uid, 'Question')
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
@check_ready
def get_my_polls(update, context):
    uid = update.effective_user.id
    db = DB()
    polls = db.get_user_poll_list(uid)
    if not polls or not polls[0]:
        update.message.reply_text('Опросов не обнаружено')
        return
    polls_num = len(polls)
    buttons = [[InlineKeyboardButton(q, callback_data=('upoll_' + p))] for q,p in polls]
    if polls_num > 5:
        buttons = buttons[:5] + [[InlineKeyboardButton('>', callback_data='upolls_2')]]
    keyboard = InlineKeyboardMarkup(buttons)
    update.message.reply_text(text=('Количество ваших опросов: {}'.format(str(polls_num)) +
                '\nПоказаны {0} из {1}'.format(5 if polls_num > 5 else polls_num, polls_num)),
                reply_markup=keyboard)

@check_ready
@check_poll_exists
@check_poll_creator
def show_poll_settings(update, context):
    uid = update.effective_user.id
    pollid = update.callback_query.data.split('_')[1]
    db = DB()
    is_active = db.is_poll_active(pollid)
    question = db.get_poll_question(pollid)
    answers = db.get_answer_count_list(pollid)
    answers = [[a,c if c else 0] for a,c in answers]
    answers.sort(key=lambda a: a[1])
    tot_ans = sum([ca[1] for ca in answers]) or 1
    txt = '{0}\n\n{1}'.format(question, 
          '\n'.join(['{0}: {1} ({2}%)'.format(a, c, c / tot_ans * 100) for a,c in answers]))
    act_btn = [InlineKeyboardButton('Остановить опрос' if is_active else 'Запустить опрос', 
                                    callback_data='setpoll_act_' + pollid)]
    del_btn = [InlineKeyboardButton('Удалить опрос', callback_data='setpoll_dell1_' + pollid)]
    buttons = [act_btn, del_btn]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.message.reply_text(txt, reply_markup=keyboard)
    update.callback_query.answer()

@check_ready
@check_poll_exists
@check_poll_creator
def change_poll_settings(update, context):
    uid = update.effective_user.id
    _, set_mode, pollid = update.callback_query.data.split('_')
    db = DB()
    if set_mode == 'act':
        is_active = db.is_poll_active(pollid)
        is_active = not is_active
        db.set_poll_active(pollid, is_active)
        txt = update.callback_query.message.text
        act_btn = [InlineKeyboardButton('Остановить опрос' if is_active else 'Запустить опрос', 
                                    callback_data='setpoll_act_' + pollid)]
        del_btn = [InlineKeyboardButton('Удалить опрос', callback_data='setpoll_dell1_' + pollid)]
        buttons = [act_btn, del_btn]
        keyboard = InlineKeyboardMarkup(buttons)
        update.callback_query.message.reply_text(txt, reply_markup=keyboard)
    if set_mode == 'del1':
        txt = 'Вы уверены, что хотите удалить этот опрос?'
        del_btn = [InlineKeyboardButton('Удалить опрос', callback_data='setpoll_dell2_' + pollid)]
        update.callback_query.message.reply_text(txt, reply_markup=InlineKeyboardMarkup([del_btn]))
    if set_mode == 'del2':
        db.delete_poll(pollid)
        update.callback_query.message.reply_text('Опрос удален')
    update.callback_query.answer()

@check_ready
def show_poll_list(update, context):
    uid = update.effective_user.id
    page_num = int(update.callback_query.data.split('_')[1])
    db = DB()
    polls = db.get_user_poll_list(uid)
    if not polls or not polls[0]:
        update.callback_query.message.reply_text('Опросов не обнаружено')
        update.callback_query.answer()
        return
    polls_num = len(polls)
    buttons = [[InlineKeyboardButton(q, callback_data=('upoll_' + p))] for q,p in polls]
    next_btn = [InlineKeyboardButton('>', callback_data='upolls_{}'.format(page_num + 1))]
    prev_btn = [InlineKeyboardButton('<', callback_data='upolls_{}'.format(page_num - 1))]
    if polls_num > 5 * (page_num - 1):
        buttons = buttons[5 * (page_num - 1):]
    else:
        page_num = 1
    if len(buttons) > 5:
        buttons = buttons[:5]
    turn_btns = []
    if page_num > 1:
        turn_btns += prev_btn
    if polls_num > 5 * page_num:
        turn_btns += next_btn
    if turn_btns:
        buttons += [turn_btns]
    txt = 'Количество ваших опросов: {}'.format(polls_num)
    txt += '\nПоказаны {0} - {1}'.format(5 * (page_num - 1) + 1, 
                5 * page_num if polls_num > (5 * page_num) else polls_num)
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.edit_message_text(text=txt, reply_markup=keyboard)
    update.callback_query.answer()

@private
def done_poll(update, context):
    uid = update.effective_user.id
    db = DB()
    umode, pollid = db.get_user_mode(uid)
    if umode == 'Ready':
        update.message.reply_text('Вы еще не начали создание опроса')
    if umode == 'Question':
        update.message.reply_text('Вы еще не ввели вопрос')
    if umode == 'Answer':
        answers = db.get_answer_list(pollid)
        if not answers or len(answers) == 1:
            update.message.reply_text('Введите больше одного варианта ответа на опрос')
        else:
            db.set_user_mode(uid, 'Ready')
            db.set_poll_active(pollid)
            update.message.reply_text('Процесс создание опроса завершен успешно')
    print('Poll done')

@private
def cancel_poll(update, context):
    uid = update.effective_user.id
    db = DB()
    umode, pollid = db.get_user_mode(uid)
    if umode == 'Ready':
        update.message.reply_text('Вы еще не начали создание опроса')
        return
    if umode == 'Question':
        db.set_user_mode(uid, 'Ready')
    if umode == 'Answer':
        db.set_user_mode(uid, 'Ready')
        db.delete_poll(pollid)
    update.message.reply_text('Создание опроса отменено')

def main():
    print('start program')

    updater=Updater(os.environ['TOKEN'])
    dp=updater.dispatcher

    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, process_msg),0)
    dp.add_handler(CommandHandler('start', start),1)
    dp.add_handler(CommandHandler('help', help),1)
    dp.add_handler(CommandHandler('NewPoll', add_new_poll),1)
    dp.add_handler(CommandHandler('MyPolls', get_my_polls),1)
    dp.add_handler(CommandHandler('Done', done_poll),1)
    dp.add_handler(CommandHandler('Cancel', cancel_poll),1)
    dp.add_handler(CallbackQueryHandler(show_poll_settings, pattern='^upoll_.*'), 2)
    dp.add_handler(CallbackQueryHandler(show_poll_list, pattern='^upolls_.*'), 2)
    dp.add_handler(CallbackQueryHandler(change_poll_settings, pattern='^setpoll_.*'), 2)
    print('handlers added')

    updater.start_polling()
    updater.idle()
    print('exit program')

main()
