import datetime as datetime
import telebot
from telebot import types
import time
import sqlite3
import pytz
from datetime import datetime
from contextlib import closing

import smtplib
import os
import pandas as pd
import mimetypes

# Библиотеки для отправки файлов по почте
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart

# Библиотеки для анализа слов (вопрос-ответ)
import stanza
ppln = stanza.Pipeline('ru', processors='tokenize,pos,lemma')

import pandas as pd
import csv
from csv import writer
from keyboa import Keyboa
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import text

import statistic_analysis

import imaplib
#Необходимо создать отдельный поток, который проверяет новые входящие письма
import threading


import config

bot = telebot.TeleBot(config.token, skip_pending=True)

user_dict = {}


def date_now():
    return datetime.now(pytz.timezone('Europe/Moscow'))


class User:
    def __init__(self, userid):
        self.userid = userid

        self.userfirstname = None
        self.userlastname = None

        self.startDS = None

        self.MSZ = None
        self.msz_step_one = None
        self.msz_step_two = None
        self.msz_step_two_one = None
        self.msz_step_two_two = None
        self.msz_step_three = None

        self.EDP_start = None
        self.market = None
        self.restr = None
        self.biglist = None
        self.hard_quest = None
        self.summ = None
        self.EDP_subject = None
        self.EDP_eol = None
        self.purch = None

        self.DSone = None
        self.DS = None
        self.customer = None
        self.subject = None
        self.eol = None
        self.change = None
        self.option = None
        self.changesize1 = None
        self.changesize2 = None

        self.grad = None
        self.grad_values = None
        self.comments = None

        self.type_quest = None

        self.quest = None

        self.quest_gl = None

        self.fir_quest = None
        self.sec_quest = None
        self.th_quest = None

        self.fir_quest_gl = None
        self.sec_quest_gl = None
        self.th_quest_gl = None
        self.breakk = None

        self.send = None

        self.take_nb = None

        self.list_massage_id = None

        self.user_id_to_sed_msg = None
        self.user_msg_to_sed_msg = None


# Получение данных для алгоритма вопрос-ответ
data_df = pd.read_excel('quest_dir/2021.02.25. Алгоритм (схема) и вопросы для чат-бота 14.11.2022!.xlsx',
                        engine='openpyxl')
da = {i: data_df.ans[i] for i in range(len(data_df.ans))}
dq = {i: data_df.quest[i] for i in range(len(data_df.quest))}

data_glos = pd.read_excel('quest_dir/Глоссарий.xlsx', engine='openpyxl')
dga = {i: data_glos.pon[i] for i in range(len(data_glos.pon))}
dgq = {i: data_glos.q[i] for i in range(len(data_glos.q))}
try:
    data_glos.ab = data_glos.ab.str.lower()
    data_glos.ab = data_glos.ab.str.replace(',', "")
    data_glos.ab = data_glos.ab.str.replace('?', "")
    data_glos.ab = data_glos.ab.str.replace('.', "")
    data_glos.ab = data_glos.ab.str.replace('"', "")
    data_glos.ab = data_glos.ab.str.replace("'", "")
    data_glos.ab = data_glos.ab.str.replace('«', "")
    data_glos.ab = data_glos.ab.str.replace('»', "")
    data_glos.ab = data_glos.ab.str.replace(')', "")
    data_glos.ab = data_glos.ab.str.replace('(', "")
    data_glos.ab = data_glos.ab.str.replace('-', " ")
except:
    print('')

# Чтение заранее подготовленного файла для алгоритма вопрос-ответ
quest_list_l = []
reader = pd.read_csv('quest_dir/file.csv', encoding='cp1251')
for i in reader:
    quest_list_l.append(i)

## Создание списка с id пользователей для проверки наличия доступа
users = list(pd.read_csv('users_card.csv', delimiter=',')['userid'])


def mail_check_info(sender, message):
    if ('gpn' in sender or 'gazprom' in sender) and not message in users:
        list_data = [message, sender]

        with open("users_card.csv", 'a', newline='',encoding='utf-8') as f_object:
            writer_object = writer(f_object)
            writer_object.writerow(list_data)
            f_object.close()


        users.append(int(message))
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать")
        markup.add(btn1)
        bot.send_sticker(message, text.sti_love)
        msg = bot.send_message(message, text=text.done_check_mail, reply_markup=markup)
        bot.register_next_step_handler(msg, send_start)



# команда /start
@bot.message_handler(commands=['start']
     , func=lambda message: message.chat.id in users
                     )
def send_start(message):
    user_card_p = pd.read_csv('users_card.csv', delimiter=',')
    if message.chat.id in list(user_card_p['userid']):
        chat_id = message.chat.id
        userid = message.chat.id
        user = User(userid)
        user_dict[chat_id] = user
        user.userfirstname = message.chat.first_name
        user.userlastname = message.chat.last_name

        collection_of_statistic_summ_start(user)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("ДС")
        btn2 = types.KeyboardButton("МСЗ")
        btn3 = types.KeyboardButton("ЕдП")
        btn4 = types.KeyboardButton("Задать вопрос")

        btn5 = types.KeyboardButton("Статистика3009")
        btn6 = types.KeyboardButton("Статистика1122")
        btn7 = types.KeyboardButton("Oтправить сообщение пользователям")

        markup.add(btn1, btn2, btn3)
        markup.add(btn4)

        if userid == 798637297:

            markup.add(btn5, btn6)
            markup.add(btn7)

        # msg = bot.send_message(message.chat.id,
        #                        text.start_1.format(
        #                            message.from_user), reply_markup=markup, parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.sti_hi)
        # bot.send_message(message.chat.id,
        #                  text.start_2.format(
        #                      message.from_user), parse_mode="Markdown")
        msg = bot.send_message(message.chat.id,
                         text.start_3.format(
                             message.from_user), reply_markup=markup, parse_mode="Markdown")
        bot.send_message(message.chat.id,"*Чат-бот проходит пилотное тестирование, разъяснения не являются официальными разъяснениями ДПОиМ*", parse_mode="Markdown")
        bot.register_next_step_handler(msg, startDS_def)
    else:
        access_check(message)




@bot.message_handler(content_types=['Начать заново'])
def send_welcome(message):
    user_card_p = pd.read_csv('users_card.csv', delimiter=',')
    if message.chat.id in list(user_card_p['userid']):
        chat_id = message.chat.id
        userid = message.chat.id
        user = User(userid)
        user_dict[chat_id] = user
        user.userfirstname = message.chat.first_name
        user.userlastname = message.chat.last_name

        collection_of_statistic_summ_start(user)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("ДС")
        btn2 = types.KeyboardButton("МСЗ")
        btn3 = types.KeyboardButton("ЕдП")
        btn4 = types.KeyboardButton("Задать вопрос")

        btn5 = types.KeyboardButton("Статистика3009")
        btn6 = types.KeyboardButton("Статистика1122")
        btn7 = types.KeyboardButton("Oтправить сообщение пользователям")

        markup.add(btn1, btn2, btn3)
        markup.add(btn4)

        if userid == 798637297:
            markup.add(btn5, btn6)
            markup.add(btn7)

        # msg = bot.send_message(message.chat.id,
        #                        text.start_1.format(
        #                            message.from_user), reply_markup=markup, parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.sti_hi)
        # bot.send_message(message.chat.id,
        #                  text.start_2.format(
        #                      message.from_user), parse_mode="Markdown")
        msg = bot.send_message(message.chat.id,
                         text.start_3.format(
                             message.from_user), reply_markup=markup, parse_mode="Markdown")
        bot.send_message(message.chat.id,
                         "*Чат-бот проходит пилотное тестирование, разъяснения не являются официальными разъяснениями ДПОиМ*",
                         parse_mode="Markdown")
        bot.register_next_step_handler(msg, startDS_def)
    else:
        access_check(message)


@bot.message_handler(func=lambda message: message.chat.id not in users)
def access_check(message):
    if message.chat.id not in users:
        bot.send_message(message.chat.id, text.danger_1.format(
                         message.from_user), parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.danger_sti)
        bot.send_message(message.chat.id, text=text.danger_2, parse_mode="Markdown")
        bot.send_message(message.chat.id, text=str(message.chat.id), parse_mode="Markdown")
        bot.send_message(message.chat.id, text=config.FROM_EMAIL, parse_mode="Markdown")
        bot.send_message(message.chat.id, text=text.danger_3, parse_mode="Markdown")
        bot.send_message(message.chat.id, text=text.danger_4, parse_mode="Markdown")
        bot.send_message(message.chat.id,
                         "*Чат-бот проходит пилотное тестирование, разъяснения не являются официальными разъяснениями ДПОиМ*",
                         parse_mode="Markdown")



