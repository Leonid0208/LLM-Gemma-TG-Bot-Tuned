import logging
import os
import requests

from time import sleep
from threading import Thread
from datetime import datetime
from database import Handler

from telegram.ext import ApplicationBuilder, ContextTypes, CallbackContext, CommandHandler, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove



logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
TG_TOKEN = os.getenv("TG_TOKEN")
DATABASE_HANDLER = Handler()


BACKEND_ADDRESS = f"{os.getenv('BACKEND_ADDRESS')}/predict"



async def answer_private(update: Update, context: CallbackContext):
    request_date = datetime.now()
    try:
        reply = requests.post(BACKEND_ADDRESS, json={"question": update.message.text}).json()
        answer = reply["answer"]
        if reply['suggest'] != None:
            reply_markup  = ReplyKeyboardMarkup([[reply['suggest']]], resize_keyboard=True, one_time_keyboard=True)
        else:
            reply_markup = ReplyKeyboardRemove()
        DATABASE_HANDLER.insert(request_date, update.message.text, answer, update.message.chat.username, update.effective_chat.id)
    except requests.exceptions.ConnectionError:
        reply_markup = ReplyKeyboardRemove()
        logging.exception("ConnectionError")
        answer = "Я облажался. Мой сервер упал."
        DATABASE_HANDLER.insert(request_date, update.message.text, None, update.message.chat.username, update.effective_chat.id)

    await update.message.reply_text(text=answer, reply_markup=reply_markup)
    DATABASE_HANDLER.flush()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_message = 'Я виртуальный помощник для абитуринтов МГТУ Станкин. Могу помочь с вопросами о проходных баллах, сроках подачи документов и многое другое.\n\nЧем я могу помочь?'
    reply_keyboard = [["Какой минимальный балл необходим для поступления на направление 'Информатика и вычислительная техника"],
                        ["Можно ли подать документы онлайн?"]]
    await update.message.reply_text(text=start_message,
                                    reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, resize_keyboard=True
        ),)


def main():
    logger.info("Bot restarted")
    app = ApplicationBuilder().token(TG_TOKEN).concurrent_updates(True).build()

    private_answer_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), answer_private)
    app.add_handler(private_answer_handler)

    comm_start = CommandHandler('start', start)
    app.add_handler(comm_start)
    
    logger.info("Ready to poll")
    app.run_polling()
    logger.info("Polling")

def saver():
    logger.info("Starting saver")
    sleep(10)

if __name__ == "__main__":
    saver_thread = Thread(target=saver)
    saver_thread.start()
    main()