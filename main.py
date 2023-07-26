import telebot
import os
from flask import Flask, request
import schedule, time, pytz
from threading import Thread
import random
from emojis import emojis
from datetime import datetime
import logging as log

log.basicConfig(level=log.INFO)
TOKEN = os.environ['API_KEY']
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)

# bot
GREET_CMDS = ['Hi', 'Hello', 'Help', 'start']


@bot.message_handler(commands=GREET_CMDS)
def greet(message):
  print(message.chat.id, ":", message.text)
  bot.send_message(message.chat.id, "Hey! I'm Roh-Bot. Hows it going?")


@bot.message_handler(func=lambda message: True)
def generic_reply(message):
  log.debug(message.chat.id, ":", message.text)
  bot.send_message(message.chat.id, random.choice(emojis))


# bot.polling()


# webhook
@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
  bot.process_new_updates(
    [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200


@server.route("/")
def webhook():
  bot.remove_webhook()
  bot.set_webhook(url='https://rohbot.mridulgain1.repl.co/' + TOKEN)
  return "Rohbot's webhook..", 200


# scheduled message
mridul_id = 5703068653
mallika_id = 5540889629
us_grp_id = -982538437


def schedule_checker():
  while True:
    schedule.run_pending()
    time.sleep(30)


def restart_aleart(id):
  log.info("scheduled job")
  bot.send_message(
    id, f"{time.asctime(time.localtime())} {random.choice(emojis)}")


TZ_KOLKATA = pytz.timezone('Asia/Kolkata')
LEAVING_DATE = datetime(2023, 7, 16, tzinfo=TZ_KOLKATA)
today = datetime.now(TZ_KOLKATA)
difference = today - LEAVING_DATE


def good_morning(id):
  msg = ("Good Morning sunshine 🌞.\n"
         f"It's been {difference.days} long days since you left Kolkata 😢")
  log.info(msg)
  bot.send_message(id, msg)


def good_night(id):
  msg = ("Good Night 🌙 dear.\nSleep well and take care!🛌🏼\n"
         f"It's been {difference.days} long days since you left Kolkata 😢\n"
         "We miss you a lot & hope to see you soon 🙏")
  log.info(msg)
  bot.send_message(id, msg)


if __name__ == "__main__":
  restart_aleart(mridul_id)
  schedule.every().day.at("18:49:59").do(good_night, id=mallika_id)
  schedule.every().day.at("18:49:59").do(good_night, id=mridul_id)
  # schedule.every().day.at("01:50").do(good_morning, id=us_grp_id)
  # schedule.every().day.at("01:30:00", TZ_KOLKATA).do(good_morning,
  #                                                    id=us_grp_id)
  # schedule.every().day.at("01:20", "Asia/Kolkata").do(good_night,
  #                                                     id=us_grp_id)
  Thread(target=schedule_checker).start()

  # run simple flask web server
  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