@bot.message_handler(content_types=['text'])
def startDS_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]

    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Статистика1122"):
        #
        # # Отправка пользователю баз данных при вводе "Статистика1122" в самом начале

        statistic_analysis.send_statistic()

        conn = sqlite3.connect('alg_dir/data.db')
        df = pd.read_sql('select * from stat', conn)
        df.to_excel(r'Статистика.xlsx', index=False)
        bot.send_document(chat_id=chat_id, document=open(
            'Статистика.xlsx',
            'rb'))
        os.remove('Статистика.xlsx')

        conn = sqlite3.connect('alg_dir/data.db')
        df = pd.read_sql('select * from grade', conn)
        df.to_excel(r'Оценки.xlsx', index=False)
        bot.send_document(chat_id=chat_id, document=open(
            'Оценки.xlsx',
            'rb'))
        os.remove('Оценки.xlsx')

        conn = sqlite3.connect('alg_dir/data.db')
        df = pd.read_sql('select * from summ', conn)
        df.to_excel(r'Статистика_start.xlsx', index=False)
        bot.send_document(chat_id=chat_id, document=open(
            'Статистика_start.xlsx',
            'rb'))
        os.remove('Статистика_start.xlsx')

        conn = sqlite3.connect('quest_dir/data_quest.db')
        df = pd.read_sql('select * from quest', conn)
        df.to_excel(r'Статистика вопросов.xlsx', index=False)
        bot.send_document(chat_id=chat_id, document=open(
            'Статистика вопросов.xlsx',
            'rb'))
        os.remove('Статистика вопросов.xlsx')
        bot.send_document(chat_id=chat_id, document=open(
            'users_card.csv',
            'rb'))


        statistic_analysis.send_statistic()
    elif message.text == 'Удалить меня из базы':
        users.remove(798637297)

        list_mail_id_base = []
        with open("users_card.csv", newline='', encoding='utf-8') as f_object:
            reader = csv.reader(f_object)
            for row in reader:
                if not row[0] == '798637297':
                    list_mail_id_base.append(row)

        with open("users_card.csv", 'w', newline='', encoding='utf-8') as f_object:
            writer_object = writer(f_object)
            for list_data in list_mail_id_base:
                print(list_data)
                writer_object.writerow(list_data)
            f_object.close()

        bot.send_message(798637297, 'Удалено')

    elif message.text == "Задать вопрос":
        quest_def(message)
    elif message.text == "Статистика3009":
        bot.send_message(message.chat.id, statistic_analysis.send_statistic(),
                               parse_mode="Markdown")
    elif message.text == "Oтправить сообщение пользователям":
        send_msg_to_users(message)
    elif (message.text == "Вернуться назад"):
        if user.startDS == None:
            send_start(message)
    startDS = message.text
    if (message.text == "ДС" or message.text == "МСЗ" or message.text == "Вернуться назад" or message.text == "ЕдП"):
        if ((message.text == "ДС") or (message.text == "МСЗ") or (message.text == "ЕдП")):
            user.startDS = startDS
        if user.startDS == "ДС":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.ds_start_mark_neraz)
            btn2 = types.KeyboardButton(text.ds_start_mark_priznak)
            btn3 = types.KeyboardButton(text.ds_start_mark_uznat)
            btn4 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            markup.row(btn4)
            msg = bot.send_message(message.chat.id, text.ds_start_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, DSone_def)
        elif user.startDS == "МСЗ":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.msz_start_mark1)
            btn2 = types.KeyboardButton(text.msz_start_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.msz_start, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, MSZ_def)
        elif user.startDS == "ЕдП":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.EDP_start_mark_1)
            btn2 = types.KeyboardButton(text.EDP_start_mark_2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.add(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.EDP_start, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, EDP_start_def)
    # if not (message.text == "ДС" or message.text == "МСЗ" or message.text == "Вернуться назад" or message.text == "ЕдП"
    #                 or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
    #     msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
    #     bot.register_next_step_handler(msg, startDS_def)


########################################################################################################################
# Ветка МСЗ
def MSZ_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.MSZ == None:
            user.startDS = None
            send_start(message)
    if (
            message.text == text.msz_start_mark2 or message.text == text.msz_start_mark1 or message.text == "Вернуться назад"):
        if ((message.text == text.msz_start_mark2) or (message.text == text.msz_start_mark1)):
            MSZ = message.text
            user.MSZ = MSZ
        if user.MSZ == text.msz_start_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.MSZ_def_prev, reply_markup=markup, parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
        elif user.MSZ == text.msz_start_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.MSZ_def_ne_prev_mark1)
            btn2 = types.KeyboardButton(text.MSZ_def_ne_prev_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            bot.send_message(message.chat.id, text.MSZ_def_ne_prev_1, reply_markup=markup, parse_mode="Markdown")

            msg = bot.send_message(message.chat.id, text.MSZ_def_ne_prev_2, reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, msz_step_one_def)
    if not (message.text == text.msz_start_mark2 or message.text == text.msz_start_mark1
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, MSZ_def)


def msz_step_one_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.msz_step_one == None:
            user.MSZ = None
            startDS_def(message)
    if (
            message.text == text.MSZ_def_ne_prev_mark1 or message.text == text.MSZ_def_ne_prev_mark2 or message.text == "Вернуться назад"):
        if ((message.text == text.MSZ_def_ne_prev_mark1) or (message.text == text.MSZ_def_ne_prev_mark2)):
            msz_step_one = message.text
            user.msz_step_one = msz_step_one
        if user.msz_step_one == text.MSZ_def_ne_prev_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")

            collection_of_statistic(user)

            bot.register_next_step_handler(msg, grad)

        elif user.msz_step_one == text.MSZ_def_ne_prev_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.msz_step_one_def_mark1)
            btn2 = types.KeyboardButton(text.msz_step_one_def_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)

            msg = bot.send_message(message.chat.id, text.msz_step_one_def, reply_markup=markup, parse_mode="Markdown")

            bot.register_next_step_handler(msg, msz_step_two_def)
    if not (message.text == text.MSZ_def_ne_prev_mark1 or message.text == text.MSZ_def_ne_prev_mark2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_one_def)


def msz_step_two_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.msz_step_two == None:
            user.msz_step_one = None
            MSZ_def(message)
    if (
            message.text == text.msz_step_one_def_mark1 or message.text == text.msz_step_one_def_mark2 or message.text == "Вернуться назад"):
        if ((message.text == text.msz_step_one_def_mark1) or (message.text == text.msz_step_one_def_mark2)):
            msz_step_two = message.text
            user.msz_step_two = msz_step_two
        if user.msz_step_two == text.msz_step_one_def_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.msz_step_two_def_da_mark1)
            btn2 = types.KeyboardButton(text.msz_step_two_def_da_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.msz_step_two_def_da, reply_markup=markup,
                                   parse_mode="Markdown")

            bot.register_next_step_handler(msg, msz_step_two_one_def)

        elif user.msz_step_two == text.msz_step_one_def_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.msz_step_two_def_net_mark1)
            btn2 = types.KeyboardButton(text.msz_step_two_def_net_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.msz_step_two_def_net, reply_markup=markup,
                                   parse_mode="Markdown")

            bot.register_next_step_handler(msg, msz_step_two_two_def)
    if not (message.text == text.msz_step_one_def_mark1 or message.text == text.msz_step_one_def_mark2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_two_def)


def msz_step_two_one_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.msz_step_two_one == None:
            user.msz_step_two = None
            msz_step_one_def(message)
    if (
            message.text == text.msz_step_two_def_da_mark1 or message.text == text.msz_step_two_def_da_mark2 or message.text == "Вернуться назад"):
        if ((message.text == text.msz_step_two_def_da_mark1) or (message.text == text.msz_step_two_def_da_mark2)):
            msz_step_two_one = message.text
            user.msz_step_two_one = msz_step_two_one
        if user.msz_step_two_one == text.msz_step_two_def_da_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.msz_step_two_one_def_da, reply_markup=markup,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)

        elif user.msz_step_two_one == text.msz_step_two_def_da_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.msz_step_two_one_def_net, reply_markup=markup,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
    if not (message.text == text.msz_step_two_def_da_mark1 or message.text == text.msz_step_two_def_da_mark2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_two_one_def)


def msz_step_two_two_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.msz_step_two_two == None:
            user.msz_step_two = None
            msz_step_one_def(message)
    if (
            message.text == text.msz_step_two_def_net_mark1 or message.text == text.msz_step_two_def_net_mark2 or message.text == "Вернуться назад"):
        if ((message.text == text.msz_step_two_def_net_mark1) or (message.text == text.msz_step_two_def_net_mark2)):
            msz_step_two_two = message.text
            user.msz_step_two_two = msz_step_two_two
        if msz_step_two_two == text.msz_step_two_def_net_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.msz_step_two_two_def_da_mark1)
            btn2 = types.KeyboardButton(text.msz_step_two_two_def_da_mark2)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.msz_step_two_two_def_da, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, msz_step_three_def)

        elif msz_step_two_two == text.msz_step_two_def_net_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.msz_step_two_two_def_net,
                             parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")

            collection_of_statistic(user)

            bot.register_next_step_handler(msg, grad)
    if not (message.text == text.msz_step_two_def_net_mark1 or message.text == text.msz_step_two_def_net_mark2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_two_two_def)


