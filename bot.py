import os
import telebot
from PyPDF2 import PdfMerger

# Get the bot token from environment variables
API_TOKEN = os.getenv("TELEGRAM_API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Dictionary to keep track of user-uploaded PDFs
user_pdfs = {}

# Start command
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Hello! Send me multiple PDF files, and I'll merge them into one. Use /merge when you're ready.")

# Handle PDF files
@bot.message_handler(content_types=['document'])
def handle_pdf(message):
    if message.document.mime_type == 'application/pdf':
        file_id = message.document.file_id
        user_id = message.from_user.id

        # Ensure the user's PDF list exists
        if user_id not in user_pdfs:
            user_pdfs[user_id] = []

        # Download and store the PDF
        file_info = bot.get_file(file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        user_pdfs[user_id].append(downloaded_file)
        bot.reply_to(message, "PDF received! Send more or type /merge to combine them.")
    else:
        bot.reply_to(message, "Please send a PDF file.")

# Merge PDFs when the user sends /merge
@bot.message_handler(commands=['merge'])
def merge_pdfs(message):
    user_id = message.from_user.id

    # Check if the user has uploaded any PDFs
    if user_id not in user_pdfs or len(user_pdfs[user_id]) < 2:
        bot.reply_to(message, "You need to send at least two PDF files to merge.")
        return

    # Create a merger object
    merger = PdfMerger()
    for pdf in user_pdfs[user_id]:
        merger.append(pdf)

    # Save the merged PDF to a temporary file
    output_path = f"{user_id}_merged.pdf"
    with open(output_path, "wb") as output_file:
        merger.write(output_file)

    # Send the merged PDF back to the user
    with open(output_path, "rb") as output_file:
        bot.send_document(message.chat.id, output_file)

    # Clean up
    os.remove(output_path)
    user_pdfs[user_id].clear()  # Clear the user's PDFs after merging
    bot.reply_to(message, "Here is your merged PDF!")

# Run the bot
bot.polling()
