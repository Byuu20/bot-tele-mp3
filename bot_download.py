import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)
app = Flask('')

@app.route('/')
def home():
    return "Bot Telegram sedang aktif dan berjalan 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "🎵 **Bot Music Downloader (Render 24/7)**\n\n"
        "Kirimkan link YouTube atau TikTok, bot akan mengirimkan audionya untuk kamu!"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_download(message):
    url = message.text.strip()

    if not (url.startswith("http://") or url.startswith("https://")):
        bot.reply_to(message, "⚠️ Tolong kirimkan link YouTube/TikTok yang valid.")
        return

    sent_msg = bot.reply_to(message, "⏳ Sedang memproses audio... Mohon tunggu sebentar.")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': '%(id)s.%(ext)s',
        'quiet': True,
        'noplaylist': True
    }

    filename = ""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

            if 'entries' in info:
                info = info['entries'][0]

            ext = info.get('ext', 'm4a')
            if ext not in ['m4a', 'mp3', 'webm']:
                ext = 'm4a'

            file_id = info.get('id', 'audio')
            filename = f"{file_id}.{ext}"
            title = info.get('title', 'Audio Download')

        with open(filename, 'rb') as audio_file:
            bot.send_audio(
                message.chat.id, 
                audio_file, 
                title=title, 
                caption=f"✅ Berhasil!\n🎵 {title}"
            )

        if os.path.exists(filename):
            os.remove(filename)

        bot.delete_message(message.chat.id, sent_msg.message_id)

    except Exception as e:
        bot.edit_message_text(
            f"❌ Terjadi kesalahan.\nDetail: {str(e)}", 
            message.chat.id, 
            sent_msg.message_id
        )
        if filename and os.path.exists(filename):
            os.remove(filename)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    print("🤖 Bot Telegram berjalan mulus dengan Flask server...")
    bot.infinity_polling()
          