def msz_step_three_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.msz_step_three == None:
            user.msz_step_two_two = None
            msz_step_two_def(message)
    if (
            message.text == text.msz_step_two_two_def_da_mark1 or message.text == text.msz_step_two_two_def_da_mark2 or message.text == "Вернуться назад"):
        if ((message.text == text.msz_step_two_two_def_da_mark1) or (
                message.text == text.msz_step_two_two_def_da_mark2)):
            msz_step_three = message.text
            user.msz_step_three = msz_step_three
        if user.msz_step_three == text.msz_step_two_two_def_da_mark1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Начать заново")
            btn2 = types.KeyboardButton(text.mark_grad)
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.msz_step_three_def_da,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)

        elif user.msz_step_three == text.msz_step_two_two_def_da_mark2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            bot.send_message(message.chat.id, text.msz_step_three_def_net,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
    if not (message.text == text.msz_step_two_two_def_da_mark1 or message.text == text.msz_step_two_two_def_da_mark2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


########################################################################################################################


# Ветка с ЕдП

def EDP_start_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.EDP_start == None:
            user.startDS = None
            send_start(message)
    if (
            message.text == text.EDP_start_mark_1 or message.text == text.EDP_start_mark_2 or message.text == "Вернуться назад"):
        if ((message.text == text.EDP_start_mark_1) or (message.text == text.EDP_start_mark_2)):
            EDP_start = message.text
            user.EDP_start = EDP_start
        if user.EDP_start == text.EDP_start_mark_1:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.EDP_start_def_1_mark_da)
            btn2 = types.KeyboardButton(text.EDP_start_def_1_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.EDP_start_def_1,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, market_def)
        elif user.EDP_start == text.EDP_start_mark_2:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.EDP_start_def_2_mark_da)
            btn2 = types.KeyboardButton(text.EDP_start_def_2_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.EDP_start_def_2,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, summ_def)
    if not (message.text == text.EDP_start_mark_1 or message.text == text.EDP_start_mark_2
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def market_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.market == None:
            user.EDP_start = None
            startDS_def(message)
    if (
            message.text == text.EDP_start_def_1_mark_da or message.text == text.EDP_start_def_1_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.EDP_start_def_1_mark_da) or (message.text == text.EDP_start_def_1_mark_net)):
            market = message.text
            user.market = market
        if user.market == text.EDP_start_def_1_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.market_def_da_mark_da)
            btn2 = types.KeyboardButton(text.market_def_da_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.market_def_da,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, restr_def)
        elif user.market == text.EDP_start_def_1_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.market_def_net_mark_da)
            btn2 = types.KeyboardButton(text.market_def_net_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.market_def_net,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.send_document(chat_id=chat_id,
                              document=open('alg_dir/Основания для закупки у ЕдП.pdf', 'rb'))
            bot.register_next_step_handler(msg, biglist_def)
    if not (message.text == text.EDP_start_def_1_mark_da or message.text == text.EDP_start_def_1_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def restr_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.restr == None:
            user.market = None
            EDP_start_def(message)
    if (
            message.text == text.market_def_da_mark_da or message.text == text.market_def_da_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.market_def_da_mark_da) or (message.text == text.market_def_da_mark_net)):
            restr = message.text
            user.restr = restr
        if user.restr == text.market_def_da_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)

            collection_of_statistic(user)
            bot.send_message(message.chat.id, text.restr_def_net, parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
        elif user.restr == text.market_def_da_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.restr_def_da_mark_da)
            btn2 = types.KeyboardButton(text.restr_def_da_mark_da)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.restr_def_da,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.send_document(chat_id=chat_id,
                              document=open('alg_dir/Основания для закупки у ЕдП.pdf', 'rb'))
            bot.register_next_step_handler(msg, biglist_def)
    if not (message.text == text.market_def_da_mark_da or message.text == text.market_def_da_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def biglist_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.biglist == None:
            if user.restr == None:
                user.market = None
                EDP_start_def(message)
            else:
                user.restr = None
                market_def(message)
    if (
            message.text == text.market_def_net_mark_da or message.text == text.market_def_net_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.market_def_net_mark_da) or (message.text == text.market_def_net_mark_net)):
            biglist = message.text
            user.biglist = biglist
        if user.biglist == text.market_def_net_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)

            collection_of_statistic(user)
            bot.send_message(message.chat.id, text.biglist_def_net, parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
        elif user.biglist == text.market_def_net_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.biglist_def_da_mark_da)
            btn2 = types.KeyboardButton(text.biglist_def_da_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.biglist_def_da,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, hard_quest_def)
    if not (message.text == text.market_def_net_mark_da or message.text == text.market_def_net_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def hard_quest_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.hard_quest == None:
            user.biglist = None
            if user.restr == None:
                market_def(message)
            else:
                restr_def(message)
    if (
            message.text == text.biglist_def_da_mark_da or message.text == text.biglist_def_da_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.biglist_def_da_mark_da) or (message.text == text.biglist_def_da_mark_net)):
            hard_quest = message.text
            user.hard_quest = hard_quest
        if user.hard_quest == text.biglist_def_da_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)

            collection_of_statistic(user)
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
        elif hard_quest == text.biglist_def_da_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.hard_quest_def_da_mark_da)
            btn2 = types.KeyboardButton(text.hard_quest_def_da_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.hard_quest_def_da,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, summ_def)
    if not (message.text == text.biglist_def_da_mark_da or message.text == text.biglist_def_da_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def summ_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.summ == None:
            if user.hard_quest == None:
                user.EDP_start = None
                startDS_def(message)
            else:
                user.hard_quest = None
                biglist_def(message)
    if (message.text == text.EDP_start_def_2_mark_da or message.text == text.EDP_start_def_2_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.EDP_start_def_2_mark_da) or (message.text == text.EDP_start_def_2_mark_net)):
            summ = message.text
            user.summ = summ
        if ((user.summ == text.EDP_start_def_2_mark_da) or (user.summ == text.EDP_start_def_2_mark_net)):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.summ_def_mark_kc)
            btn2 = types.KeyboardButton(text.summ_def_mark_gpn)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.summ_def,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, EDP_subject_def)
    if not (message.text == text.EDP_start_def_2_mark_da or message.text == text.EDP_start_def_2_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def EDP_subject_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.EDP_subject == None:
            user.summ = None
            if user.hard_quest == None:
                EDP_start_def(message)
            else:
                hard_quest_def(message)

    if (
            message.text == text.summ_def_mark_kc or message.text == text.summ_def_mark_gpn or message.text == "Вернуться назад"):
        if ((message.text == text.summ_def_mark_kc) or (message.text == text.summ_def_mark_gpn)):
            EDP_subject = message.text
            user.EDP_subject = EDP_subject
        if (user.EDP_subject == text.summ_def_mark_kc) or (user.EDP_subject == text.summ_def_mark_gpn):
            if (user.EDP_subject == text.summ_def_mark_gpn) and (user.summ == text.hard_quest_def_da_mark_net):
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.EDP_subject_def_gpn_net_mark_da)
                btn2 = types.KeyboardButton(text.EDP_subject_def_gpn_net_mark_net)
                btn3 = types.KeyboardButton("Вернуться назад")
                markup.row(btn1, btn2)
                markup.row(btn3)
                msg = bot.send_message(message.chat.id, text.EDP_subject_def_gpn_net,
                                       reply_markup=markup, parse_mode="Markdown")
                bot.register_next_step_handler(msg, EDP_final_step_def)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.EDP_subject_def_mark_da)
                btn2 = types.KeyboardButton(text.EDP_subject_def_mark_net)
                btn3 = types.KeyboardButton("Вернуться назад")
                markup.row(btn1, btn2)
                markup.row(btn3)
                msg = bot.send_message(message.chat.id, text.EDP_subject_def,
                                       reply_markup=markup, parse_mode="Markdown")
                bot.register_next_step_handler(msg, EDP_eol_def)
    if not (message.text == text.summ_def_mark_kc or message.text == text.summ_def_mark_gpn
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def EDP_eol_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.EDP_eol == None:
            user.EDP_subject = None
            summ_def(message)
    if (
            message.text == text.EDP_subject_def_mark_da or message.text == text.EDP_subject_def_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.EDP_subject_def_mark_da) or (message.text == text.EDP_subject_def_mark_net)):
            EDP_eol = message.text
            user.EDP_eol = EDP_eol
        if (user.EDP_eol == text.EDP_subject_def_mark_da) or (user.EDP_eol == text.EDP_subject_def_mark_net):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.EDP_eol_def_mark_da)
            btn2 = types.KeyboardButton(text.EDP_eol_def_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.EDP_eol_def,
                                   reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, EDP_final_step_def)
    if not (message.text == text.EDP_subject_def_mark_da or message.text == text.EDP_subject_def_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)


