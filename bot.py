import telebot
import yt_dlp
import os

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

# user temporary data
user_data = {}

# ===== START =====
@bot.message_handler(commands=['start'])
def start(msg):
    bot.send_message(
        msg.chat.id,
        " သီချင်းနာမည် (သို့) အဆိုတော်နာမည် ရိုက်ရှာပါ"
    )

# ===== SEARCH SONG =====
@bot.message_handler(func=lambda m: True)
def search_song(msg):
    query = msg.text
    user_data[msg.chat.id] = {"query": query}

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'cookiefile': '/data/cookies.txt'
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            result = ydl.extract_info(f"ytsearch5:{query}", download=False)

        markup = telebot.types.InlineKeyboardMarkup()
        for i, v in enumerate(result['entries']):
            markup.add(
                telebot.types.InlineKeyboardButton(
                    f"{i+1}. {v['title']}",
                    callback_data=f"song_{v['id']}"
                )
            )

        bot.send_message(msg.chat.id, " သီချင်းရွေးပါ", reply_markup=markup)

    except Exception as e:
        bot.send_message(
            msg.chat.id,
            " Search မအောင်မြင်ပါ\nCookies expire ဖြစ်နိုင်ပါတယ်"
        )

# ===== SONG SELECT =====
@bot.callback_query_handler(func=lambda c: c.data.startswith("song_"))
def choose_song(call):
    video_id = call.data.replace("song_", "")
    user_data[call.message.chat.id]["video"] = video_id

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(" MP3", callback_data="mp3"),
        telebot.types.InlineKeyboardButton(" MP4", callback_data="mp4")
    )
    markup.add(
        telebot.types.InlineKeyboardButton(" Back", callback_data="back")
    )

    bot.edit_message_text(
        "Format ရွေးပါ",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ===== BACK TO SEARCH RESULT =====
@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(call):
    query = user_data[call.message.chat.id]["query"]

    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'cookiefile': '/data/cookies.txt'
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(f"ytsearch5:{query}", download=False)

    markup = telebot.types.InlineKeyboardMarkup()
    for i, v in enumerate(result['entries']):
        markup.add(
            telebot.types.InlineKeyboardButton(
                f"{i+1}. {v['title']}",
                callback_data=f"song_{v['id']}"
            )
        )

    bot.edit_message_text(
        " သီချင်းရွေးပါ",
        call.message.chat.id,
        call.message.message_id,
        reply_markup=markup
    )

# ===== DOWNLOAD =====
@bot.callback_query_handler(func=lambda c: c.data in ["mp3", "mp4"])
def download(call):
    video_id = user_data[call.message.chat.id]["video"]
    url = f"https://www.youtube.com/watch?v={video_id}"

    bot.edit_message_text(
        " Downloading...",
        call.message.chat.id,
        call.message.message_id
    )

    if call.data == "mp3":
        ydl_opts = {
            'format': 'bestaudio',
            'outtmpl': '%(title)s.mp3',
            'cookiefile': '/data/cookies.txt',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3'
            }]
        }
    else:
        ydl_opts = {
            'format': 'best',
            'outtmpl': '%(title)s.%(ext)s',
            'cookiefile': '/data/cookies.txt'
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file = ydl.prepare_filename(info)

        with open(file, 'rb') as f:
            bot.send_document(call.message.chat.id, f)

        os.remove(file)

    except Exception as e:
        bot.send_message(
            call.message.chat.id,
            " Download မအောင်မြင်ပါ\nCookies expire ဖြစ်နိုင်ပါတယ်"
        )

# ===== RUN =====
bot.polling()
