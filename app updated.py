import streamlit as st
import requests
import re
import tempfile
import os

class InstagramVideoDownloader:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0.0.0 Safari/537.36"
        }

    def download_single_post(self, url: str) -> dict:
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code != 200:
                return {"status": "error", "message": "Failed to fetch Instagram page"}

            # Regex se direct video URL nikalna
            match = re.search(r'"video_url":"([^"]+)"', resp.text)
            if not match:
                return {"status": "error", "message": "No video found in this post"}

            video_url = match.group(1).replace("\\u0026", "&")

            # Video ko temporary file me save karna
            temp_dir = tempfile.mkdtemp()
            video_path = os.path.join(temp_dir, "video.mp4")

            with requests.get(video_url, headers=self.headers, stream=True) as r:
                r.raise_for_status()
                with open(video_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)

            return {
                "status": "success",
                "video_url": video_url,
                "video_path": video_path
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


# ---------------- STREAMLIT APP ----------------

st.set_page_config(page_title="Instagram Video Downloader", page_icon="📥")

st.title("📥 Instagram Video Downloader")
st.write("Paste a public Instagram video link below to watch or download it.")

url_input = st.text_input("Instagram Post URL", placeholder="https://www.instagram.com/reel/...")

if st.button("Download Video"):
    if url_input.strip() == "":
        st.error("Please enter a valid Instagram URL.")
    else:
        with st.spinner("Fetching video..."):
            downloader = InstagramVideoDownloader()
            result = downloader.download_single_post(url_input.strip())

        if result["status"] == "success":
            st.success("✅ Video Fetched!")

            # Show video in browser
            with open(result["video_path"], "rb") as f:
                video_bytes = f.read()
                st.video(video_bytes)
                st.download_button("⬇️ Download Video", video_bytes,
                                   file_name="instagram_video.mp4", mime="video/mp4")
        else:
            st.error(f"❌ {result['message']}")