def EDP_final_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.purch == None:
            if user.EDP_eol == None:
                user.EDP_subject = None
                summ_def(message)
            else:
                user.EDP_eol = None
                EDP_subject_def(message)
    if (
            message.text == text.EDP_subject_def_gpn_net_mark_da or message.text == text.EDP_subject_def_gpn_net_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.EDP_subject_def_gpn_net_mark_da) or (
                message.text == text.EDP_subject_def_gpn_net_mark_net)):
            purch = message.text
            user.purch = purch

        if ((user.purch == text.EDP_subject_def_gpn_net_mark_da) or (
                user.purch == text.EDP_subject_def_gpn_net_mark_net)):
            if user.summ == text.hard_quest_def_da_mark_net:
                if user.EDP_subject == text.summ_def_mark_kc:
                    if user.EDP_eol == text.EDP_subject_def_gpn_net_mark_net:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_1, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
                    elif user.EDP_eol == text.EDP_subject_def_mark_da:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_2, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
                elif user.EDP_subject == text.summ_def_mark_gpn:
                    if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                        bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                    elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                        bot.send_message(message.chat.id, text.EDP_vers_3, parse_mode="Markdown")
                        bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                        bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
            elif user.summ == text.hard_quest_def_da_mark_da:
                if user.EDP_subject == text.summ_def_mark_kc:
                    if user.EDP_eol == text.EDP_subject_def_gpn_net_mark_net:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_4, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
                    elif user.EDP_eol == text.EDP_subject_def_mark_da:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_5, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
                elif user.EDP_subject == text.summ_def_mark_gpn:
                    if user.EDP_eol == text.EDP_subject_def_gpn_net_mark_net:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_6, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
                    elif user.EDP_eol == text.EDP_subject_def_mark_da:
                        if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                            bot.send_message(message.chat.id, text.EDP_vers_0, parse_mode="Markdown")
                        elif user.purch == text.EDP_subject_def_gpn_net_mark_net:
                            bot.send_message(message.chat.id, text.EDP_vers_7, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_documents, parse_mode="Markdown")
                            bot.send_message(message.chat.id, text.EDP_templates, parse_mode="Markdown")
             if user.purch == text.EDP_subject_def_gpn_net_mark_da:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.mark_grad)
                btn2 = types.KeyboardButton("Начать заново")
                markup.add(btn1)
                markup.add(btn2)
                collection_of_statistic(user)
                msg = bot.send_message(message.chat.id, text.finish_1,
                                       reply_markup=markup, parse_mode="Markdown")

                bot.send_sticker(message.chat.id, text.finish_sti)

                bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
                bot.register_next_step_handler(msg, grad)
            else:

                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.mark_grad)
                btn2 = types.KeyboardButton("Отправить шаблоны на почту")
                btn3 = types.KeyboardButton("Начать заново")
                markup.add(btn1)
                markup.add(btn2)
                markup.add(btn3)
                msg = bot.send_message(message.chat.id, text.finish_1,
                                       reply_markup=markup, parse_mode="Markdown")

                bot.send_sticker(message.chat.id, text.finish_sti)

                bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
                bot.register_next_step_handler(msg, grad)
    if not (
            message.text == text.EDP_subject_def_gpn_net_mark_da or message.text == text.EDP_subject_def_gpn_net_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, msz_step_three_def)



#####################################################################################################################################3


# Ветка с ДС

def DSone_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.DSone == None:
            user.startDS = None
            send_start(message)
    if (
            message.text == text.ds_start_mark_neraz or message.text == text.ds_start_mark_priznak or message.text == text.ds_start_mark_uznat or message.text == "Вернуться назад"):
        if ((message.text == text.ds_start_mark_neraz) or (message.text == text.ds_start_mark_priznak) or (
                message.text == text.ds_start_mark_uznat)):
            DSone = message.text
            user.DSone = DSone
        if user.DSone == text.ds_start_mark_neraz:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.DSone_def_neraz_mark_da)
            btn2 = types.KeyboardButton(text.DSone_def_neraz_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.DSone_def_neraz_text_1, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.send_message(message.chat.id, text.DSone_def_neraz_text_2,
                             parse_mode="Markdown")
            bot.register_next_step_handler(msg, DS_def)


        elif user.DSone == text.ds_start_mark_priznak:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)

            bot.send_message(message.chat.id, text.DSone_def_priznak_text,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)

        elif user.DSone == text.ds_start_mark_uznat:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.ds_start_mark_neraz)
            btn2 = types.KeyboardButton(text.ds_start_mark_priznak)
            btn3 = types.KeyboardButton(text.ds_start_mark_uznat)
            btn4 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            markup.row(btn4)
            msg = bot.send_message(message.chat.id, text.DSone_def_uznat_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, DSone_def)
    if not (message.text == text.ds_start_mark_neraz or message.text == text.ds_start_mark_priznak
            or message.text == text.ds_start_mark_uznat
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DSone_def)


def DS_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.DS == None:
            user.DSone = None
            startDS_def(message)
    if (
            message.text == text.DSone_def_neraz_mark_net or message.text == text.DSone_def_neraz_mark_da or message.text == "Вернуться назад"):
        if ((message.text == text.DSone_def_neraz_mark_net) or (message.text == text.DSone_def_neraz_mark_da)):
            DS = message.text
            user.DS = DS
        if user.DS == text.DSone_def_neraz_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.DS_def_net_mark_gpn)
            btn2 = types.KeyboardButton(text.DS_def_net_mark_kc)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.DS_def_net_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_customer_step_def)

        elif user.DS == text.DSone_def_neraz_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)

            bot.send_message(message.chat.id, text.DS_def_da_text,
                             parse_mode="Markdown")

            collection_of_statistic(user)

            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
    if not (message.text == text.DSone_def_neraz_mark_da or message.text == text.DSone_def_neraz_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DS_def)


def process_customer_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.customer == None:
            user.DS = None
            DSone_def(message)
    if (
            message.text == text.DS_def_net_mark_gpn or message.text == text.DS_def_net_mark_kc or message.text == "Вернуться назад"):
        if ((message.text == text.DS_def_net_mark_gpn) or (message.text == text.DS_def_net_mark_kc)):
            customer = message.text
            user.customer = customer
        if ((user.customer == text.DS_def_net_mark_gpn) or (user.customer == text.DS_def_net_mark_kc)):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True, )
            btn1 = types.KeyboardButton(text.process_customer_step_def_mark_rabota)
            btn2 = types.KeyboardButton(text.process_customer_step_def_mark_mtr)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.process_customer_step_def_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_subject_step_def)

    if not (message.text == text.DS_def_net_mark_gpn or message.text == text.DS_def_net_mark_kc
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, process_customer_step_def)


def process_subject_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.subject == None:
            user.customer = None
            DS_def(message)
    if (
            message.text == text.process_customer_step_def_mark_mtr or message.text == text.process_customer_step_def_mark_rabota or message.text == "Вернуться назад"):
        if ((message.text == text.process_customer_step_def_mark_mtr) or (
                message.text == text.process_customer_step_def_mark_rabota)):
            subject = message.text
            user.subject = subject

        if user.subject == text.process_customer_step_def_mark_mtr:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_subject_step_def_mtr_mark_da)
            btn2 = types.KeyboardButton(text.process_subject_step_def_mtr_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.process_subject_step_def_mtr_text, reply_markup=markup,
                                   parse_mode="Markdown")

            bot.register_next_step_handler(msg, process_change_step_def)

        elif user.subject == text.process_customer_step_def_mark_rabota:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_subject_step_def_rabota_mark_da)
            btn2 = types.KeyboardButton(text.process_subject_step_def_rabota_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.process_subject_step_def_rabota_text_1, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.send_message(message.chat.id, text.process_subject_step_def_rabota_text_2,
                             parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_eol_step_def)

    if not (
            message.text == text.process_customer_step_def_mark_mtr or message.text == text.process_customer_step_def_mark_rabota
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, process_subject_step_def)


def process_eol_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.eol == None:
            user.subject = None
            process_customer_step_def(message)
    if (
            message.text == text.process_subject_step_def_rabota_mark_da or message.text == text.process_subject_step_def_rabota_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.process_subject_step_def_rabota_mark_da) or (
                message.text == text.process_subject_step_def_rabota_mark_net)):
            eol = message.text
            user.eol = eol

        if ((user.eol == text.process_subject_step_def_rabota_mark_da) or (
                user.eol == text.process_subject_step_def_rabota_mark_net)):
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_eol_step_def_mark_da)
            btn2 = types.KeyboardButton(text.process_eol_step_def_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.process_eol_step_def_text, reply_markup=markup,
                                   parse_mode="Markdown")

            bot.register_next_step_handler(msg, process_change_step_def)
    if not (
            message.text == text.process_subject_step_def_rabota_mark_da or message.text == text.process_subject_step_def_rabota_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, process_subject_step_def)


def process_change_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.change == None:
            if user.eol == None:
                user.subject = None
                process_customer_step_def(message)
            else:
                user.eol = None
                process_subject_step_def(message)
    if (
            message.text == text.process_eol_step_def_mark_da or message.text == text.process_eol_step_def_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.process_eol_step_def_mark_da) or (
                message.text == text.process_eol_step_def_mark_net)):
            change = message.text
            user.change = change

        if user.change == text.process_eol_step_def_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_change_step_def_net_mark_1)
            btn2 = types.KeyboardButton(text.process_change_step_def_net_mark_2)
            btn3 = types.KeyboardButton(text.process_change_step_def_net_mark_3)
            btn4 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2, btn3)
            markup.row(btn4)
            msg = bot.send_message(message.chat.id, text.process_change_step_def_net_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.send_document(chat_id=chat_id, document=open(
                'alg_dir/Характер планируемых изменений (дополнений) к договору, заключенному по результату закупки.pdf',
                'rb'))

            bot.register_next_step_handler(msg, process_final_step_def)
        elif user.change == text.process_eol_step_def_mark_da:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_change_step_def_da_mark_da)
            btn2 = types.KeyboardButton(text.process_change_step_def_da_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)

            bot.send_message(message.chat.id, text.process_change_step_def_da_text_1,
                             parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, text.process_change_step_def_da_text_2, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_changesize1_step_def)
    if not (message.text == text.process_eol_step_def_mark_da or message.text == text.process_eol_step_def_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DS_def)


