import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from PyPDF2 import PdfMerger

# Fetch the API credentials from environment variables
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
bot_token = os.getenv("BOT_TOKEN")

if not api_id or not api_hash or not bot_token:
    raise ValueError("API ID, API Hash, and Bot Token are required.")

# Initialize the Pyrogram Client with API credentials
app = Client("pdf_genie", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Temporary storage for user files
user_files = {}

ABOUT_TXT = """<b><blockquote>⍟───[ MY ᴅᴇᴛᴀɪʟꜱ ]───⍟</blockquote>
‣ ᴍʏ ɴᴀᴍᴇ : <a href='https://t.me/PDF_Genie_Robot'>PDF Genie</a>
‣ ᴍʏ ʙᴇsᴛ ғʀɪᴇɴᴅ : <a href='tg://settings'>ᴛʜɪs ᴘᴇʀsᴏɴ</a> 
‣ ᴅᴇᴠᴇʟᴏᴘᴇʀ : <a href='https://t.me/Ur_amit_01'>ꫝᴍɪᴛ ꢺɪɴɢʜ ⚝</a> 
‣ ʟɪʙʀᴀʀʏ : <a href='https://docs.pyrogram.org/'>ᴘʏʀᴏɢʀᴀᴍ</a> 
‣ ʟᴀɴɢᴜᴀɢᴇ : <a href='https://www.python.org/download/releases/3.0/'>ᴘʏᴛʜᴏɴ 3</a> 
‣ ᴅᴀᴛᴀ ʙᴀsᴇ : <a href='https://www.mongodb.com/'>ᴍᴏɴɢᴏ ᴅʙ</a> 
‣ ʙᴜɪʟᴅ sᴛᴀᴛᴜs : ᴠ2.7.1 [sᴛᴀʙʟᴇ]</b>"""

@app.on_message(filters.command("start"))
async def start(client, message):
    sticker_id = 'CAACAgUAAxkBAAECEpdnLcqQbmvQfCMf5E3rBK2dkgzqiAACJBMAAts8yFf1hVr67KQJnh4E'
    sent_sticker = await client.send_sticker(message.chat.id, sticker_id)
    if sent_sticker and hasattr(sent_sticker, "message_id"):
        await time.sleep(3)
        await client.delete_messages(message.chat.id, sent_sticker.message_id)

    # Inline keyboard with buttons
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("«ʜᴇʟᴘ» 🕵️", callback_data="help"),
         InlineKeyboardButton("«ᴀʙᴏᴜᴛ» 📄", callback_data="about")],
        [InlineKeyboardButton("•Dᴇᴠᴇʟᴏᴘᴇʀ• ☘", url="https://t.me/Ur_amit_01")]
    ])

    image_url = 'https://envs.sh/jxZ.jpg'
    await client.send_photo(
        message.chat.id,
        image_url,
        caption="•Hello there, Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done.",
        reply_markup=markup
    )

@app.on_callback_query(filters.regex("^(help|about|back)$"))
async def callback_handler(client, callback_query):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    if data == "help":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = """Here is the Help for my commands:\n1. Send PDF files.\n2. Use /merge when you're ready to combine them.\n3. Max size = 20MB per file."""
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])

    elif data == "about":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = ABOUT_TXT
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("Back", callback_data="back")]])

    elif data == "back":
        new_image_url = 'https://envs.sh/jxZ.jpg'
        new_caption = "Welcome💓✨\n• I can merge PDFs (Max= 20MB per file).\n• Send PDF files 📕 to merge and use /merge when you're done."
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Help 🕵️", callback_data="help"),
             InlineKeyboardButton("About 📄", callback_data="about")],
            [InlineKeyboardButton("Developer ☘", url="https://t.me/Ur_amit_01")]
        ])

    await client.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaPhoto(media=new_image_url, caption=new_caption, parse_mode="html"),
        reply_markup=markup
    )

# Merge command handler
@app.on_message(filters.command("merge"))
async def merge_pdfs(client, message):
    user_id = message.from_user.id

    if user_id not in user_files or len(user_files[user_id]) < 2:
        await message.reply("You need to send at least two PDF files before merging.")
        return

    await message.reply("Please provide a filename for the merged PDF (without the .pdf extension).")
    client.listen("filename_input")

# Handler for receiving filename
async def handle_filename_input(client, message):
    user_id = message.from_user.id
    filename = message.text.strip()

    if filename:
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"
        await merge_pdfs_with_filename(client, user_id, message.chat.id, filename)
    else:
        await message.reply("Please provide a valid filename.")
        client.listen("filename_input")

# Function to merge PDFs
async def merge_pdfs_with_filename(client, user_id, chat_id, filename):
    merger = PdfMerger()
    progress_message = await client.send_message(chat_id, "Merging PDFs: 0%")

    try:
        total_files = len(user_files[user_id])
        for i, pdf_file in enumerate(user_files[user_id]):
            merger.append(pdf_file)
            progress_text = f"Merging PDFs: {int((i + 1) / total_files * 100)}%"
            await progress_message.edit_text(progress_text)
            await asyncio.sleep(1)

        with open(filename, "wb") as merged_file:
            merger.write(merged_file)

        await progress_message.edit_text("Uploading merged file...")

        with open(filename, "rb") as merged_file:
            await client.send_document(chat_id, merged_file)

        await client.delete_messages(chat_id, progress_message.message_id)
        await client.send_message(chat_id, "Here is your merged PDF!📕😎", parse_mode="markdown")

    finally:
        for pdf_file in user_files[user_id]:
            os.remove(pdf_file)
        user_files[user_id] = []

# Handler for received documents (PDFs)
MAX_FILE_SIZE = 20 * 1024 * 1024

@app.on_message(filters.document)
async def handle_document(client, message):
    # Check if the message has `from_user` data to ensure it is from a user
    if not message.from_user:
        await message.reply("Sorry, I can't process this message.")
        return

    if message.document.mime_type == "application/pdf":
        file_size = message.document.file_size

        if file_size > MAX_FILE_SIZE:
            await message.reply("Sorry, the file is too large. Please upload a PDF smaller than 20 MB.")
            return

        user_id = message.from_user.id
        if user_id not in user_files:
            user_files[user_id] = []

        file_path = await client.download_media(message.document)
        user_files[user_id].append(file_path)
        await message.reply(f"Added {message.document.file_name} to the list for merging.")
    else:
        await message.reply("Please send only PDF files.")

# Clear command to reset files
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
