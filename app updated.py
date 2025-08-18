import streamlit as st
import requests
import re
from bs4 import BeautifulSoup

st.set_page_config(page_title="Instagram Downloader", page_icon="📸", layout="centered")

st.title("📸 Instagram Downloader by Yousuf")

url = st.text_input("Paste Instagram Post/Reel URL:")

def get_instagram_data(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return None, None, None

        soup = BeautifulSoup(r.text, "html.parser")

        # Title
        title_tag = soup.find("meta", property="og:title")
        title = title_tag["content"] if title_tag else "Instagram Post"

        # Thumbnail
        thumb_tag = soup.find("meta", property="og:image")
        thumbnail = thumb_tag["content"] if thumb_tag else None

        # Video or Image
        video_tag = soup.find("meta", property="og:video")
        if video_tag:
            media_url = video_tag["content"]
        else:
            media_url = thumbnail

        return title, thumbnail, media_url
    except Exception as e:
        return None, None, None

if st.button("Fetch Post"):
    if url:
        title, thumbnail, media_url = get_instagram_data(url)
        if media_url:
            st.success("✅ Post Fetched Successfully!")
            st.write(f"**Title:** {title}")

            if media_url.endswith(".mp4"):
                st.video(media_url)
                st.download_button("⬇ Download Video", media_url)
            else:
                st.image(media_url, use_container_width=True)
                st.download_button("⬇ Download Image", media_url)
        else:
            st.error("❌ Failed to fetch media. Try another link.")
    else:
        st.warning("⚠️ Please enter a valid Instagram URL.")
