import os
import telebot
from telebot import types
from PyPDF2 import PdfMerger
import time 
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from PIL import Image

# Initialize bot with token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

# Start command handler
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # Send a sticker first
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    sent_sticker = bot.send_sticker(message.chat.id, sticker_id)
    sticker_message_id = sent_sticker.message_id
    time.sleep(3)
    bot.delete_message(message.chat.id, sticker_message_id)
    
    # Define the inline keyboard with buttons
    markup = InlineKeyboardMarkup()
    # First row: Help and About buttons
    markup.row_width = 2
    markup.add(
        InlineKeyboardButton("Help 🕵️", callback_data="help"),
        InlineKeyboardButton("About 📄", callback_data="about")
    )
    # Second row: Developer button
    markup.add(InlineKeyboardButton("Developer ☘", url="https://t.me/Ur_amit_01"))
    
    # Send the photo with the caption and inline keyboard
    image_url = 'https://envs.sh/jxZ.jpg'
    bot.send_photo(
        message.chat.id, 
        image_url, 
        caption="•Hello there, Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done.",
        reply_markup=markup
    )

@bot.callback_query_handler(func=lambda call: call.data in ["help", "about", "back"])
def callback_handler(call):
    # Define media and caption based on the button clicked
    if call.data == "help":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = "Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ Mʏ Cᴏᴍᴍᴀɴᴅs.:\n1. Send PDF files.\n2. Use /merge when you're ready to combine them.\n3. Max size = 20MB per file.\n\n• Note: My developer is constantly adding new features in my program , if you found any bug or error please report at @Ur_Amit_01"
        # Add a "Back" button
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("Back", callback_data="back"))
    elif call.data == "about":
    # Get the bot's username dynamically
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = ABOUT_TXT
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("Back", callback_data="back"))
    elif call.data == "back":
        # Go back to the start message
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = "*Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done.*"
        # Restore original keyboard with Help, About, and Developer buttons
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(
            InlineKeyboardButton("Help 🕵️", callback_data="help"),
            InlineKeyboardButton("About 📄", callback_data="about")
        )
        markup.add(InlineKeyboardButton("Developer ☘", url="https://t.me/Ur_Amit_01"))
    
    # Create media object with the new image and caption
    media = InputMediaPhoto(media=new_image_url, caption=new_caption, parse_mode="HTML")
    
    # Edit the original message with the new image and caption
    bot.edit_message_media(
        media=media,
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup  # Updated inline keyboard
    )

ABOUT_TXT = """<b><blockquote>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</blockquote>
    
‣ ᴍʏ ɴᴀᴍᴇ : <a href='https://t.me/PDF_Genie_Robot'>PDF Genie</a>
‣ ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a> 
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/Ur_amit_01'>ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝</a> 
‣ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a> 
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a> 
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : ᴠ2.7.1 [sᴛᴀʙʟᴇ]</b>"""

# Help command handler
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = "1. Send me PDF files you want to merge.\n"
    help_text += "2. Use /merge to combine the files into one PDF.\n"
    help_text += "3. Use /clear to reset the list of files."
    bot.reply_to(message, help_text)

# Helper to update progress
def update_progress(chat_id, message_id, progress_text):
    bot.edit_message_text(
        text=progress_text,
        chat_id=chat_id,
        message_id=message_id
    )

# Merge command handler
@bot.message_handler(commands=['merge'])
def merge_pdfs(message):
    user_id = message.from_user.id
    
    # Check if there are files to merge
    if user_id not in user_files or len(user_files[user_id]) < 2:
        bot.reply_to(message, "You need to send at least two PDF files before merging.")
        return
    
    # Ask for the filename
    bot.reply_to(message, "Please provide a filename for the merged PDF (without the .pdf extension).")
    bot.register_next_step_handler(message, handle_filename_input)

