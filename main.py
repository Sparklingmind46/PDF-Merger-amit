import os
import time
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from PyPDF2 import PdfMerger

# Initialize the Pyrogram Client with token from environment variable
BOT_TOKEN = os.getenv('BOT_TOKEN')
app = Client("pdf_genie", bot_token=BOT_TOKEN)

# Temporary storage for user files (dictionary to store file paths by user)
user_files = {}

# Start command handler
@app.on_message(filters.command("start"))
async def send_welcome(client, message):
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    sent_sticker = await message.reply_sticker(sticker_id)
    await time.sleep(3)
    await client.delete_messages(message.chat.id, sent_sticker.id)

    # Define the inline keyboard with buttons
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("«ʜᴇʟᴘ» 🕵️", callback_data="help"),
         InlineKeyboardButton("«ᴀʙᴏᴜᴛ» 📄", callback_data="about")],
        [InlineKeyboardButton("•Dᴇᴠᴇʟᴏᴘᴇʀ• ☘", url="https://t.me/Ur_amit_01")]
    ])

    # Send the photo with the caption and inline keyboard
    image_url = 'https://envs.sh/jxZ.jpg'
    await client.send_photo(
        chat_id=message.chat.id,
        photo=image_url,
        caption="•Hello there, Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done.",
        reply_markup=markup
    )

# Callback query handler for "help", "about", and "back"
@app.on_callback_query(filters.regex("help|about|back"))
async def callback_handler(client, callback_query):
    if callback_query.data == "help":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = "Hᴇʀᴇ Is Tʜᴇ Hᴇʟᴘ Fᴏʀ Mʏ Cᴏᴍᴍᴀɴᴅs.:\n1. Send PDF files.\n2. Use /merge when you're ready to combine them.\n3. Max size = 20MB per file.\n\n• Note: My developer is constantly adding new features in my program , if you found any bug or error please report at @Ur_Amit_01"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
    elif callback_query.data == "about":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = ABOUT_TXT
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])
    else:  # callback_query.data == "back"
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = "*Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done.*"
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Help 🕵️", callback_data="help"),
             InlineKeyboardButton("About 📄", callback_data="about")],
            [InlineKeyboardButton("Developer ☘", url="https://t.me/Ur_Amit_01")]
        ])
    
    # Edit the original message with the new image and caption
    await callback_query.edit_message_media(
        InputMediaPhoto(media=new_image_url, caption=new_caption, parse_mode="html"),
        reply_markup=markup
    )

# Text for "about" section
ABOUT_TXT = """<b><blockquote>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</blockquote>
    
‣ ᴍʏ ɴᴀᴍᴇ : <a href='https://t.me/PDF_Genie_Robot'>PDF Genie</a>
‣ ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a> 
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/Ur_amit_01'>ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝</a> 
‣ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a> 
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a> 
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : ᴠ2.7.1 [sᴛᴀʙʟᴇ]</b>"""

# Merge PDF command handler
@app.on_message(filters.command("merge"))
async def merge_pdfs(client, message):
    user_id = message.from_user.id
    if user_id not in user_files or len(user_files[user_id]) < 2:
        await message.reply("You need to send at least two PDF files before merging.")
        return
    
    await message.reply("Please provide a filename for the merged PDF (without the .pdf extension).")
    client.add_handler(filters.text & filters.user(user_id), handle_filename_input)

# Filename input handler
async def handle_filename_input(client, message):
    user_id = message.from_user.id
    filename = message.text.strip() + ".pdf"
    await merge_pdfs_with_filename(client, user_id, message.chat.id, filename)

# Merge files with filename
async def merge_pdfs_with_filename(client, user_id, chat_id, filename):
    merger = PdfMerger()
    progress_message = await client.send_message(chat_id, "Merging PDFs: 0%")
    
    try:
        total_files = len(user_files[user_id])
        for i, pdf_file in enumerate(user_files[user_id]):
            merger.append(pdf_file)
            await progress_message.edit(f"Merging PDFs: {int((i + 1) / total_files * 100)}%")
            time.sleep(1)  # Simulate merge time

        with open(filename, "wb") as merged_file:
            merger.write(merged_file)

        await progress_message.edit("Uploading merged file...")
        await client.send_document(chat_id, filename)
        await progress_message.delete()
        await client.send_message(chat_id, f"*Here is your merged PDF!📕😎*", parse_mode="Markdown")

    finally:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []

# Document (PDF) handler
@app.on_message(filters.document)
async def handle_document(client, message):
    if message.document.mime_type == 'application/pdf':
        if message.document.file_size > MAX_FILE_SIZE:
            await message.reply("File is too large. Please upload a PDF smaller than 20 MB.")
            return

        user_id = message.from_user.id
        if user_id not in user_files:
            user_files[user_id] = []

        file_path = await client.download_media(message.document)
        user_files[user_id].append(file_path)
        await message.reply(f"Added {message.document.file_name} to the list for merging.")
    else:
        await message.reply("Please send only PDF files.")

# Clear command handler to reset files
@app.on_message(filters.command("clear"))
async def clear_files(client, message):
    user_id = message.from_user.id
    if user_id in user_files:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []
    await message.reply("Your file list has been cleared.")

# Run the bot
app.run()