def process_changesize1_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.changesize1 == None:
            user.change = None
            if user.eol == None:
                process_subject_step_def(message)
            else:
                process_eol_step_def(message)
    if (
            message.text == text.process_change_step_def_da_mark_da or message.text == text.process_change_step_def_da_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.process_change_step_def_da_mark_da) or (
                message.text == text.process_change_step_def_da_mark_net)):
            changesize1 = message.text
            user.changesize1 = changesize1

        if user.changesize1 == text.process_change_step_def_da_mark_da:
            if user.subject == text.process_customer_step_def_mark_mtr:
                bot.send_message(message.chat.id, text.pers_14, parse_mode="Markdown")
            elif user.subject == text.process_customer_step_def_mark_rabota and user.eol == text.process_subject_step_def_rabota_mark_da:
                bot.send_message(message.chat.id, text.pers_15, parse_mode="Markdown")
            elif user.subject == text.process_customer_step_def_mark_rabota and user.eol == text.process_subject_step_def_rabota_mark_net:
                bot.send_message(message.chat.id, text.pers_16, parse_mode="Markdown")
            #             bot.send_document(chat_id=chat_id,
            #                               document=open('alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Аналитические данные изменения стоимости договора.xlsx', 'rb'))
            #             bot.send_document(chat_id=chat_id,
            #                               document=open('alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Бюллетень для голосования члена Сметной комиссии.docx', 'rb'))
            #             bot.send_document(chat_id=chat_id, document=open(
            #                 'alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Решение о заключении ДС.docx', 'rb'))
            #             bot.send_document(chat_id=chat_id, document=open(
            #                 'alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Сопроводительное письмо в адрес Сметной комиссии.docx', 'rb'))
            #             bot.send_document(chat_id=chat_id, document=open(
            #                 'alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Справка по изменению, дополнению договора.xlsx',
            #                 'rb'))
            #             bot.send_document(chat_id=chat_id, document=open(
            #                 'alg_dir/templates/Папка 4 (п.4.3 - КТ 530)/Уведомление Инициатора о возможности изменения, дополнения договора.docx',
            #                 'rb'))
            bot.send_message(message.chat.id,
                             "Шаблоны доступы на ресурсе [«Закупки. Методология»](https://poz.gazprom-neft.local) в разделе «Шаблоны» / «Дополнительные соглашения».",
                             parse_mode="Markdown")

            collection_of_statistic(user)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Отправить шаблоны на почту")
            btn3 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)

        elif user.changesize1 == text.process_change_step_def_da_mark_net:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.process_changesize1_step_def_net_mark_da)
            btn2 = types.KeyboardButton(text.process_changesize1_step_def_net_mark_net)
            btn3 = types.KeyboardButton("Вернуться назад")
            markup.row(btn1, btn2)
            markup.row(btn3)
            msg = bot.send_message(message.chat.id, text.process_changesize1_step_def_net_text, reply_markup=markup,
                                   parse_mode="Markdown")
            bot.register_next_step_handler(msg, process_changesize2_step_def)
    if not (
            message.text == text.process_change_step_def_da_mark_da or message.text == text.process_change_step_def_da_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DS_def)


