import streamlit as st
import instaloader
import tempfile
import os
from urllib.parse import urlparse

class InstagramVideoDownloader:
    def __init__(self):
        self.L = instaloader.Instaloader(
            save_metadata=False,
            download_videos=True,
            download_video_thumbnails=False,
            post_metadata_txt_pattern="",
            compress_json=False
        )

    def download_single_post(self, url: str) -> dict:
        try:
            shortcode = self._extract_shortcode(url)
            if not shortcode:
                return {"status": "error", "message": "Invalid Instagram URL"}

            post = instaloader.Post.from_shortcode(self.L.context, shortcode)

            if not post.is_video:
                return {"status": "error", "message": "This post does not contain a video"}

            # Temporary folder for Streamlit
            temp_dir = tempfile.mkdtemp()
            self.L.dirname_pattern = temp_dir
            self.L.download_post(post, target=temp_dir)

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
        with st.spinner("Fetching video..."):
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
