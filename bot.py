import os
import telebot
from flask import Flask, request
from telebot import types
from PyPDF2 import PdfMerger
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from font_string import Fonts  # Ensure this module is available

# Fetch the bot token and webhook URL from the environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# Ensure the token is loaded
if not BOT_TOKEN:
    raise ValueError("No bot token provided. Please set the BOT_TOKEN environment variable.")
if not WEBHOOK_URL:
    raise ValueError("Webhook URL is missing! Please set the WEBHOOK_URL environment variable.")

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


#Font styling 
@Client.on_message(filters.private & filters.command(["font"]))
async def style_buttons(c, m, cb=False):
    buttons = [[
        InlineKeyboardButton('𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛', callback_data='style+typewriter'),
        InlineKeyboardButton('𝕆𝕦𝕥𝕝𝕚𝕟𝕖', callback_data='style+outline'),
        InlineKeyboardButton('𝐒𝐞𝐫𝐢𝐟', callback_data='style+serif'),
        ],[
        InlineKeyboardButton('𝑺𝒆𝒓𝒊𝒇', callback_data='style+bold_cool'),
        InlineKeyboardButton('𝑆𝑒𝑟𝑖𝑓', callback_data='style+cool'),
        InlineKeyboardButton('Sᴍᴀʟʟ Cᴀᴘs', callback_data='style+small_cap'),
        ],[
        InlineKeyboardButton('𝓈𝒸𝓇𝒾𝓅𝓉', callback_data='style+script'),
        InlineKeyboardButton('𝓼𝓬𝓻𝓲𝓹𝓽', callback_data='style+script_bolt'),
        InlineKeyboardButton('ᵗⁱⁿʸ', callback_data='style+tiny'),
        ],[
        InlineKeyboardButton('ᑕOᗰIᑕ', callback_data='style+comic'),
        InlineKeyboardButton('𝗦𝗮𝗻𝘀', callback_data='style+sans'),
        InlineKeyboardButton('𝙎𝙖𝙣𝙨', callback_data='style+slant_sans'),
        ],[
        InlineKeyboardButton('𝘚𝘢𝘯𝘴', callback_data='style+slant'),
        InlineKeyboardButton('𝖲𝖺𝗇𝗌', callback_data='style+sim'),
        InlineKeyboardButton('Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎', callback_data='style+circles')
        ],[
        InlineKeyboardButton('🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎', callback_data='style+circle_dark'),
        InlineKeyboardButton('𝔊𝔬𝔱𝔥𝔦𝔠', callback_data='style+gothic'),
        InlineKeyboardButton('𝕲𝖔𝖙𝖍𝖎𝖈', callback_data='style+gothic_bolt'),
        ],[
        InlineKeyboardButton('C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡', callback_data='style+cloud'),
        InlineKeyboardButton('H̆̈ă̈p̆̈p̆̈y̆̈', callback_data='style+happy'),
        InlineKeyboardButton('S̑̈ȃ̈d̑̈', callback_data='style+sad'),
        ],[
        InlineKeyboardButton('Next ➡️', callback_data="nxt")
    ]]
    if not cb:
        if ' ' in m.text:
            title = m.text.split(" ", 1)[1]
            await m.reply_text(title, reply_markup=InlineKeyboardMarkup(buttons), reply_to_message_id=m.id)                     
        else:
            await m.reply_text(text="Ente Any Text Eg:- `/font [text]`")    
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex('^nxt'))
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [[
            InlineKeyboardButton('🇸 🇵 🇪 🇨 🇮 🇦 🇱 ', callback_data='style+special'),
            InlineKeyboardButton('🅂🅀🅄🄰🅁🄴🅂', callback_data='style+squares'),
            InlineKeyboardButton('🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎', callback_data='style+squares_bold'),
            ],[
            InlineKeyboardButton('ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ', callback_data='style+andalucia'),
            InlineKeyboardButton('爪卂几ᘜ卂', callback_data='style+manga'),
            InlineKeyboardButton('S̾t̾i̾n̾k̾y̾', callback_data='style+stinky'),
            ],[
            InlineKeyboardButton('B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ', callback_data='style+bubbles'),
            InlineKeyboardButton('U͟n͟d͟e͟r͟l͟i͟n͟e͟', callback_data='style+underline'),
            InlineKeyboardButton('꒒ꍏꀷꌩꌃꀎꁅ', callback_data='style+ladybug'),
            ],[
            InlineKeyboardButton('R҉a҉y҉s҉', callback_data='style+rays'),
            InlineKeyboardButton('B҈i҈r҈d҈s҈', callback_data='style+birds'),
            InlineKeyboardButton('S̸l̸a̸s̸h̸', callback_data='style+slash'),
            ],[
            InlineKeyboardButton('s⃠t⃠o⃠p⃠', callback_data='style+stop'),
            InlineKeyboardButton('S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆', callback_data='style+skyline'),
            InlineKeyboardButton('A͎r͎r͎o͎w͎s͎', callback_data='style+arrows'),
            ],[
            InlineKeyboardButton('ዪሀክቿነ', callback_data='style+qvnes'),
            InlineKeyboardButton('S̶t̶r̶i̶k̶e̶', callback_data='style+strike'),
            InlineKeyboardButton('F༙r༙o༙z༙e༙n༙', callback_data='style+frozen')
            ],[
            InlineKeyboardButton('⬅️ Back', callback_data='nxt+0')
        ]]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@Client.on_callback_query(filters.regex('^style'))
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split('+')

    if style == 'typewriter':
        cls = Fonts.typewriter
    if style == 'outline':
        cls = Fonts.outline
    if style == 'serif':
        cls = Fonts.serief
    if style == 'bold_cool':
        cls = Fonts.bold_cool
    if style == 'cool':
        cls = Fonts.cool
    if style == 'small_cap':
        cls = Fonts.smallcap
    if style == 'script':
        cls = Fonts.script
    if style == 'script_bolt':
        cls = Fonts.bold_script
    if style == 'tiny':
        cls = Fonts.tiny
    if style == 'comic':
        cls = Fonts.comic
    if style == 'sans':
        cls = Fonts.san
    if style == 'slant_sans':
        cls = Fonts.slant_san
    if style == 'slant':
        cls = Fonts.slant
    if style == 'sim':
        cls = Fonts.sim
    if style == 'circles':
        cls = Fonts.circles
    if style == 'circle_dark':
        cls = Fonts.dark_circle
    if style == 'gothic':
        cls = Fonts.gothic
    if style == 'gothic_bolt':
        cls = Fonts.bold_gothic
    if style == 'cloud':
        cls = Fonts.cloud
    if style == 'happy':
        cls = Fonts.happy
    if style == 'sad':
        cls = Fonts.sad
    if style == 'special':
        cls = Fonts.special
    if style == 'squares':
        cls = Fonts.square
    if style == 'squares_bold':
        cls = Fonts.dark_square
    if style == 'andalucia':
        cls = Fonts.andalucia
    if style == 'manga':
        cls = Fonts.manga
    if style == 'stinky':
        cls = Fonts.stinky
    if style == 'bubbles':
        cls = Fonts.bubbles
    if style == 'underline':
        cls = Fonts.underline
    if style == 'ladybug':
        cls = Fonts.ladybug
    if style == 'rays':
        cls = Fonts.rays
    if style == 'birds':
        cls = Fonts.birds
    if style == 'slash':
        cls = Fonts.slash
    if style == 'stop':
        cls = Fonts.stop
    if style == 'skyline':
        cls = Fonts.skyline
    if style == 'arrows':
        cls = Fonts.arrows
    if style == 'qvnes':
        cls = Fonts.rvnes
    if style == 'strike':
        cls = Fonts.strike
    if style == 'frozen':
        cls = Fonts.frozen

    r, oldtxt = m.message.reply_to_message.text.split(None, 1) 
    new_text = cls(oldtxt)            
    try:
        await m.message.edit_text(f"`{new_text}`\n\n👆 Click To Copy", reply_markup=m.message.reply_markup)
    except Exception as e:
        print(e)

# Run bot and webhook
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    bot.polling()