def process_changesize2_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.changesize2 == None:
            user.changesize1 = None
            process_change_step_def(message)
    if (
            message.text == text.process_changesize1_step_def_net_mark_da or message.text == text.process_changesize1_step_def_net_mark_net or message.text == "Вернуться назад"):
        if ((message.text == text.process_changesize1_step_def_net_mark_da) or (
                message.text == text.process_changesize1_step_def_net_mark_net)):
            changesize2 = message.text
            user.changesize2 = changesize2

            if user.changesize2 == text.process_changesize1_step_def_net_mark_da:
                if user.subject == text.process_customer_step_def_mark_mtr:
                    bot.send_message(message.chat.id, text.pers_11, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.eol == text.process_subject_step_def_rabota_mark_da:
                    bot.send_message(message.chat.id, text.pers_12, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.eol == text.process_subject_step_def_rabota_mark_net:
                    bot.send_message(message.chat.id, text.pers_13, parse_mode="Markdown")
                # bot.send_document(chat_id=chat_id,
                #                   document=open('alg_dir/templates/Папка 3 (п.4.2 - КТ 530)/Аналитические данные изменения стоимости договора.xlsx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 3 (п.4.2 - КТ 530)/Решение о заключении ДС.docx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 3 (п.4.2 - КТ 530)/Справка по изменению, дополнению договора.xlsx',
                #     'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 3 (п.4.2 - КТ 530)/Уведомление Инициатора о возможности изменения, дополнения договора.docx',
                #     'rb'))
            elif user.changesize2 == text.process_changesize1_step_def_net_mark_net:
                if ((user.subject == text.process_customer_step_def_mark_mtr) or (
                        user.subject == text.process_customer_step_def_mark_rabota)) and user.customer == text.DS_def_net_mark_gpn:
                    bot.send_message(message.chat.id, text.pers_7, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_mtr and user.customer == text.DS_def_net_mark_kc:
                    bot.send_message(message.chat.id, text.pers_8, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.customer == text.DS_def_net_mark_kc and user.eol == text.process_subject_step_def_rabota_mark_da:
                    bot.send_message(message.chat.id, text.pers_9, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.customer == text.DS_def_net_mark_kc and user.eol == text.process_subject_step_def_rabota_mark_net:
                    bot.send_message(message.chat.id, text.pers_10, parse_mode="Markdown")
                # bot.send_document(chat_id=chat_id,
                #                   document=open('alg_dir/templates/Папка 2 (п.4.1 _КТ 530)/Аналитические данные изменения стоимости договора.xlsx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 2 (п.4.1 _КТ 530)/Решение о заключении ДС.docx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 2 (п.4.1 _КТ 530)/Справка по изменению, дополнению договора.xlsx',
                #     'rb'))
                # bot.send_document(chat_id=chat_id, document=open(
                #     'alg_dir/templates/Папка 2 (п.4.1 _КТ 530)/Уведомление Инициатора о возможности изменения, дополнения договора.docx',
                #     'rb'))
            bot.send_message(message.chat.id,
                             "Шаблоны доступы на ресурсе [«Закупки. Методология»](https://poz.gazprom-neft.local) в разделе «Шаблоны» / «Дополнительные соглашения».",
                             parse_mode="Markdown")

            collection_of_statistic(user)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton(text.mark_grad)
            btn2 = types.KeyboardButton("Отправить шаблоны на почту")
            btn3 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
            msg = bot.send_message(message.chat.id, text.finish_1,
                                   reply_markup=markup, parse_mode="Markdown")

            bot.send_sticker(message.chat.id, text.finish_sti)

            bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
            bot.register_next_step_handler(msg, grad)
    if not (
            message.text == text.process_changesize1_step_def_net_mark_da or message.text == text.process_changesize1_step_def_net_mark_net
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DS_def)


def process_final_step_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Вернуться назад"):
        if user.option == None:
            user.change = None
            if user.eol == None:
                process_subject_step_def(message)
            else:
                process_eol_step_def(message)
    if ((message.text == text.process_change_step_def_net_mark_1) or (
            message.text == text.process_change_step_def_net_mark_2) or (
            message.text == text.process_change_step_def_net_mark_3) or (
            message.text == "Вернуться назад")):
        if ((message.text == text.process_change_step_def_net_mark_1) or (
                message.text == text.process_change_step_def_net_mark_2) or (
                message.text == text.process_change_step_def_net_mark_3)):
            option = message.text
            user.option = option
        collection_of_statistic(user)

        if user.change == text.process_eol_step_def_mark_net:
            if user.option == text.process_change_step_def_net_mark_1:
                bot.send_message(message.chat.id, text.pers_1_1, parse_mode="Markdown")
                bot.send_message(message.chat.id, "Шаблон не предусмотрен")
            elif user.option == text.process_change_step_def_net_mark_2:
                bot.send_message(message.chat.id, text.pers_1_2, parse_mode="Markdown")
                bot.send_message(message.chat.id, "Шаблон не предусмотрен")
            elif user.option == text.process_change_step_def_net_mark_3:
                if user.subject == text.process_customer_step_def_mark_mtr and user.customer == text.DS_def_net_mark_gpn:
                    bot.send_message(message.chat.id, text.pers_2, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_mtr and user.customer == text.DS_def_net_mark_kc:
                    bot.send_message(message.chat.id, text.pers_3, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.customer == text.DS_def_net_mark_gpn and user.eol == text.process_subject_step_def_rabota_mark_da:
                    bot.send_message(message.chat.id, text.pers_4, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.customer == text.DS_def_net_mark_gpn and user.eol == text.process_subject_step_def_rabota_mark_net:
                    bot.send_message(message.chat.id, text.pers_5, parse_mode="Markdown")
                elif user.subject == text.process_customer_step_def_mark_rabota and user.customer == text.DS_def_net_mark_kc:
                    bot.send_message(message.chat.id, text.pers_6, parse_mode="Markdown")
                # bot.send_document(chat_id=chat_id, document=open('alg_dir/templates/Папка 1 (п.3 - КТ 530)/Решение о заключении ДС.docx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open('alg_dir/templates/Папка 1 (п.3 - КТ 530)/Справка по изменению, дополнению договора.xlsx', 'rb'))
                # bot.send_document(chat_id=chat_id, document=open('alg_dir/templates/Папка 1 (п.3 - КТ 530)/Уведомление Инициатора о возможности изменения, дополнения договора.docx', 'rb'))
                bot.send_message(message.chat.id,
                                 "Шаблоны доступы на ресурсе [«Закупки. Методология»](https://poz.gazprom-neft.local) в разделе «Шаблоны» / «Дополнительные соглашения».",
                                 parse_mode="Markdown")

            if user.option == text.process_change_step_def_net_mark_1 or user.option == text.process_change_step_def_net_mark_2:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.mark_grad)
                btn2 = types.KeyboardButton("Начать заново")
                markup.add(btn1)
                markup.add(btn2)
                msg = bot.send_message(message.chat.id, text.finish_1,
                                       reply_markup=markup, parse_mode="Markdown")

                bot.send_sticker(message.chat.id, text.finish_sti)

                bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
                bot.register_next_step_handler(msg, grad)
            else:
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                btn1 = types.KeyboardButton(text.mark_grad)
                btn2 = types.KeyboardButton("Отправить шаблоны на почту")
                btn3 = types.KeyboardButton("Начать заново")
                markup.add(btn1)
                markup.add(btn2)
                markup.add(btn3)
                msg = bot.send_message(message.chat.id, text.finish_1,
                                       reply_markup=markup, parse_mode="Markdown")

                bot.send_sticker(message.chat.id, text.finish_sti)

                bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
                bot.register_next_step_handler(msg, grad)
    if not (
            message.text == text.process_change_step_def_net_mark_1 or message.text == text.process_change_step_def_net_mark_2 or message.text == text.process_change_step_def_net_mark_3
            or message.text == "Вернуться назад" or message.text == "/start" or message.text == "Начать заново"):
        msg = bot.send_message(message.chat.id, 'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
        # bot.register_next_step_handler(msg, DS_def)


#####################################################################################################################################3


# Формирование оценки пользователй

def grad(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    elif (message.text == "Отправить шаблоны на почту"):
        # markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        # btn1 = types.KeyboardButton("Начать заново")
        # markup.add(btn1)
        #
        # msg = bot.send_message(message.chat.id,
        #                        'Пожалуйста, введите адрес электронной почты:',
        #                        reply_markup=markup)
        # bot.register_next_step_handler(msg, mail)

        mail(message)
    else:
        grad = message.text

        if not (grad == text.mark_grad):
            msg = bot.send_message(message.chat.id,
                                   'Я вас не понимаю... Пожалуйста, выберите из предложенных вариантов')
            # bot.register_next_step_handler(msg, grad)
            return

        user.grad = grad

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text.smile_list[0])
        btn2 = types.KeyboardButton(text.smile_list[1])
        btn3 = types.KeyboardButton(text.smile_list[2])
        btn4 = types.KeyboardButton("Начать заново")
        markup.row(btn1, btn2, btn3)
        markup.row(btn4)
        msg = bot.send_message(message.chat.id, text.grad_smile,
                               reply_markup=markup, parse_mode="Markdown")

        bot.register_next_step_handler(msg, grad_values)


def grad_values(message):
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    else:
        chat_id = message.chat.id
        grad_values = message.text

        if grad_values == text.smile_list[0]:
            grad_values = '1'
        elif grad_values == text.smile_list[1]:
            grad_values = '2'
        elif grad_values == text.smile_list[2]:
            grad_values = '3'

        user = user_dict[chat_id]
        user.grad_values = grad_values

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать заново")
        markup.row(btn1)
        msg = bot.send_message(message.chat.id, text.komment_1, reply_markup=markup, parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.thank_for_grad_sti)

        bot.register_next_step_handler(msg, comments)


def comments(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if (message.text == "/start"):
        try:
            conn = sqlite3.connect('alg_dir/data.db')
            cur = conn.cursor()

            sqlite_insert_with_param = """INSERT INTO grade
                                  (userid, datetime, userfirstname, userlastname, val)
                                  VALUES (?, ?, ?, ?, ?);"""

            data_tuple = (user.userid, date_now(), user.userfirstname, user.userlastname, user.grad_values)
            cur.execute(sqlite_insert_with_param, data_tuple)
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        send_start(message)
    elif (message.text == "Начать заново"):
        try:
            conn = sqlite3.connect('alg_dir/data.db')
            cur = conn.cursor()

            sqlite_insert_with_param = """INSERT INTO grade
                                  (userid, datetime, userfirstname, userlastname, val)
                                  VALUES (?, ?, ?, ?, ?);"""

            data_tuple = (user.userid, date_now(), user.userfirstname, user.userlastname, user.grad_values)
            cur.execute(sqlite_insert_with_param, data_tuple)
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
        send_welcome(message)
    else:
        comments = message.text
        user.comments = comments

        try:
            conn = sqlite3.connect('alg_dir/data.db')
            cur = conn.cursor()

            sqlite_insert_with_param = """INSERT INTO grade
                                  (userid, datetime, userfirstname, userlastname, val, comments)
                                  VALUES (?, ?, ?, ?, ?, ?);"""

            data_tuple = (
                user.userid, date_now(), user.userfirstname, user.userlastname, user.grad_values, user.comments)
            cur.execute(sqlite_insert_with_param, data_tuple)
            conn.commit()
            cur.close()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать заново")
        markup.row(btn1)
        msg = bot.send_message(message.chat.id, text.thank_for_grad,
                               reply_markup=markup, parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.sti_done)

        bot.register_next_step_handler(msg, send_start)


###################################################################################################################################3

# Отправка шаблонов по почте

def mail(message):
    if (message.text == "/start"):
        send_start(message)
    elif (message.text == "Начать заново"):
        send_welcome(message)
    else:
        chat_id = message.chat.id
        user = user_dict[chat_id]

        #Здесь надо определить адрес электронной почты по ID пользователя
        user_card_p = pd.read_csv('users_card.csv', delimiter=',')
        mail = list(user_card_p.loc[user_card_p['userid']==message.chat.id]['usermail'])[0]

        user.mail = mail
        m = bot.send_message(message.chat.id, 'Это может занять некоторое время, подождите.')
        if user.change == 'Нет':
            files = ['alg_dir/templates/folder_1']
        elif user.changesize1 == 'Да':
            files = ['alg_dir/templates/folder_4']
        elif user.changesize2 == 'Да':
            files = ['alg_dir/templates/folder_3']
        elif user.changesize2 == 'Нет':
            files = ['alg_dir/templates/folder_2']

        elif user.summ == 'Нет':
            files = ['alg_dir/templates/path_1']
        elif user.summ == 'Да':
            files = ['alg_dir/templates/path_2']
        try:
            send_email(user.mail, 'Шаблоны', 'Добрый день!\n \nНаправляю обещанные шаблоны!', files)
        except:
            msg = bot.send_message(message.chat.id,
                                   'Не получается отправить письмо на указанную почту. \nПожалуйста, проверьте корректность ввода.')
            bot.register_next_step_handler(msg, mail)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text.mark_grad)
        btn2 = types.KeyboardButton("Начать заново")
        markup.add(btn1)
        markup.add(btn2)
        bot.delete_message(message.chat.id, m.id)
        msg = bot.send_message(message.chat.id, text.finish_1,
                               reply_markup=markup, parse_mode="Markdown")

        bot.send_sticker(message.chat.id, text.finish_sti)

        bot.send_message(message.chat.id, text.finish_3, parse_mode="Markdown")
        bot.send_sticker(message.chat.id, text.sti_mail)
        bot.register_next_step_handler(msg, grad)



###################################################################################################################################3

# Сохранение шагов в БД

def collection_of_statistic(user):
    try:
        conn = sqlite3.connect('alg_dir/data.db')
        cur = conn.cursor()

        sqlite_insert_with_param = """INSERT INTO stat
                              (userid, datetime, userfirstname, userlastname, startDS, MSZ, msz_step_one, msz_step_two, 
                              msz_step_two_one, msz_step_two_two, msz_step_three, DSone, DS, customer, subject, eol, 
                              сhange, option, changesize1, changesize2, EDP_start, market,
                              restr, biglist, summ, EDP_subject, EDP_eol, purch)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        data_tuple = (user.userid, date_now(), user.userfirstname, user.userlastname, user.startDS, user.MSZ,
                      user.msz_step_one, user.msz_step_two, user.msz_step_two_one, user.msz_step_two_two,
                      user.msz_step_three, user.DSone, user.DS, user.customer, user.subject, user.eol,
                      user.change, user.option, user.changesize1, user.changesize2, user.EDP_start, user.market,
                      user.restr, user.biglist, user.summ, user.EDP_subject, user.EDP_eol, user.purch)

        cur.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


def quest_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    if message.text == "Задать вопрос" or message.text == "Глоссарий" or message.text == "Отправить вопрос":
        user.take_nb = message.text
        if message.text == "Отправить вопрос":
            user.take_nb = "Задать вопрос"
        if user.take_nb == "Задать вопрос":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            msg = bot.send_message(message.chat.id, text.quest, parse_mode="Markdown", reply_markup=markup)
            # msg = bot.send_message(message.chat.id,
            #                    'Спроси меня о чем-нибудь, а я постараюсь подобрать наиболее подходящие вопросы.', reply_markup=markup)
            bot.register_next_step_handler(msg, analiz_quest_def)
        if user.take_nb == "Глоссарий":
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            msg = bot.send_message(message.chat.id, text.gloss, reply_markup=markup, parse_mode="Markdown")
            # msg = bot.send_message(message.chat.id,
            #                    'Введи термин, а я попробую дать тебе разъеснение о нем', reply_markup=markup)
            bot.register_next_step_handler(msg, analiz_glos_def)


###################################################################################################################################3

# Ветка с ответом на типовые вопрос

def analiz_quest_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    elif message.text == text.mark_grad:
        grad(message)
    elif message.text == "Отправить вопрос":
        user.send = '1'
        collection_of_statistic_quest(user)
        bot.send_message(message.chat.id, text.send_quest, parse_mode="Markdown")
        quest_def(message)
        user_card_p = pd.read_csv('users_card.csv', delimiter=',')
        email = list(user_card_p.loc[user_card_p['userid'] == message.chat.id]['usermail'])[0]
        mail_mess = str(user.quest)+'\n'+str(message.chat.id)+'\n'+str(message.chat.first_name)+' '+str(message.chat.last_name) +'\n' + email
        send_email('Bukin.NA@gazprom-neft.ru', 'Вопросы из ТГ-бота', mail_mess)
    if not ((message.text == "/start") or (message.text == "Начать заново") or (message.text == "Отправить вопрос") or (
            message.text == text.mark_grad)):
        user.send = None
        user.quest_gl = None
        user.breakk = False
        user.list_message_id = {}
        user.quest = message.text
        mess = message.text
        mess = mess.lower()
        some_texts = data_df.quest
        df = pd.DataFrame({'texts': some_texts})
        df_regr = pd.DataFrame({'texts': some_texts})
        mess = mess.replace(',', "")
        mess = mess.replace('?', "")
        mess = mess.replace('.', "")
        mess = mess.replace('"', "")
        mess = mess.replace("'", "")
        mess = mess.replace('«', "")
        mess = mess.replace('»', "")
        mess = mess.replace(')', "")
        mess = mess.replace('(', "")
        for key in config.gloss.keys():
            mess = mess.replace(key, str(config.gloss[key]))

        docmes = ppln(mess)
        mess_list = []

        # Создание списка с лемматизированными словами
        for snt in docmes.sentences:
            for word in snt.words:
                # Если слово не знак препинания, местоимение, приставка, вспомогательное слово,
                # частица, подчинительный союз или символ, то добавляем в конечное предложение
                if word.upos not in ['PUNC', 'PRON', 'ADP', 'AUX', 'PART', 'SCONJ', 'SYM', 'DET']:
                    mess_list.append(word.lemma)

        # # Предлагаем перейти на другого бота, если подходящая тема
        # if ('Дополнительный' and 'соглашение') or ('малостоящий' and 'закупка') or (
        #         'единственный' and 'поставщик') in mess_list:
        #     markupVera = types.InlineKeyboardMarkup()
        #     button1 = types.InlineKeyboardButton("Методолог Вера", url='https://t.me/Vera_Methodologist_GPN_bot')
        #     markupVera.add(button1)
        #     bot.send_message(message.chat.id, text=text.quest_Vera,
        #                      reply_markup=markupVera, parse_mode="Markdown")

        conc = []
        for quest_l in quest_list_l:
            i = 0
            quest_l.split()
            for mess in mess_list:
                if mess in quest_l.split():
                    i = i + 1
            delta = i / ((len(quest_l.split()) + len(mess_list)) * 0.5)
            conc.append(delta)

        df_regr['delta'] = conc
        df_regr = df_regr.sort_values(by=['delta'], ascending=[0])

        # Создание списка наиболее подходящих позиций
        find_max = []
        max_conc = max(conc)
        for i in range(len(conc)):
            if conc[i] == max_conc:
                find_max.append(i)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton(text.mark_send)
        btn2 = types.KeyboardButton(text.mark_grad)
        btn3 = types.KeyboardButton('Начать заново')
        markup.add(btn1)
        markup.add(btn2)
        markup.add(btn3)
        user.list_message_id = {}


        # Формирование таблицы и тремя наиболее подходящими вариантами (если они есть)

        if not max(df_regr.delta) == 0:
            var = []
            var_ = []
            data_quest = []
            prob_ = []
            for index, row in df_regr[0:3].iterrows():
                if not row['delta'] == 0:
                    prob_.append(row['delta'])
                    var.append(
                        {dq[df[df['texts'] == row['texts']].index[0]]: str(df[df['texts'] == row['texts']].index[0])})
                    var_.append({'Узнать ответ': str(df[df['texts'] == row['texts']].index[0])})
                    data_quest.append(dq[df[df['texts'] == row['texts']].index[0]])
                if row['delta'] == 1:
                    user.breakk = True
                    break

            user.fir_quest = data_quest[0]
            if len(var) == 2: user.sec_quest = data_quest[1]
            if len(var) == 3:
                user.sec_quest = data_quest[1]
                user.th_quest = data_quest[2]


            if user.breakk ==True:
                msg = bot.send_message(message.chat.id,
                                       text=da[int(var_[0]['Узнать ответ'])],
                                       reply_markup=markup)
            else:
                msg = bot.send_message(message.chat.id,
                                       text='Вот что я смогла найти:',
                                       reply_markup=markup, parse_mode="Markdown")
                for i in range(len(var)):
                    if prob_[i]*2>prob_[0]:
                        keyboard = Keyboa(items=var_[i])
                        m = bot.send_message(message.chat.id, text=var[i], reply_markup=keyboard())

                        user.list_message_id[var_[i]['Узнать ответ']] = m.id
                m = bot.send_message(message.chat.id,
                                     text=text.quest_fin, parse_mode="Markdown")
                user.list_message_id['доп'] = m.id

        else:
            msg = bot.send_message(message.chat.id, text.quest_zero, parse_mode="Markdown")
            bot.send_message(message.chat.id,
                                 text=text.quest_fin, parse_mode="Markdown")


        collection_of_statistic_quest(user)

        bot.register_next_step_handler(msg, analiz_quest_def)

# Неиспользуемый пока вариант с глоссарием (принцип работы аналогичный с предыдущей функцией)

def analiz_glos_def(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    elif message.text == text.mark_grad:
        grad(message)
    elif message.text == "Отправить вопрос":
        user.send = '1'
        collection_of_statistic_quest(user)
        bot.send_message(message.chat.id, text.send_quest)
        quest_def(message)
    if not ((message.text == "/start") or (message.text == "Начать заново") or (message.text == "Отправить вопрос") or (
            message.text == text.mark_grad)):
        user.send = None
        user.quest = None
        user.list_message_id = None
        user.quest_gl = message.text
        input_w = message.text
        input_w = input_w.lower()
        input_w = input_w.replace(',', "")
        input_w = input_w.replace('?', "")
        input_w = input_w.replace('.', "")
        input_w = input_w.replace('"', "")
        input_w = input_w.replace("'", "")
        input_w = input_w.replace('«', "")
        input_w = input_w.replace('»', "")
        input_w = input_w.replace(')', "")
        input_w = input_w.replace('(', "")
        input_w = input_w.replace('-', " ")
        input_w = input_w.replace('!', " ")

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        btn1 = types.KeyboardButton("Начать заново")
        btn2 = types.KeyboardButton(text.mark_send)
        btn3 = types.KeyboardButton(text.mark_grad)

        user.list_message_id = {}

        markup.add(btn3)
        markup.add(btn1)
        markup.add(btn2)

        msg = bot.send_message(message.chat.id, text=text.gloss_fin,
                               reply_markup=markup)

        some_texts = data_glos.pon
        df = pd.DataFrame({'texts': some_texts})
        pos = None
        var = []
        var_ = []
        for i in range(len(data_glos.ab)):
            if data_glos.ab[i] == input_w:
                pos = i


        if not pos is None:
            var.append({dga[pos]: str(pos)})
            var_.append({'Узнать ответ': str(pos)})
            user.fir_quest = str(var[0].keys())
            keyboard = Keyboa(items=var_[0])
            m = bot.send_message(message.chat.id, text=var[0], reply_markup=keyboard())
            user.list_message_id[var_[0]['Узнать ответ']] = m.id
        else:
            some_texts = data_glos.pon
            df_regr = pd.DataFrame({'texts': some_texts})

            find_nearest_to = input_w

            # формирование весов tf-idf
            tfidf = TfidfVectorizer()
            mx_tf = tfidf.fit_transform(data_glos.pon)
            new_entry = tfidf.transform([find_nearest_to])

            # расчет косинусного расстояния
            cosine_similarities = linear_kernel(new_entry, mx_tf).flatten()

            # запишем все попарные результаты сравнений
            df_regr['cos_similarities'] = cosine_similarities
            # и отсортируем по убыванию (т.к. cos(0)=1)
            df_regr = df_regr.sort_values(by=['cos_similarities'], ascending=[0])



            if not max(df_regr.cos_similarities) == 0:
                var = []
                var_ = []

                for index, row in df_regr[0:3].iterrows():
                    if not row['cos_similarities'] == 0:
                        var.append(
                            {dga[df[df['texts'] == row['texts']].index[0]]: str(
                                df[df['texts'] == row['texts']].index[0])})
                        var_.append({'Узнать ответ': str(df[df['texts'] == row['texts']].index[0])})
                user.fir_quest = str(var[0].keys())
                if len(var) == 2: user.sec_quest = str(var[1].keys())
                if len(var) == 3:
                    user.sec_quest = str(var[1].keys())
                    user.th_quest = str(var[2].keys())

                for i in range(len(var)):
                    keyboard = Keyboa(items=var_[i])
                    m = bot.send_message(message.chat.id, text=var[i], reply_markup=keyboard())
                    user.list_message_id[var_[i]['Узнать ответ']] = m.id

            else:
                bot.send_message(message.chat.id, text.gloss_zero)
        collection_of_statistic_quest(user)

        bot.register_next_step_handler(msg, analiz_glos_def)


@bot.callback_query_handler(func=lambda message: True)
def send_ans(call):
    chat_id = call.from_user.id
    user = user_dict[chat_id]

    answer = int(call.data)
    if not user.quest == None:
        bot.send_message(call.from_user.id, dq[answer])
        bot.send_message(call.from_user.id, da[answer])
        for i in user.list_message_id:
            bot.delete_message(call.from_user.id, user.list_message_id[i])

    if not user.quest_gl == None:
        bot.send_message(call.from_user.id, dga[answer])
        bot.send_message(call.from_user.id, dgq[answer])
        for i in user.list_message_id:
            bot.delete_message(call.from_user.id, user.list_message_id[i])


# Сохранение входящих и предложенных вопросов пользователю в БД

def collection_of_statistic_quest(user):
    try:
        conn = sqlite3.connect('quest_dir/data_quest.db')
        cur = conn.cursor()

        sqlite_insert_with_param = """INSERT INTO quest
                              (userid, datetime, userfirstname, userlastname, quest, fir_quest, sec_quest, th_quest, send, take_nb)
                              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

        data_tuple = (
            user.userid, date_now(), user.userfirstname, user.userlastname, user.quest, user.fir_quest, user.sec_quest,
            user.th_quest, user.send, user.take_nb)

        cur.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)


# Сохранение всех посещений начального этапа пользователями

def collection_of_statistic_summ_start(user):
    try:
        conn = sqlite3.connect('alg_dir/data.db')
        cur = conn.cursor()

        sqlite_insert_with_param = """INSERT INTO summ
                              (userid, datetime, userfirstname, userlastname)
                              VALUES (?,?,?,?);"""

        data_tuple = (user.userid, date_now(), user.userfirstname, user.userlastname)

        cur.execute(sqlite_insert_with_param, data_tuple)
        conn.commit()
        cur.close()
    except sqlite3.Error as error:
        print("Ошибка при работе с SQLite", error)

def send_email(addr_to, msg_subj, msg_text, files=None):
    addr_from = config.FROM_EMAIL
    password = config.MY_PASSWORD

    msg = MIMEMultipart()
    msg['From'] = config.FROM_EMAIL
    msg['To'] = addr_to
    msg['Subject'] = msg_subj

    body = msg_text
    msg.attach(MIMEText(body, 'plain'))

    if not files == None:
        process_attachement(msg, files)

    server = smtplib.SMTP(config.Y_SERVER, config.Y_PORT)
    server.starttls()
    server.set_debuglevel(True)
    server.login(addr_from, password)
    server.send_message(msg)
    server.quit()


# Функция по обработке списка, добавляемых к сообщению файлов
def process_attachement(msg, files):
    for f in files:
        if os.path.isfile(f):  # Если файл существует
            attach_file(msg, f)  # Добавляем файл к сообщению
        elif os.path.exists(f):  # Если путь не файл и существует, значит - папка
            dir = os.listdir(f)  # Получаем список файлов в папке
            for file in dir:  # Перебираем все файлы и...
                attach_file(msg, f + "/" + file)  # ...добавляем каждый файл к сообщению


def attach_file(msg, filepath):  # Функция по добавлению конкретного файла к сообщению
    filename = os.path.basename(filepath)  # Получаем только имя файла
    ctype, encoding = mimetypes.guess_type(filepath)  # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:  # Если тип файла не определяется
        ctype = 'application/octet-stream'  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)  # Получаем тип и подтип
    if maintype == 'text':  # Если текстовый файл
        with open(filepath) as fp:  # Открываем файл для чтения
            file = MIMEText(fp.read(), _subtype=subtype)  # Используем тип MIMEText
            fp.close()  # После использования файл обязательно нужно закрыть
    elif maintype == 'image':  # Если изображение
        with open(filepath, 'rb') as fp:
            file = MIMEImage(fp.read(), _subtype=subtype)
            fp.close()
    elif maintype == 'audio':  # Если аудио
        with open(filepath, 'rb') as fp:
            file = MIMEAudio(fp.read(), _subtype=subtype)
            fp.close()
    else:  # Неизвестный тип файла
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)  # Используем общий MIME-тип
            file.set_payload(fp.read())  # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
            encoders.encode_base64(file)  # Содержимое должно кодироваться как Base64
    file.add_header('Content-Disposition', 'attachment', filename=filename)  # Добавляем заголовки
    msg.attach(file)  # Присоединяем файл к сообщению



def mail_check_mes():
    # Connect to the IMAP server
    imap = imaplib.IMAP4_SSL("imap.mail.ru")

    # Login to the account
    imap.login(config.Y_LOGIN, config.MY_PASSWORD)

    # Select the inbox folder
    imap.select("inbox")

    # Search for all unseen emails
    status, email_ids = imap.search(None, "(UNSEEN)")

    # Infinite loop to check for new emails
    while True:
        # Search for all unseen emails
        status, email_ids = imap.search(None, "(UNSEEN)")

        # Iterate over all email IDs
        for email_id in email_ids[0].split():
            # Fetch the email
            status, email_data = imap.fetch(email_id, "(RFC822)")

            # Parse the email
            email_message = email.message_from_bytes(email_data[0][1])

            # Get the sender's email address
            sender = email.utils.parseaddr(email_message["From"])[1]

            # Get the decoded message body
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    message = part.get_payload(decode=True).decode(encoding = "utf-8",errors='ignore')

            #так как длинна id разная, а пользователь, помимо мсамого кода, может отправить другую информацию (подпись, например)
            #забираем из сообщения только числа, выдаем первое

            s = message
            l = len(s)
            integ = []
            i = 0
            while i < l:
                s_int = ''
                a = s[i]
                while '0' <= a <= '9':
                    s_int += a
                    i += 1
                    if i < l:
                        a = s[i]
                    else:
                        break
                i += 1
                if s_int != '':
                    integ.append(int(s_int))
            mail_check_info(sender, integ[0])

        # Sleep for a certain amount of time
        time.sleep(40)

    # Close the connection
    imap.close()
    imap.logout()




def send_msg_to_users(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    else:
        msg = bot.send_message(message.chat.id, text = "Напиши id пользователя", parse_mode="Markdown")
        bot.register_next_step_handler(msg, send_msg_to_users_1)

def send_msg_to_users_1(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.user_id_to_sed_msg = message.text
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    else:
        msg = bot.send_message(message.chat.id, text="Напиши сообщение пользователю", parse_mode="Markdown")
        bot.register_next_step_handler(msg, send_msg_to_users_2)

def send_msg_to_users_2(message):
    chat_id = message.chat.id
    user = user_dict[chat_id]
    user.user_msg_to_sed_msg = message.text
    if message.text == "/start":
        send_start(message)
    elif message.text == "Начать заново":
        send_welcome(message)
    else:
        if message.chat.id == 798637297:
            msg = bot.send_message(message.chat.id, text="Подключение...",
                                   parse_mode="Markdown")
            btn1 = types.KeyboardButton("Начать заново")
            markup.add(btn1)
            bot.send_message(int(user.user_id_to_sed_msg), text=message.text, parse_mode="Markdown")
            msg = bot.send_message(message.chat.id, text="Сообщение отправлено", reply_markup=markup, parse_mode="Markdown")
            bot.register_next_step_handler(msg, send_start)


thr1 = threading.Thread(target = mail_check_mes ).start()



if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, skip_pending=True)
        except Exception as e:
            time.sleep(3)
            print(e)
