import streamlit as st
import instaloader
import os
from urllib.parse import urlparse
import time

class InstagramVideoDownloader:
    def __init__(self):
        self.L = instaloader.Instaloader(
            save_metadata=False,
            download_videos=True,
            download_video_thumbnails=False,
            post_metadata_txt_pattern="",
            compress_json=False
        )
        self.delay_between_downloads = 5

    def download_single_post(self, url: str, folder: str = "downloads") -> dict:
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)

            shortcode = self._extract_shortcode(url)
            if not shortcode:
                return {"status": "error", "message": "Invalid Instagram URL"}

            post = instaloader.Post.from_shortcode(self.L.context, shortcode)

            if not post.is_video:
                return {"status": "error", "message": "This post does not contain a video"}

            self.L.dirname_pattern = folder
            self.L.download_post(post, target=folder)

            return {
                "status": "success",
                "caption": post.caption[:100] if post.caption else "No caption",
                "date": str(post.date_utc),
                "likes": post.likes,
                "comments": post.comments
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _extract_shortcode(self, url: str) -> str:
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) >= 2 and path_parts[0] in ["p", "reel", "tv"]:
                return path_parts[1]
            return None
        except:
            return None


# ---------------- STREAMLIT APP ----------------

st.set_page_config(page_title="Instagram Video Downloader", page_icon="📥")

st.title("📥 Instagram Video Downloader")
st.write("Paste a public Instagram video link below to download it.")

url_input = st.text_input("Instagram Post URL", placeholder="https://www.instagram.com/reel/...")
folder_name = st.text_input("Download Folder", value="downloads")
delay_time = st.slider("Delay between downloads (seconds)", 1, 10, 5)

if st.button("Download Video"):
    if url_input.strip() == "":
        st.error("Please enter a valid Instagram URL.")
    else:
        with st.spinner("Downloading..."):
            downloader = InstagramVideoDownloader()
            downloader.delay_between_downloads = delay_time
            result = downloader.download_single_post(url_input.strip(), folder_name.strip())

        if result["status"] == "success":
            st.success("✅ Download Complete!")
            st.write(f"**Caption:** {result['caption']}")
            st.write(f"📅 Date: {result['date']}")
            st.write(f"❤️ Likes: {result['likes']}")
            st.write(f"💬 Comments: {result['comments']}")
            st.write(f"📂 Saved to: `{os.path.abspath(folder_name)}`")
        else:
            st.error(f"❌ {result['message']}")
