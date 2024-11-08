import os
import telebot
from telebot import types
from PyPDF2 import PdfMerger
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    
    # Create inline keyboard with a button that links to the developer
    markup = InlineKeyboardMarkup()
    developer_button = InlineKeyboardButton("Developer 🪷", url="https://t.me/Ur_Amit_01")
    markup.add(developer_button)
    
    # Send the welcome message with the inline keyboard
    bot.send_message(
        message.chat.id,
        "*Welcome! Send me PDF files to merge. When you're done, use /merge to combine them.😉*",
        parse_mode='Markdown'
    )
    
# Initialize bot with token from environment variable
API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

# Temporary storage for user files (dictionary to store file paths by user)
user_files = {}

# Help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = "1. Send me PDF files you want to merge.\n"
    help_text += "2. Use /merge to combine the files into one PDF.\n"
    help_text += "3. Use /clear to reset the list of files."
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
        bot.reply_to(message, f"Added {file_name} to the list for merging.")
    else:
        bot.reply_to(message, "Please send only PDF files.")

# Merge command handler
@bot.message_handler(commands=['merge'])
def merge_pdfs(message):
    user_id = message.from_user.id
    
    # Check if there are files to merge
    if user_id not in user_files or len(user_files[user_id]) < 2:
        bot.reply_to(message, "You need to send at least two PDF files before merging.")
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
        
        bot.reply_to(message, "Here is your merged PDF!")
        
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
    bot.reply_to(message, "Your file list has been cleared.")

# Run the bot
bot.polling()
