import logging
import os

import telebot as tb

API_TOKEN = os.environ.get('PAVLIK_API_TOKEN')

logger = tb.logger
logger.setLevel(logging.INFO)

bot = tb.TeleBot(API_TOKEN)


def get_quotes(query):
    msg: str = query.query
    words = msg.split()
    results = []

    # здесь итерируемся по описаниям мп3 файлов и если находим похожие слова — добавляем путь к мп3шке в results
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
