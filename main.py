import telebot
import os
from flask import Flask, request
import schedule, time
from threading import Thread


TOKEN = os.environ['API_KEY']
bot = telebot.TeleBot(token=TOKEN)
server = Flask(__name__)


# bot
GREET_CMDS = ['Hi', 'Hello', 'Help', 'start']
@bot.message_handler(commands=GREET_CMDS)
def greet(message):
  bot.send_message(message.chat.id, "Hey! I'm Roh-Bot. Hows it going?")


@bot.message_handler(func=lambda message: True)
def generic_reply(message):
  print(message.chat.id, ":", message.text)
  bot.send_message(message.chat.id,
                   "My dev hasn't taught me how to reply this.. yet!")


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
mridul_id=5703068653
# mallika_id=5540889629

def schedule_checker():
  while True:
    schedule.run_pending()
    time.sleep(30)
    
def job(id):
  bot.send_message(id, time.asctime(time.localtime()))
  
if __name__ == "__main__":
  schedule.every(59).seconds.do(job, id=mridul_id)
  Thread(target=schedule_checker).start()
  
  server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
