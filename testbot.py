import telebot
from telebot import types
from pymongo import MongoClient
import yt_dlp
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv('8559319537:AAG4BulP--sETSx2u67zvo5tcJ5x5snzPz0')
MONGO_URI = os.getenv('mongodb+srv://javohirtojiyev99_db_user:0cD7fxlkOfNmY4zS@cluster0.4skcgpy.mongodb.net/?appName=Cluster0'')
ADMIN_ID = int(os.getenv('7808985151'))
CHANNEL_1 = os.getenv('CLC_KINO_BOT')
CHANNEL_2 = os.getenv('CLC_KINO')

bot = telebot.TeleBot(TOKEN)

client = MongoClient(MONGO_URI)
db = client['video_bot']
users = db['users']

# =========================
# MAJBURIY OBUNA
# =========================

def check_sub(user_id):
    try:
        ch1 = bot.get_chat_member(CHANNEL_1, user_id)
        ch2 = bot.get_chat_member(CHANNEL_2, user_id)

        if ch1.status in ['member', 'administrator', 'creator'] and ch2.status in ['member', 'administrator', 'creator']:
            return True

        return False

    except:
        return False

# =========================
# START
# =========================

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not users.find_one({'id': user_id}):
        users.insert_one({
            'id': user_id,
            'name': message.from_user.first_name
        })

    if not check_sub(user_id):
        markup = types.InlineKeyboardMarkup()

        markup.add(
            types.InlineKeyboardButton('📢 Kanal 1', url=f'https://t.me/{CHANNEL_1.replace("@","")}')
        )

        markup.add(
            types.InlineKeyboardButton('📢 Kanal 2', url=f'https://t.me/{CHANNEL_2.replace("@","")}')
        )

        markup.add(
            types.InlineKeyboardButton('✅ Tekshirish', callback_data='check_sub')
        )

        text = """
🔥 Botdan foydalanish uchun quyidagi kanallarga obuna bo‘ling 👇

━━━━━━━━━━━━━━
📢 Premium kanallar
━━━━━━━━━━━━━━

✅ Obuna bo‘lgach "Tekshirish" tugmasini bosing.
"""

        bot.send_message(message.chat.id, text, reply_markup=markup)
        return

    lang_buttons(message.chat.id)

# =========================
# TIL TANLASH
# =========================

def lang_buttons(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.row('🇺🇿 Uzbekcha', '🇷🇺 Русский')
    markup.row('🇺🇸 English')

    bot.send_message(
        chat_id,
        '🌍 Tilni tanlang:',
        reply_markup=markup
    )

# =========================
# OBUNA CHECK
# =========================

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data == 'check_sub':

        if check_sub(call.from_user.id):
            bot.answer_callback_query(call.id, '✅ Tasdiqlandi')
            lang_buttons(call.message.chat.id)

        else:
            bot.answer_callback_query(call.id, '❌ Hali obuna emassiz')

# =========================
# VIDEO LINK
# =========================

@bot.message_handler(func=lambda m: 'http' in m.text)
def get_video(message):

    url = message.text

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton('🎬 1080p', callback_data=f'1080|{url}')
    )

    markup.add(
        types.InlineKeyboardButton('📺 720p', callback_data=f'720|{url}')
    )

    markup.add(
        types.InlineKeyboardButton('📱 480p', callback_data=f'480|{url}')
    )

    text = """
🌈 Video sifati tanlang

━━━━━━━━━━━━━━
🎥 HD yuklash tizimi
━━━━━━━━━━━━━━

⚡ Tez yuklash
💎 Premium sifat
🔥 TikTok / Instagram / YouTube
"""

    bot.send_message(message.chat.id, text, reply_markup=markup)

# =========================
# VIDEO YUKLASH
# =========================

@bot.callback_query_handler(func=lambda c: '|' in c.data)
def download_video(call):

    quality, url = call.data.split('|')

    bot.answer_callback_query(call.id, '⏳ Video yuklanmoqda...')

    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        with open(filename, 'rb') as video:
            bot.send_video(
                call.message.chat.id,
                video,
                caption='🔥 Video tayyor ✅\n💎 Powered by Premium Bot'
            )

        os.remove(filename)

    except Exception as e:
        bot.send_message(call.message.chat.id, f'❌ Xatolik: {e}')

# =========================
# ADMIN PANEL
# =========================

@bot.message_handler(commands=['admin'])
def admin(message):

    if message.from_user.id != ADMIN_ID:
        return

    total = users.count_documents({})

    text = f"""
👑 ADMIN PANEL

━━━━━━━━━━━━━━
👥 Foydalanuvchilar: {total}
━━━━━━━━━━━━━━

🔥 Bot aktiv ishlayapti
💎 Server online
⚡ Premium mode
"""

    markup = types.InlineKeyboardMarkup()

    markup.add(
        types.InlineKeyboardButton('📢 Reklama yuborish', callback_data='broadcast')
    )

    bot.send_message(message.chat.id, text, reply_markup=markup)

# =========================
# RUN
# =========================

print('Bot ishga tushdi...')
bot.infinity_polling()