# Handler for receiving the filename
def handle_filename_input(message):
    user_id = message.from_user.id
    filename = message.text.strip()
    
    if filename:
        # Ensure the filename ends with .pdf
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        
        # Proceed to merge the PDFs with the given filename
        merge_pdfs_with_filename(user_id, message.chat.id, filename)
    else:
        bot.reply_to(message, "Please provide a valid filename.")
        bot.register_next_step_handler(message, handle_filename_input)

def merge_pdfs_with_filename(user_id, chat_id, filename):
    merger = PdfMerger()
    total_files = len(user_files["pdfs"].get(user_id, [])) + len(user_files["images"].get(user_id, []))
    progress_message = bot.send_message(chat_id, "Merging files: 0%")

    # Convert images to a single PDF first
    image_pdfs = []
    if user_files["images"].get(user_id):
        image_pdf_name = f"{user_id}_images.pdf"
        images = [Image.open(img_path).convert('RGB') for img_path in user_files["images"][user_id]]
        images[0].save(image_pdf_name, save_all=True, append_images=images[1:])
        image_pdfs.append(image_pdf_name)

    try:
        # Append each PDF or converted image PDF file and update progress
        for i, pdf_file in enumerate(user_files["pdfs"].get(user_id, []) + image_pdfs):
            merger.append(pdf_file)
            # Calculate and update progress percentage
            progress_percent = int(((i + 1) / total_files) * 100)
            bot.edit_message_text(
                chat_id=chat_id,
                message_id=progress_message.message_id,
                text=f"Merging files: {progress_percent}%"
            )
            time.sleep(1)  # Optional delay to simulate progress time

        # Write the final merged PDF
        with open(filename, "wb") as merged_file:
            merger.write(merged_file)

        # Notify the user that the merging is complete
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=progress_message.message_id,
            text="Uploading merged file..."
        )

        # Send the merged PDF back to the user
        with open(filename, "rb") as merged_file:
            bot.send_document(chat_id, merged_file)
        
        bot.send_message(chat_id, "Here is your merged PDF!",parse_mode="Markdown")
    finally:
        # Clean up
        for file_list in user_files.values():
            if user_id in file_list:
                for file in file_list[user_id]:
                    os.remove(file)
                file_list[user_id] = []
        os.remove(filename)
    
    # Delete the progress message
    bot.delete_message(chat_id, progress_message.message_id)


         
# Handler for received documents (PDFs)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB in bytes

# Dictionary to store PDFs and images separately for each user
user_files = {
    "pdfs": {},   # Stores paths to PDF files
    "images": {}  # Stores paths to image files
}

@bot.message_handler(content_types=['document'])
def handle_document(message):
    user_id = message.from_user.id
    file_type = message.document.mime_type
    file_size = message.document.file_size
    
    if file_size > MAX_FILE_SIZE:
        bot.reply_to(message, "File too large. Please upload files under 20 MB.")
        return

    # Ensure dictionary entries for each user
    if user_id not in user_files["pdfs"]:
        user_files["pdfs"][user_id] = []
        user_files["images"][user_id] = []

    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
    # Save file with a unique name
    file_name = f"{message.document.file_name}"
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Check if file is a PDF or an image and store accordingly
    if file_type == 'application/pdf':
        user_files["pdfs"][user_id].append(file_name)
        bot.reply_to(message, f"Added {file_name} to the PDF list for merging.")
    elif file_type in ['image/jpeg', 'image/png']:
        user_files["images"][user_id].append(file_name)
        bot.reply_to(message, f"Added {file_name} to the image list for merging.")
    else:
        bot.reply_to(message, "Please send only PDF or image files.")


@bot.message_handler(commands=['clear'])
def clear_files(message):
    user_id = message.from_user.id
    for file_list in user_files.values():
        if user_id in file_list:
            for file_path in file_list[user_id]:
                os.remove(file_path)
            file_list[user_id] = []
    bot.reply_to(message, "Your file list has been cleared.")

bot.delete_webhook()
# Run the bot
bot.polling()
