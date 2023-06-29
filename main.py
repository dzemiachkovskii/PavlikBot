import logging
import os
import re
import xml.etree.ElementTree as ET

import telebot as tb

logger = tb.logger
logger.setLevel(logging.INFO)

ADMIN_UID = os.environ.get('PAVLIK_BOT_ADMIN_UID')
API_TOKEN = os.environ.get('PAVLIK_BOT_TOKEN')
if not API_TOKEN:
    logger.fatal('Telegram Bot API token is not defined in environment variables')
    exit(1)
if not ADMIN_UID:
    logger.fatal('Admin UID is not defined in environment variables')
    exit(2)

bot = tb.TeleBot(API_TOKEN)


def similar(query, quote):
    for query_word in query:
        if query_word.lower() in re.findall(r'\w+', quote.lower()):
            return True
    return False


def get_quotes(query):
    queried_words = query.lower().split()
    quotes = []

    tree = ET.parse('quotes.xml')
    resources = tree.getroot()

    i = 0
    for season in resources:
        for episode in season:
            for quote in episode:
                quote_text = quote.attrib['desc']
                if similar(queried_words, quote_text):
                    file_id = quote.attrib['file_id']
                    name = quote_text[:quote_text.find('%')]
                    result = tb.types.InlineQueryResultCachedVoice(i, file_id, name)
                    quotes.append(result)
                    i += 1

    return quotes


def send_big_message(cid, msg):
    if len(msg) > 4096:
        gap_index = msg[:4096].rfind('\n')
        cropped_msg = msg[:gap_index]
        bot.send_message(cid, cropped_msg, parse_mode='HTML')
        send_big_message(cid, msg[gap_index:])
    else:
        bot.send_message(cid, msg, parse_mode='HTML')


@bot.message_handler(commands=['start'])
def start(m):
    msg = 'Здарова, братиш!\n\n' \
          'Чтобы воспользоваться ботом, введи в любом чате @NarcoPavlikBot и фразу, которую хочешь отправить.' \
          'Бот предложит варианты голосовых сообщений, которые доступны для отправки.\n\n' \
          'Также ты можешь воспользоваться командой /list, чтобы посмотреть все доступные на данный момент фразы.'
    bot.send_message(m.chat.id, msg)


@bot.message_handler(commands=['list'])
def print_list(m):
    msg = ''

    tree = ET.parse('quotes.xml')
    resources = tree.getroot()

    total_count = 0
    for season in resources:
        msg += f'                <b>{season.attrib["id"]} СЕЗОН:</b>\n'
        for episode in season:
            msg += f'        <b>{episode.attrib["id"]} СЕРИЯ:</b>\n'
            i = 1
            for quote in episode:
                text = quote.attrib['desc']
                text = text[:text.find('%')]  # cutting extra words used for search
                msg += f'{str(i)}. <pre>{text}</pre>\n\n'
                i += 1
                total_count += 1
    msg = f'<b>Всего цитат: {total_count}</b>\n\n' + msg

    send_big_message(m.chat.id, msg)


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query):
    try:
        quotes = get_quotes(inline_query.query)
        if quotes:
            bot.answer_inline_query(inline_query.id, quotes)
    except Exception as e:
        logger.error(e)


@bot.message_handler(content_types=['voice'])  # to get file id's
def get_file_id(m):
    if str(m.chat.id) == ADMIN_UID:
        bot.send_message(m.chat.id, m.voice.file_id, reply_to_message_id=m.message_id)


bot.infinity_polling()
