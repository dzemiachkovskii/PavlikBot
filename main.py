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
    return True


def get_quotes(query):
    msg: str = query.query
    queried_words = msg.split()
    results = []

    tree = ET.parse('quotes.xml')
    root = tree.getroot()

    i = 0
    for season in root:
        for episode in season:
            for quote in episode:
                if simillar(queried_words, quote.attrib['desc']):
                    path = '\\'.join([node.attrib['path'] for node in (root, season, episode, quote)])
                    print(path)
                    i += 1
    # result = tb.types.InlineQueryResultArticle(i, char.upper(), tb.types.InputTextMessageContent(char.lower()))
    # results.append(result)
    return results


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(inline_query):
    try:
        results = get_quotes(inline_query)
        if results:
            bot.answer_inline_query(inline_query.id, results)
    except Exception as e:
        logger.error(e)


bot.infinity_polling()
