import telebot
import os
from flask import Flask, request
import schedule, time, pytz
from threading import Thread
import random
from emojis import emojis
from datetime import datetime
import logging
import openai, os


# logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
# bot instance
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
openai.api_key = os.environ['OPENAI_TOKEN']
bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
# simple web server
server = Flask(__name__)
# miscellaneous
mridul_id = 5703068653


def send_log(message):
  d = {}
  if message.chat.id < 0:
    # group
    log.info("message from group")
    d["group_id"] = message.chat.id
    d["group_name"] = message.chat.title
  else:
    log.info("message from user")
  # user
  d["user_id"] = message.from_user.id
  d["user_name"] = message.from_user.username
  d["msg"] = message.text
  log.debug(d)
  if mridul_id != message.chat.id:
    bot.send_message(mridul_id, str(d))


@bot.message_handler(commands=['Hi', 'Hello', 'start'])
def greet(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id, "Hey! I'm Roh-Bot. How's it going?")


@bot.message_handler(commands=['help', 'Help'])
def help(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  msg = ("Usage:\n"
    "`/rohbot <prompt>`: use chatgpt integration to ask a question")
  bot.send_message(message.chat.id, msg)


@bot.message_handler(commands=['support'])
def help(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id, "please contact my maintainer: @mridulgain")

  
def get_completion(prompt, model="gpt-3.5-turbo"):
  messages = [{"role": "user", "content": prompt}]
  response = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=0,
  )
  return response.choices[0].message["content"]


@bot.message_handler(commands=['rohbot', 'Rohbot'])
def ai_reply(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot_response = get_completion(message.text)
  log.debug(bot_response)
  bot.send_message(message.chat.id, bot_response)


@bot.message_handler(func=lambda message: True)
def generic_reply(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id, random.choice(emojis))


# bot.polling()


# webhook
@server.route('/' + TELEGRAM_TOKEN, methods=['POST'])
def getMessage():
  bot.process_new_updates(
    [telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
  return "!", 200


@server.route("/")
def webhook():
  bot.remove_webhook()
  bot.set_webhook(url='https://rohbot.mridulgain1.repl.co/' + TELEGRAM_TOKEN)
  return "🤖 Rohbot's webhook..", 200


# scheduled message
mallika_id = 5540889629
us_grp_id = -982538437


def schedule_checker():
  while True:
    t = schedule.idle_seconds()
    log.debug(f"next job after {t} seconds")
    if t is None:
      # no jobs in queue
      break
    else:
      time.sleep(t)
    schedule.run_pending()


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
  msg = ("Good Night 🌙 dear.\nSleep well and take care! 🛌🏼\n"
         f"It's been {difference.days} long days since you left Kolkata. 😢"
         "We miss you a lot & hope to see you soon 🙏")
  log.info(msg)
  bot.send_message(id, msg)


if __name__ == "__main__":
  restart_aleart(mridul_id)
  schedule.every().day.at("17:49:59").do(good_night, id=mallika_id)
  schedule.every().day.at("17:49:59").do(good_night, id=mridul_id)
  schedule.every().day.at("03:50").do(good_morning, id=us_grp_id)
  # schedule.every().day.at("01:30:00", TZ_KOLKATA).do(good_morning,
  #                                                    id=us_grp_id)
  # schedule.every().day.at("01:20", "Asia/Kolkata").do(good_night,
  #                                                     id=us_grp_id)
  Thread(target=schedule_checker).start()

  # run simple flask web server
  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
