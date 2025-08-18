import streamlit as st
import instaloader
import os
from urllib.parse import urlparse
import time

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stTextInput input {
        border-radius: 8px !important;
        border: 1px solid #ced4da !important;
    }
    .stButton button {
        background-color: #405de6 !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 8px 16px !important;
        border: none !important;
        width: 100%;
    }
    .stButton button:hover {
        background-color: #3749aa !important;
    }
    .success-box {
        background-color: #e6f7ee;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }
    .error-box {
        background-color: #fde8e8;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
    }
    .info-text {
        color: #6c757d;
        font-size: 0.9em;
    }
    .stats-container {
        display: flex;
        justify-content: space-between;
        margin-top: 15px;
    }
    .stat-box {
        background-color: white;
        border-radius: 8px;
        padding: 10px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        flex: 1;
        margin: 0 5px;
    }
    .header-container {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .header-icon {
        font-size: 2.5rem;
        margin-right: 15px;
    }
    </style>
    """, unsafe_allow_html=True)

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
                return {"status": "error", "message": "This post doesn't contain a video"}

            self.L.dirname_pattern = folder
            self.L.download_post(post, target=folder)

            return {
                "status": "success",
                "caption": post.caption[:100] + "..." if post.caption else "No caption",
                "date": str(post.date_utc),
                "likes": post.likes,
                "comments": post.comments,
                "username": post.owner_username,
                "media": post.url
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

# App Header
st.markdown("""
<div class="header-container">
    <div class="header-icon">📥</div>
    <div>
        <h1 style="margin: 0;">Instagram Video Downloader By Yousuf</h1>
        <p style="margin: 0; color: #6c757d;">Download videos from public Instagram posts</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Form
with st.form("download_form"):
    url_input = st.text_input(
        "Instagram Post URL",
        placeholder="https://www.instagram.com/reel/...",
        help="Paste the URL of a public Instagram post (Reel, TV, or regular video post)"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        folder_name = st.text_input(
            "Save to folder",
            value="instagram_videos",
            help="Folder where videos will be saved"
        )
    with col2:
        delay_time = st.slider(
            "Download delay (seconds)",
            1, 10, 2,
            help="Delay between download attempts to avoid rate limiting"
        )
    
    submit_button = st.form_submit_button("Download Video")

# Download Logic
if submit_button:
    if not url_input.strip():
        st.error("Please enter a valid Instagram URL.")
    else:
        with st.spinner("Downloading video... Please wait"):
            downloader = InstagramVideoDownloader()
            downloader.delay_between_downloads = delay_time
            result = downloader.download_single_post(url_input.strip(), folder_name.strip())
        
        if result["status"] == "success":
            st.markdown("""
            <div class="success-box">
                <h3 style="color: #28a745; margin-bottom: 15px;">✅ Download Complete!</h3>
                <p><strong>Caption:</strong> {caption}</p>
                <div class="stats-container">
                    <div class="stat-box">
                        <div>📅</div>
                        <div><strong>Posted</strong></div>
                        <div>{date}</div>
                    </div>
                    <div class="stat-box">
                        <div>❤️</div>
                        <div><strong>Likes</strong></div>
                        <div>{likes:,}</div>
                    </div>
                    <div class="stat-box">
                        <div>💬</div>
                        <div><strong>Comments</strong></div>
                        <div>{comments:,}</div>
                    </div>
                </div>
                <p style="margin-top: 15px;"><strong>By:</strong> @{username}</p>
            </div>
            """.format(
                caption=result["caption"],
                date=result["date"].split()[0],
                likes=result["likes"],
                comments=result["comments"],
                username=result["username"]
            ), unsafe_allow_html=True)
            
            # Show success message
            st.balloons()
            
        else:
            st.markdown("""
            <div class="error-box">
                <h3 style="color: #dc3545; margin-bottom: 15px;">❌ Download Failed</h3>
                <p>{message}</p>
                <p class="info-text">Please check the URL and try again. Make sure the post is public.</p>
            </div>
            """.format(message=result["message"]), unsafe_allow_html=True)

# Information Section
st.markdown("---")
st.markdown("### How to use:")
st.markdown("""
1. Copy the URL of a public Instagram video (Reel, TV, or regular post)
2. Paste it in the input field above
3. Click "Download Video"
4. Wait for the download to complete
""")

st.markdown("### Notes:")
st.markdown("""
- Only works with public Instagram accounts
- Videos are saved in the specified folder
- Respect Instagram's terms of service
""")

