import os
import telebot
from telebot import types
from PyPDF2 import PdfMerger
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Fetch the bot token from the environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Ensure the token is loaded
if not BOT_TOKEN:
    raise ValueError("No bot token provided. Please set the BOT_TOKEN environment variable.")

bot = telebot.TeleBot(BOT_TOKEN)

#start

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Replace 'YOUR_STICKER_FILE_ID' with the actual file ID of the sticker
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    
    # Send the sticker and get the message ID
    sent_sticker = bot.send_sticker(message.chat.id, sticker_id)
    sticker_message_id = sent_sticker.message_id
    
    # Wait for 3 seconds
    time.sleep(3)
    
    # Delete the sticker message
    bot.delete_message(message.chat.id, sticker_message_id)
    
# Function to create the "Start" menu with buttons
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(row_width=2)
    
    # Button for developer link
    dev_button = types.KeyboardButton('Developer Link')
    
    # Button for Help
    help_button = types.KeyboardButton('Help')
    
    markup.add(dev_button, help_button)
    
    bot.send_message(message.chat.id, "*Welcome💓✨\n• ɪ ᴄᴀɴ ᴍᴇʀɢᴇ ᴘᴅғs (Mᴀx= 20ᴍʙ ᴘᴇʀ ғɪʟᴇ)\n» Send me PDF files 📕 to merge. When you're done, send /merge to combine them.😉\n\n• ʜɪᴛ /help ᴛᴏ ᴋɴᴏᴡ ᴍᴏʀᴇ*", reply_markup=markup)

# Function to handle the "Developer Link" button
@bot.message_handler(func=lambda message: message.text == "Developer 🪷")
def send_developer_link(message):
    bot.send_message(message.chat.id, "Here is the developer's link: https://t.me/Ur_Amit_01")

# Function to handle the "Help" button
@bot.message_handler(func=lambda message: message.text == "Help 🤖")
def show_help(message):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    
    # Button for Back to Start
    back_button = types.KeyboardButton('Back to Start ⬅️')
    
    markup.add(back_button)
    
    help_text = """
    This is the help page.
    • Send me PDF files you want to merge.
    • Use /merge to combine the files into one PDF.
    • Use /clear to reset the list of files (Recommend when you start to merge new files).
    Here you can get information about how to use the bot.
    """
    
    bot.send_message(message.chat.id, help_text, reply_markup=markup)

# Function to handle the "Back to Start" button
@bot.message_handler(func=lambda message: message.text == "Back to Start")
def back_to_start(message):
    start(message)  # Calls the start function to show the main menu again

# Temporary storage for user files (dictionary to store file paths by user)
user_files = {}

# Help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = "• Send me PDF files you want to merge.\n"
    help_text += "• Use /merge to combine the files into one PDF.\n"
    help_text += "• Use /clear to reset the list of files (Recommend when you start to merge new files)."
    bot.reply_to(message, help_text)

# Handler for received documents (PDFs)
@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Check if the file is a PDF
    if message.document.mime_type == 'application/pdf':
        # Ensure directory for each user
        user_id = message.from_user.id
        if user_id not in user_files:
            user_files[user_id] = []
        
        # Get the file info and download it
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Save the file with a unique name
        file_name = f"{message.document.file_name}"
        with open(file_name, 'wb') as new_file:
            new_file.write(downloaded_file)
        
        # Store file path in user's file list
        user_files[user_id].append(file_name)
        bot.reply_to(message, f"Added {file_name} to the list for merging, send /merge when you're done ✅.")
    else:
        bot.reply_to(message, "Please send only PDF files 💔")

# Merge command handler
@bot.message_handler(commands=['merge'])
def merge_pdfs(message):
    user_id = message.from_user.id
    
    # Check if there are files to merge
    if user_id not in user_files or len(user_files[user_id]) < 2:
        bot.reply_to(message, "You need to send at least two PDF files 📕 before merging.")
        return
    
    # Create a PdfMerger object
    merger = PdfMerger()
    try:
        # Append each PDF file for merging
        for pdf_file in user_files[user_id]:
            merger.append(pdf_file)
        
        # Output merged file
        merged_file_name = f"{user_id}_merged.pdf"
        with open(merged_file_name, "wb") as merged_file:
            merger.write(merged_file)
        
        # Send the merged PDF back to the user
        with open(merged_file_name, "rb") as merged_file:
            bot.send_document(message.chat.id, merged_file)
        
        bot.reply_to(message, "Here is your merged PDF 📕😎")
        
        # Clean up merged file
        os.remove(merged_file_name)
    finally:
        # Cleanup each user's files after merging
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []

# Clear command to reset files
@bot.message_handler(commands=['clear'])
def clear_files(message):
    user_id = message.from_user.id
    if user_id in user_files:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []
    bot.reply_to(message, "Your file list has been cleared 🧹.")

# Run the bot
bot.polling()
