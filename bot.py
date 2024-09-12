import config as cfg
import config_msg
import telebot
import sql


bot = telebot.TeleBot(cfg.TOKEN)

@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id, config_msg.start_msg)
  sql.User(message).create_user()
    
@bot.message_handler(commands=['premium'])
def premium_message(message):
  bot.send_message(message.chat.id, "В разработке...)")

def promo(message):
  out = sql.User(message).promo(message.text)
  bot.send_message(message.chat.id, out)

@bot.message_handler(commands=['promo'])
def promo_message(message):
  bot.send_message(message.chat.id, "Введите промокод")
  bot.register_next_step_handler(message, promo)

def create_promt(message):
  promt = sql.User(message).create_promt(message.text)
  bot.send_message(message.chat.id, "Введите название:")
  bot.register_next_step_handler(message, promt.set_name) 

@bot.message_handler(commands=['create_promt'])
def create_promt_message(message):
  bot.send_message(message.chat.id, "Введите роль для бота \n\nПример: \"Представь, что ты преподаватель в школе\"")
  bot.register_next_step_handler(message, create_promt)  

def set_promt(message):
  sql.User(message).set_promt(message.text)
  bot.send_message(message.chat.id, 'Вы переключились на '+message.text)

@bot.message_handler(commands=['set_promt'])
def set_promt_message(message):
  markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  data = sql.User(message).promt_list()
  for i in data:
    btn = telebot.types.KeyboardButton(i['name'])
    markup.add(btn)
  bot.send_message(message.chat.id, 'Выберите роль из списка:', reply_markup=markup)
  bot.register_next_step_handler(message, set_promt)

def del_promt(message):
  sql.User(message).del_promt(message.text)
  bot.send_message(message.chat.id, 'Вы удалили '+message.text)

@bot.message_handler(commands=['del_promt'])
def del_promt_message(message): 
  markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  data = sql.User(message).promt_list()
  for i in data:
    if i['id']==0:
      continue
    btn = telebot.types.KeyboardButton(i['name'])
    markup.add(btn)
  bot.send_message(message.chat.id, 'Выберите роль ДЛЯ УДАЛЕНИЯ из списка:', reply_markup=markup)
  bot.register_next_step_handler(message, del_promt)

'''
def load_file(message):
  file_id = message.document.file_id
  file_name = message.document.file_name
  file_path = bot.get_file(file_id).file_path
  downloaded_file = bot.download_file(file_path)
  bot.send_message(message.chat.id, "Файл успешно загружен.")

@bot.message_handler(commands=['get_file'])
def get_file_message(message):
  bot.send_message(message.chat.id, "📁Загрузите файл:")
  bot.register_next_step_handler(message, load_file)
'''

def next_query(message, memory, msg):
  bot.delete_message(message.chat.id, msg.message_id)
  if (message.text == 'Закрыть диалог'):
    return()
  
  msg = bot.send_message(message.chat.id, 'Генерация ответа...')
  otvet, memory = sql.User(message).gpt_query(message.text, memory=memory)
  bot.edit_message_text(otvet, message.chat.id, msg.message_id)

  markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  btn = telebot.types.KeyboardButton('Закрыть диалог')
  markup.add(btn)
  msg = bot.send_message(message.chat.id, 'Введите следующий вопрос:', reply_markup=markup)
  bot.register_next_step_handler(message, next_query, memory, msg)

@bot.message_handler()
def query_message(message):
  msg = bot.send_message(message.chat.id, 'Генерация ответа...')
  otvet, memory = sql.User(message).gpt_query(message.text)
  bot.edit_message_text(otvet, message.chat.id, msg.message_id)

  markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
  btn = telebot.types.KeyboardButton('Закрыть диалог')
  markup.add(btn)
  msg = bot.send_message(message.chat.id, 'Продолжим диалог?', reply_markup=markup)
  bot.register_next_step_handler(message, next_query, memory, msg)


'''
@bot.message_handler()
def query_message(message):
  msg = bot.send_message(message.chat.id, 'Генерация ответа...')
  otvet = sql.User(message).gpt_query(message.text)
  bot.edit_message_text(otvet, message.chat.id, msg.message_id)
  if otvet == config_msg.out_time_msg:
    pass
'''

bot.infinity_polling()