import requests, telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup as mk
from telebot.types import InlineKeyboardButton as btn
import os, json, requests, flask,time

server = flask.Flask(__name__)
bot = telebot.TeleBot("")
@bot.message_handler(func=lambda m:True)
def d(message):
    bot.reply_to(message,"hi")
@server.route("/bot", methods=['POST'])
def getMessage():
  bot.process_new_updates([
    telebot.types.Update.de_json(flask.request.stream.read().decode("utf-8"))
  ])
  return "!", 200


@server.route("/")
def webhook():
  bot.remove_webhook()
  link = "https://wa11sas.onrender.com"
  bot.set_webhook(url=f"{link}/bot")
  return "!", 200


server.run(host="0.0.0.0", port=os.environ.get('PORT', 5000))
server = flask.Flask(__name__)
