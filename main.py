import os
import random
import telebot
import schedule, time
import logging
import openai

from threading import Thread
from flask import Flask, request
from emojis import emojis
from personal import (MRIDUL_ID, MALLIKA_ID, gd_morning, gd_night)

# logging
log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
# bot instance
TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
openai.api_key = os.environ['OPENAI_TOKEN']
bot = telebot.TeleBot(token=TELEGRAM_TOKEN)
# simple web server
server = Flask(__name__)
# miscellaneous


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
  if MRIDUL_ID != message.chat.id:
    bot.send_message(MRIDUL_ID, str(d))


@bot.message_handler(commands=['Hi', 'Hello', 'start'])
def greet(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id,
                   "Hey! I'm Rohan's Personal Bot 🤖 How's it going?")


@bot.message_handler(commands=['help', 'Help'])
def help(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  msg = ("Send a prompt to chat GPT:\n"
         "`/rohbot <prompt>`")
  bot.send_message(message.chat.id, msg, parse_mode="Markdown")


@bot.message_handler(commands=['support'])
def support(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id, "maintainer: @mridulgain")


def get_completion(prompt, model="gpt-3.5-turbo"):
  messages = [{"role": "user", "content": prompt}]
  response = openai.ChatCompletion.create(
    model=model,
    messages=messages,
    temperature=0,
  )
  return response.choices[0].message["content"]


def ai_reply(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_chat_action(message.chat.id, "typing")
  bot_response = get_completion(message.text)
  log.debug(bot_response)
  bot.send_message(message.chat.id, bot_response, parse_mode="Markdown")


@bot.message_handler(commands=['rohbot', 'Rohbot'])
@bot.message_handler(func=lambda message: True)
def reply(message):
  ai_reply(message)


@bot.message_handler(commands=['emoji', 'Emoji'])
def emoji(message):
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
  time_stamp = f"{time.asctime(time.localtime())} {random.choice(emojis)}"
  bot.send_message(id, time_stamp)


def send_message(id, msg):
  log.info(msg)
  bot.send_message(id, msg)


if __name__ == "__main__":
  restart_aleart(MRIDUL_ID)
  # night
  schedule.every().day.at("17:49:30").do(send_message,
                                         id=MALLIKA_ID,
                                         msg=gd_night())
  schedule.every().day.at("17:49:30").do(send_message,
                                         id=MRIDUL_ID,
                                         msg=gd_night())
  # morning
  # schedule.every().day.at("01:40").do(send_message,
  #                                     id=MRIDUL_ID,
  #                                     msg=gd_morning())
  # schedule.every().day.at("01:40").do(send_message,
  #                                     id=MALLIKA_ID,
  #                                     msg=gd_morning())
  # test
  # schedule.every(10).seconds.do(send_message, id=MRIDUL_ID, msg=gd_night())
  Thread(target=schedule_checker).start()

  # run simple flask web server
  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
