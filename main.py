import telebot
import os
from flask import Flask, request
import schedule, time, pytz
from threading import Thread
import random
from emojis import emojis
from datetime import datetime
import logging
import openai
from personal import(
  MRIDUL_ID,
  MALLIKA_ID,
  US_GRP_ID,
  GD_MORNING,
  GD_NIGHT
)

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
  bot.send_message(message.chat.id, "Hey! I'm Rohan's Personal Bot 🤖 How's it going?")


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
  bot.send_message(message.chat.id, bot_response)


@bot.message_handler(commands=['rohbot', 'Rohbot'])
def reply(message):
  ai_reply(message)


@bot.message_handler(commands=['emoji'])
def emoji(message):
  log.debug(f"{message.chat.id} : {message.text}")
  send_log(message)
  bot.send_message(message.chat.id, random.choice(emojis))
  
@bot.message_handler(func=lambda message: True)
def reply(message):
  ai_reply(message)


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


def good_morning(id):
  log.info(GD_MORNING)
  bot.send_message(id, GD_MORNING)


def good_night(id):
  log.info(GD_NIGHT)
  bot.send_message(id, GD_NIGHT)


if __name__ == "__main__":
  restart_aleart(MRIDUL_ID)
  schedule.every().day.at("17:49:59").do(good_night, id=MALLIKA_ID)
  schedule.every().day.at("17:49:59").do(good_night, id=MRIDUL_ID)
  schedule.every().day.at("06:20").do(good_morning, id=US_GRP_ID)
  # schedule.every().day.at("01:30:00", TZ_KOLKATA).do(good_morning,
  #                                                    id=US_GRP_ID)
  # schedule.every().day.at("01:20", "Asia/Kolkata").do(good_night,
  #                                                     id=US_GRP_ID)
  Thread(target=schedule_checker).start()

  # run simple flask web server
  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
