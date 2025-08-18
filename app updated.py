import streamlit as st
import instaloader
import tempfile
import os
from urllib.parse import urlparse
import time
import random

class InstagramVideoDownloader:
    def __init__(self):
        self.L = instaloader.Instaloader(
            save_metadata=False,
            download_videos=True,
            download_video_thumbnails=False,
            post_metadata_txt_pattern="",
            compress_json=False,
            request_timeout=60  # Increase timeout
        )
        
        # Configure to appear more like a browser
        self.L.context._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.instagram.com/',
            'DNT': '1'
        })
        
        # Slow down requests
        self.L.context.sleep = True
        self.L.context.delay = 5  # Minimum delay between requests
        self.L.context.max_connection_attempts = 3

    def download_single_post(self, url: str) -> dict:
        try:
            # Random delay to avoid appearing automated
            time.sleep(random.uniform(2, 5))
            
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                return {"status": "error", "message": "Invalid Instagram URL"}

            # Try with different query IDs if needed
            try:
                post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            except Exception as e:
                # Retry with different parameters
                time.sleep(5)
                return {"status": "error", "message": f"Failed to fetch post. Instagram may be blocking requests. Try again later. Error: {str(e)}"}

            if not post.is_video:
                return {"status": "error", "message": "This post does not contain a video"}

            # Temporary folder for Streamlit
            temp_dir = tempfile.mkdtemp()
            self.L.dirname_pattern = temp_dir
            
            try:
                self.L.download_post(post, target=temp_dir)
            except Exception as e:
                return {"status": "error", "message": f"Download failed. Instagram may be limiting requests. Error: {str(e)}"}

            # Find video file
            video_file = None
            for f in os.listdir(temp_dir):
                if f.endswith(".mp4"):
                    video_file = os.path.join(temp_dir, f)
                    break

            if not video_file:
                return {"status": "error", "message": "Video file not found"}

            return {
                "status": "success",
                "caption": post.caption[:100] if post.caption else "No caption",
                "date": str(post.date_utc),
                "likes": post.likes,
                "comments": post.comments,
                "video_path": video_file
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
st.write("Paste a public Instagram video link below to watch or download it.")

url_input = st.text_input("Instagram Post URL", placeholder="https://www.instagram.com/reel/...")

if st.button("Download Video"):
    if url_input.strip() == "":
        st.error("Please enter a valid Instagram URL.")
    else:
        with st.spinner("Fetching video (this may take a moment)..."):
            downloader = InstagramVideoDownloader()
            result = downloader.download_single_post(url_input.strip())

        if result["status"] == "success":
            st.success("✅ Video Fetched!")
            st.write(f"**Caption:** {result['caption']}")
            st.write(f"📅 Date: {result['date']}")
            st.write(f"❤️ Likes: {result['likes']}")
            st.write(f"💬 Comments: {result['comments']}")

            # Show video in browser
            with open(result["video_path"], "rb") as f:
                video_bytes = f.read()
                st.video(video_bytes)
                st.download_button("⬇️ Download Video", video_bytes, file_name="instagram_video.mp4", mime="video/mp4")
        else:
            st.error(f"❌ {result['message']}")
            st.info("If you're seeing rate limit errors, please wait a few minutes and try again.")
