import instaloader
import os
from urllib.parse import urlparse
import telebot
from telebot import apihelper
import time
import threading

# Configure timeout settings for requests
apihelper.READ_TIMEOUT = 30  # Increased timeout for API requests
apihelper.CONNECT_TIMEOUT = 30

# Telegram Bot Token (Replace with your actual token)
TOKEN = "8160547955:AAGqeJzAJnsLj2UNPzWk9F_9snKdGAFJkXg"
bot = telebot.TeleBot(TOKEN)

class InstagramDownloaderBot:
    def __init__(self):
        self.L = instaloader.Instaloader(
            save_metadata=False,
            download_videos=True,
            download_video_thumbnails=False,
            post_metadata_txt_pattern="",
            compress_json=False
        )
        self.download_folder = "instagram_downloads"
        if not os.path.exists(self.download_folder):
            os.makedirs(self.download_folder)

    def _extract_shortcode(self, url):
        """Extract shortcode from Instagram URL"""
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip("/").split("/")
            
            if len(path_parts) >= 2 and path_parts[0] in ["p", "reel", "tv"]:
                return path_parts[1]
            return None
        except:
            return None

    def download_post(self, url, chat_id):
        """Download Instagram post and send to user"""
        try:
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                bot.send_message(chat_id, "❌ Invalid Instagram URL format")
                return

            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            if not post.is_video:
                bot.send_message(chat_id, "⚠️ This post doesn't contain a video")
                return

            self.L.download_post(post, target=self.download_folder)
            
            # Find and send the downloaded video
            for file in os.listdir(self.download_folder):
                if file.endswith('.mp4'):
                    video_path = os.path.join(self.download_folder, file)
                    try:
                        with open(video_path, 'rb') as video_file:
                            caption = (
                                f"📌 Caption: {post.caption[:100]}...\n"
                                f"📅 Date: {post.date_utc}\n"
                                f"❤️ Likes: {post.likes}\n"
                                f"💬 Comments: {post.comments}"
                            ) if post.caption else "No caption available"
                            
                            bot.send_video(chat_id, video_file, caption=caption)
                    except Exception as e:
                        bot.send_message(chat_id, f"❌ Error sending video: {str(e)}")
                    finally:
                        # Clean up downloaded file
                        try:
                            os.remove(video_path)
                        except:
                            pass
                    break

        except Exception as e:
            bot.send_message(chat_id, f"❌ Error downloading post: {str(e)}")

# Bot Commands
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    help_text = """
🌟 *Instagram Video Downloader Bot* 🌟

Send me an Instagram post URL (Reel, Post, or IGTV) and I'll download the video for you.

Example URLs:
- Reels: https://www.instagram.com/reel/Cxample/
- Posts: https://www.instagram.com/p/Cxample/
- IGTV: https://www.instagram.com/tv/Cxample/

Note: Only works with public accounts.
"""
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    text = message.text.strip()
    if "instagram.com" in text:
        msg = bot.reply_to(message, "⏳ Downloading video, please wait...")
        
        # Run download in separate thread to avoid timeout issues
        downloader = InstagramDownloaderBot()
        thread = threading.Thread(
            target=downloader.download_post,
            args=(text, message.chat.id)
        )
        thread.start()
    else:
        bot.reply_to(message, "❌ Please send a valid Instagram URL")

# Configure polling with error handling
def start_bot():
    while True:
        try:
            print("Bot is running...")
            bot.polling(none_stop=True, interval=3, timeout=30)
        except Exception as e:
            print(f"Bot error: {str(e)}")
            time.sleep(10)  # Wait before restarting

if __name__ == "__main__":
    print("🚀 Starting Instagram Video Downloader Bot")
    while True:
        try:
            bot.polling(none_stop=True, interval=3, timeout=30)
        except Exception as e:
            print(f"⚠️ Error: {e}")
            print("🔄 Restarting bot in 10 seconds...")
            time.sleep(10)
