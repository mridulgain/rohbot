import telebot
import os
from flask import Flask, request
import schedule, time
from threading import Thread
import random
from emojis import emojis

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
  print(message.chat.id, ":", message.text)
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


def job(id):
  bot.send_message(
    id,
    time.asctime(time.localtime()) + "\t" + random.choice(emojis))


def good_morning(id):
  bot.send_message(
    id, "Good morning sunshine 🌞. It's been %d days away from Rohan 😢")


if __name__ == "__main__":
  schedule.every(7).minutes.do(job, id=mridul_id)
  schedule.every().day.at("06:37", "Asia/Kolkata").do(good_morning,
                                                      id=mallika_id)
  schedule.every().day.at("06:00", "Asia/Kolkata").do(good_morning,
                                                      id=us_grp_id)
  Thread(target=schedule_checker).start()

  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
