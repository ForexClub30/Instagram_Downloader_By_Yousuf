import streamlit as st
import instaloader
import time

st.set_page_config(page_title="Instagram Downloader by Yousuf", page_icon="📸", layout="centered")

st.title("📸 Instagram Post Downloader")
st.write("Download Instagram photos/videos by entering the post URL.")

# Input
url = st.text_input("Enter Instagram Post URL", placeholder="https://www.instagram.com/p/SHORTCODE/")

# Login credentials (for private / rate-limit handling)
username = st.text_input("Instagram Username (optional)")
password = st.text_input("Instagram Password (optional)", type="password")

if st.button("Download"):
    if not url:
        st.error("⚠️ Please enter a valid Instagram URL.")
    else:
        loader = instaloader.Instaloader(download_videos=True, download_video_thumbnails=False, save_metadata=False)
        try:
            # Login if provided
            if username and password:
                st.info("🔑 Logging in...")
                loader.login(username, password)

            shortcode = url.split("/")[-2]
            post = instaloader.Post.from_shortcode(loader.context, shortcode)

            st.success("✅ Post fetched successfully!")

            if post.is_video:
                st.video(post.video_url)
                st.write("🎥 [Download Video](" + post.video_url + ")")
            else:
                st.image(post.url)
                st.write("🖼️ [Download Image](" + post.url + ")")

        except instaloader.exceptions.ConnectionException as e:
            st.error("🚫 Instagram blocked the request. Please wait a few minutes or login with credentials.")
            st.write(f"**Error details:** {str(e)}")

        except Exception as e:
            st.error("⚠️ Something went wrong.")
            st.write(f"**Error details:** {str(e)}")
