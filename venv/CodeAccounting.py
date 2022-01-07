import telebot
from telebot import types
from datetime import timedelta, date
from datetime import datetime
from threading import Thread
import schedule
import time
from time import sleep

bot = telebot.TeleBot('1138419356:AAH5VitwXkiIZ9pZJRi0Gyz8601HPiM3yLY')
CHAT_ID = -627885966
CONS_WEEK_LIMIT = 10000
TXT_FILE = 'accounting_database.txt'
total_accounting_dict = {}
week_limit = 10000

def convert_date(day):
    converted_date = str(day)[8:] + '.' + str(day)[5:7] + '.' + str(day)[:4]
    return converted_date

def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)

def week_result():
    global week_limit
    global monday_date
    global sunday_date
    global CHAT_ID
    if (CONS_WEEK_LIMIT - week_limit) > CONS_WEEK_LIMIT:
        week_result_text = 'За неделю с ' + monday_date + ' по ' + sunday_date + ' было потрачено ' + str(CONS_WEEK_LIMIT - week_limit) + ' рублей.' + \
                            '\nЛимит превышен на ' + str(abs(week_limit)) + ' рублей.'
        saved_money = 0
    elif (CONS_WEEK_LIMIT - week_limit) < CONS_WEEK_LIMIT:
        week_result_text = 'За неделю с ' + monday_date + ' по ' + sunday_date + ' было потрачено ' + str(CONS_WEEK_LIMIT - week_limit) + ' рублей.' + \
                            '\nВы сэкономили ' + str(week_limit) + ' рублей.' + '\n' + str(week_limit) + ' рублей перенесены на следующую неделю.'
        saved_money = week_limit
    else:
        week_result_text = 'За неделю с ' + monday_date + ' по ' + sunday_date + ' было потрачено ' + str(CONS_WEEK_LIMIT - week_limit) + ' рублей.'
        saved_money = 0
    total_accounting_dict[monday_date + '-' + sunday_date] = CONS_WEEK_LIMIT - week_limit
    with open(TXT_FILE, 'a') as file:
        write_text = monday_date + '-' + sunday_date + ':' + str(CONS_WEEK_LIMIT - week_limit) +"\n"
        file.write(write_text)
    week_limit = CONS_WEEK_LIMIT + saved_money
    monday_date = convert_date(date.today())
    sunday_date = convert_date(date.today() + timedelta(days=6))
    return bot.send_message(chat_id=CHAT_ID, text=week_result_text)

monday = date.today() - timedelta(days=date.today().isoweekday()-1)
sunday = monday + timedelta (days=6)
monday_date = convert_date(monday)
sunday_date = convert_date(sunday)

schedule.every(2).minutes.do(week_result)
#schedule.every().monday.at("0:05").do(week_result)
Thread(target=schedule_checker).start()

@bot.message_handler(content_types=['text'])
def handle_message(message):
    if message.text == '/stats' or message.text == '/stats@AvolkBot':
        keyboard = types.InlineKeyboardMarkup()
        key_4weeks = types.InlineKeyboardButton(text='Статистика за последние 4 недели', callback_data='stats_4weeks')
        keyboard.add(key_4weeks)
        key_all_time = types.InlineKeyboardButton(text='Статистика за все время', callback_data='stats_all_time')
        keyboard.add(key_all_time)
        #bot.send_message(chat_id=-62788596, text='Укажите период, за который необходимо вывести информацию:', reply_markup=keyboard)
        bot.reply_to(message, message.json['from']['first_name'] + ', укажите период, за который необходимо вывести информацию:', reply_markup=keyboard)
    else:
        try:
            int_value = int(message.text)
            global week_limit
            week_limit = week_limit - int_value
            print(week_limit)
            bot.reply_to(message, message.json['from']['first_name'] + ', остаток на неделю с ' +
                        monday_date + ' по ' + sunday_date + ' составляет ' + str(week_limit))
            
        except ValueError:
            bot.reply_to(message, message.json['from']['first_name'] + ', введи, пожалуйста, число')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'stats_4weeks':
        with open(TXT_FILE) as file:
            lines = file.read().splitlines()
        stats_text = 'Cтатистика за последние 4 недели:'
        for item in lines[-4:]:
            week_info = item.split(':')
            stats_text += '\nЗа период ' + week_info[0] + ' было потрачено ' + week_info[1] + ' рублей'
        bot.send_message(call.message.chat.id, stats_text)
    elif call.data == 'stats_all_time':
        with open(TXT_FILE) as file:
            lines = file.read().splitlines()
        stats_text = 'Cтатистика за все время:'
        for item in lines:
            week_info = item.split(':')
            stats_text += '\nЗа период ' + week_info[0] + ' было потрачено ' + week_info[1] + ' рублей'
        bot.send_message(call.message.chat.id, stats_text)
bot.infinity_polling()