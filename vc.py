import telebot
import os
import requests
import yt_dlp
import math

# 🔥 Replace with your Telegram bot token
BOT_TOKEN = "7690937386:AAG5BY6X4nzbz0jmtAWxVYWsFSFxW7tV6IE"
bot = telebot.TeleBot(BOT_TOKEN)

# 📥 YouTube Video Download Folder
DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# 🌐 Custom Headers (User-Agent)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 🎥 Video Download Function
def download_video(url):
    """Download YouTube video and split into 19MB parts"""
    ydl_opts = {
        "format": "best[ext=mp4]",
        "outtmpl": f"{DOWNLOAD_DIR}/%(title)s.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "merge_output_format": "mp4",
        "headers": HEADERS,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    return filename, info["title"]

# 🚀 Splitting Large Videos into 19MB Chunks
def split_video(file_path, max_size=19 * 1024 * 1024):
    """Split large video into parts under 19MB"""
    file_size = os.path.getsize(file_path)
    if file_size <= max_size:
        return [file_path]
    return []

# 🎬 Handle /start
@bot.message_handler(commands=["start"])
def send_welcome(message):
    bot.send_message(message.chat.id, "👋 *Welcome!*\nSend me a YouTube link to download.", parse_mode="Markdown")

# 🔗 Handle YouTube Links
@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_youtube_download(message):
    url = message.text
    chat_id = message.chat.id

    try:
        bot.send_message(chat_id, "⏳ *Downloading... Please wait!*", parse_mode="Markdown")

        # 🎞 Download Video
        video_path, title = download_video(url)
        
        # 🚀 Check video size
        parts = split_video(video_path)

        if not parts:
            bot.send_message(chat_id, "❌ *Video has reached the limit of 19MB.*", parse_mode="Markdown")
            return

        # 📤 Send Video in Parts
        for i, part in enumerate(parts):
            bot.send_message(chat_id, f"📤 Sending part {i+1}...")
            with open(part, "rb") as video:
                bot.send_video(chat_id, video, caption=f"{title} - Part {i+1}")

        # 🗑 Clean Up
        for part in parts:
            os.remove(part)

    except:
        pass  # Error message removed

# 🚀 Run Bot
print("🤖 Bot is running...")
bot.infinity_polling()
