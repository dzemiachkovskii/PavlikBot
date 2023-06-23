import logging
import os
import xml.etree.ElementTree as ET

import telebot as tb

logger = tb.logger
logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get('PAVLIK_API_TOKEN')
if not API_TOKEN:
    logger.fatal('Telegram Bot API Token is not defined in environment variables')
    exit(1)

bot = tb.TeleBot(API_TOKEN)


def simillar(query, quote):
    for word in query:
        if word in quote:
            return True
    return False


def get_quotes(query):
    queried_words = query.lower().split()
    quotes = []

    tree = ET.parse('quotes.xml')
    root = tree.getroot()

    i = 0
    for season in root:
        for episode in season:
            for quote in episode:
                if simillar(queried_words, quote.attrib['text']):
                    path = '\\'.join([node.attrib['path'] for node in (root, season, episode, quote)])
                    with open(path, 'rb') as f:
                        pass
                    result = tb.types.InlineQueryResultCachedVoice(i, 'VOICE FILE ID', quote.attrib['text'])
                    # how do i upload a voice to telegram server and add it like an InlineQueryResultCachedVoice...
                    quotes.append(result)
                    print(path)
                    i += 1

    return quotes


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query):
    try:
        quotes = get_quotes(inline_query.query)
        if quotes:
            bot.answer_inline_query(inline_query.id, quotes)
    except Exception as e:
        logger.error(e)


bot.infinity_polling()
