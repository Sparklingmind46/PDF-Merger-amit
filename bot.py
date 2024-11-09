import os
import telebot
from flask import Flask, request
from telebot import types
from PyPDF2 import PdfMerger
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Fetch the bot token from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure the token is loaded
if not BOT_TOKEN:
    raise ValueError("No bot token provided. Please set the BOT_TOKEN environment variable.")

bot = telebot.TeleBot(BOT_TOKEN)
user_files = {}

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    sent_sticker = bot.send_sticker(message.chat.id, sticker_id)
    sticker_message_id = sent_sticker.message_id
    time.sleep(3)
    bot.delete_message(message.chat.id, sticker_message_id)

    photo_url = 'https://envs.sh/AfO.jpg'
    caption = "Welcome💓✨\n• I can merge PDFs (Max= 20MB per file). Send PDF files 📕 to merge and use /merge when ready."
    bot.send_photo(message.chat.id, photo_url, caption=caption)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    help_button = types.KeyboardButton('Help ⚙️')
    about_button = types.KeyboardButton('About 👀')
    dev_button = types.KeyboardButton('Developer 🪷')
    markup.add(help_button, about_button)
    markup.add(dev_button)

    bot.send_message(
        message.chat.id,
        "*Welcome💓✨\n• I can merge PDFs (Max= 20MB per file). Send PDF files 📕 to merge and use /merge to combine.*",
        reply_markup=markup
    )

@bot.message_handler(func=lambda message: message.text == "Help")
def show_help(message):
    help_text = """
    This is the help page.
    • Send PDF files you want to merge.
    • Use /merge to combine the files.
    • Use /clear to reset the file list.
    """
    bot.send_message(message.chat.id, help_text)

@bot.message_handler(func=lambda message: message.text == "About")
def show_about(message):
    about_text = """
    <b>⍟───[ My Details ]───⍟</b>
    ‣ My name: <a href=https://t.me/{}>{}</a>
    ‣ Developer: <a href='https://t.me/ur_amit_01'>Tech VJ</a>
    ‣ Library: <a href='https://docs.pyrogram.org/'>Pyrogram</a>
    """
    bot.send_message(message.chat.id, about_text, parse_mode="HTML")

@bot.message_handler(func=lambda message: message.text == "Developer")
def send_developer_link(message):
    bot.send_message(message.chat.id, "Here's the developer's link: https://t.me/Ur_Amit_01")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.document.mime_type == 'application/pdf':
        user_id = message.from_user.id
        if user_id not in user_files:
            user_files[user_id] = []

        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        file_name = f"{message.document.file_name}"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)

        user_files[user_id].append(file_name)
        bot.reply_to(message, f"Added {file_name} to the list for merging. Use /merge when ready.")
    else:
        bot.reply_to(message, "Please send only PDF files.")

@bot.message_handler(commands=['merge'])
def merge_pdfs(message):
    user_id = message.from_user.id
    if user_id not in user_files or len(user_files[user_id]) < 2:
        bot.reply_to(message, "You need to send at least two PDF files before merging.")
        return

    merger = PdfMerger()
    try:
        for pdf_file in user_files[user_id]:
            merger.append(pdf_file)

        merged_file_name = f"{user_id}_merged.pdf"
        with open(merged_file_name, "wb") as merged_file:
            merger.write(merged_file)

        with open(merged_file_name, "rb") as merged_file:
            bot.send_document(message.chat.id, merged_file)

        bot.reply_to(message, "*Here is your merged PDF*")
        os.remove(merged_file_name)
    finally:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []

@bot.message_handler(commands=['clear'])
def clear_files(message):
    user_id = message.from_user.id
    if user_id in user_files:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []
    bot.reply_to(message, "Your file list has been cleared.")
    
# Run bot
    bot.polling()
