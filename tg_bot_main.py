import telebot
from telebot import types
from tg_bot_token import tg_token
from tg_bot_settings import main_menu_buttons, valutes_menu, current_position

from weather_script_painter import weather_painter

from valutes_project_painter import valutes_painter
from valutes_project_settings import params_current, params_default, buttons_first_valutes, buttons_second_times

from tg_bot_logger import Logger

log = Logger()

bot = telebot.TeleBot(token=tg_token, parse_mode=None)
log.log_obj(bot)

@bot.message_handler(commands=['start'])
def start(message):
    log.log_message(message)
    log.log_position(current_position)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[types.KeyboardButton(_) for _ in main_menu_buttons])
    bot.send_message(message.chat.id, text='Hello, {0.first_name}'.format(message.from_user), reply_markup=markup)
    log.log_keyboard(markup)

@bot.message_handler(commands=['help'])
def help(message):
    log.log_message(message)
    log.log_position(current_position)
    if current_position['position'] == 'main_menu':
        bot.send_message(chat_id=message.chat.id, text='Take your choice')
    elif current_position['position'] == 'Valutes':
        bot.send_message(chat_id=message.chat.id, text='Night OFF/Night ON - change plot theme\n' \
                                                       'Drawing - Drawing plot\n' \
                                                       'Change parameters - you can choose your parameters\n' \
                                                       'Come back - back to the main menu')

@bot.message_handler(content_types=['text'])
def func(message):
    def default_button():
        current_position['layer'] = 0
        log.log_position(current_position)
        params_current['valutes'] = params_default['button_valutes']
        params_current['period'] = params_default['button_period']
        params_current['show_min_max_plot'] = params_default['show_min_max']
        params_current['night_theme'] = params_default['night_theme']
        log.log_params_current(params_current)
        picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                           period=params_current['period'], \
                                           show_min_max_plot=params_current['show_min_max_plot'], \
                                           night_theme=params_current['night_theme'])
        log.log_picture(picture)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(*[types.KeyboardButton(_) for _ in valutes_menu])
        if picture != None:
            bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
        else:
            bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
        log.log_keyboard(markup)

    log.log_message(message)
    log.log_position(current_position)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if current_position['position'] == 'main_menu':
        if message.text == 'Weather':
            bot.send_message(chat_id=message.chat.id, text='Waiting...')
            media = weather_painter()

            log.log_picture(media)

            if not media:
                bot.send_message(chat_id=message.chat.id, text='Больше 10 графиков!')
            else:
                bot.send_media_group(chat_id=message.chat.id, media=media)

        if message.text == 'Valutes':
            current_position['position'] = 'Valutes'
            log.log_params_current(params_current)
            picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                               period=params_current['period'], \
                                               show_min_max_plot=params_current['show_min_max_plot'], \
                                               night_theme=params_current['night_theme'])
            log.log_picture(picture)
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add(*[types.KeyboardButton(_) for _ in valutes_menu])
            if picture != None:
                bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
            else:
                bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
            log.log_keyboard(markup)
    elif current_position['position'] == 'Valutes':
        if current_position['layer'] == 0:
            if message.text == 'Night OFF':
                valutes_menu[0] = 'Night ON'
                params_current['night_theme'] = True
                log.log_params_current(params_current)
                picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                                   period=params_current['period'], \
                                                   show_min_max_plot=params_current['show_min_max_plot'], \
                                                   night_theme=params_current['night_theme'])
                log.log_picture(picture)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*[types.KeyboardButton(_) for _ in valutes_menu])
                if picture != None:
                    bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
                else:
                    bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
                log.log_keyboard(markup)
            elif message.text == 'Night ON':
                valutes_menu[0] = 'Night OFF'
                params_current['night_theme'] = False
                log.log_params_current(params_current)
                picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                                   period=params_current['period'], \
                                                   show_min_max_plot=params_current['show_min_max_plot'], \
                                                   night_theme=params_current['night_theme'])
                log.log_picture(picture)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*[types.KeyboardButton(_) for _ in valutes_menu])
                if picture != None:
                    bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
                else:
                    bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
                log.log_keyboard(markup)
            elif message.text == 'Drawing':
                log.log_params_current(params_current)
                picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                                   period=params_current['period'], \
                                                   show_min_max_plot=params_current['show_min_max_plot'], \
                                                   night_theme=params_current['night_theme'])
                log.log_picture(picture)
                if picture != None:
                    bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
                else:
                    bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
            elif message.text == 'Change parameters':
                current_position['layer'] = 1
                log.log_position(current_position)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                default = types.KeyboardButton('Default')
                markup.add(default, *[types.KeyboardButton(_) for _ in buttons_first_valutes])
                bot.send_message(chat_id=message.chat.id, text='Choose valute', reply_markup=markup)
                log.log_keyboard(markup)
            elif message.text == 'Come back':
                current_position['position'] = 'main_menu'
                log.log_position(current_position)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*[types.KeyboardButton(_) for _ in main_menu_buttons])
                bot.send_message(chat_id=message.chat.id, text='You back to main menu', reply_markup=markup)
                log.log_keyboard(markup)
        elif current_position['layer'] == 1:
            if message.text in buttons_first_valutes:
                current_position['layer'] = 2
                log.log_position(current_position)
                params_current['valutes'] = message.text
                log.log_params_current(params_current)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                default = types.KeyboardButton('Default')
                markup.add(default, *[types.KeyboardButton(_) for _ in buttons_second_times])
                bot.send_message(chat_id=message.chat.id, text='Choose period', reply_markup=markup)
                log.log_keyboard(markup)
            elif message.text == 'Default':
                default_button()
        elif current_position['layer'] == 2:
            if message.text in buttons_second_times:
                current_position['layer'] = 0
                log.log_position(current_position)
                params_current['period'] = message.text
                log.log_params_current(params_current)
                picture, caption = valutes_painter(valutes=params_current['valutes'], \
                                                   period=params_current['period'], \
                                                   show_min_max_plot=params_current['show_min_max_plot'], \
                                                   night_theme=params_current['night_theme'])
                log.log_picture(picture)
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                markup.add(*[types.KeyboardButton(_) for _ in valutes_menu])
                if picture != None:
                    bot.send_photo(chat_id=message.chat.id, photo=picture, caption=caption, reply_markup=markup)
                else:
                    bot.send_message(chat_id=message.chat.id, text=caption, reply_markup=markup)
                log.log_keyboard(markup)
            elif message.text == 'Default':
                default_button()

bot.infinity_polling()
