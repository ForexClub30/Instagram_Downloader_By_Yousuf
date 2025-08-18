import instaloader
import os
from urllib.parse import urlparse
import argparse
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
        self.delay_between_downloads = 5  # seconds to avoid rate limiting

    def download_single_post(self, url: str, folder: str = "downloads") -> bool:
        """Download video from a single Instagram post"""
        try:
            if not os.path.exists(folder):
                os.makedirs(folder)

            shortcode = self._extract_shortcode(url)
            if not shortcode:
                return False

            post = instaloader.Post.from_shortcode(self.L.context, shortcode)
            
            if not post.is_video:
                print(f"⚠️ The post {url} doesn't contain a video. Skipping...")
                return False

            self.L.dirname_pattern = folder
            self.L.download_post(post, target=folder)
            
            print(f"\n✅ Video downloaded successfully to {folder}/")
            print(f"📌 Caption: {post.caption[:50]}..." if post.caption else "No caption")
            print(f"📅 Date: {post.date_utc}")
            print(f"❤️ Likes: {post.likes}")
            print(f"💬 Comments: {post.comments}")
            return True

        except Exception as e:
            print(f"❌ Error downloading post {url}: {str(e)}")
            return False

    def download_bulk_posts(self, urls: list, folder: str = "downloads") -> dict:
        """Download multiple Instagram posts from a list of URLs"""
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'total': len(urls)
        }
        
        print(f"\n⏳ Starting bulk download of {len(urls)} posts...\n")
        
        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url:
                continue
                
            print(f"\n📥 Processing {i}/{len(urls)}: {url}")
            
            try:
                if self.download_single_post(url, folder):
                    results['success'] += 1
                else:
                    results['skipped'] += 1
            except Exception as e:
                print(f"❌ Unexpected error with {url}: {str(e)}")
                results['failed'] += 1
            
            # Add delay between downloads to avoid rate limiting
            if i < len(urls):
                print(f"\n⏳ Waiting {self.delay_between_downloads} seconds before next download...")
                time.sleep(self.delay_between_downloads)
        
        print("\n" + "="*50)
        print(f"📊 Download Summary:")
        print(f"✅ Success: {results['success']}")
        print(f"⚠️ Skipped: {results['skipped']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"📂 Saved to: {os.path.abspath(folder)}")
        print("="*50)
        
        return results

    def _extract_shortcode(self, url: str) -> str:
        """Extract shortcode from Instagram URL"""
        try:
            parsed_url = urlparse(url)
            path_parts = parsed_url.path.strip("/").split("/")
            
            if len(path_parts) >= 2 and path_parts[0] in ["p", "reel", "tv"]:
                return path_parts[1]
            
            print(f"❌ Invalid Instagram URL format: {url}")
            return None
        except Exception as e:
            print(f"❌ Could not parse URL {url}: {str(e)}")
            return None

def get_bulk_links_from_input():
    """Get multiple links from user input"""
    print("\n" + "="*50)
    print("📋 Paste multiple Instagram links (one per line)")
    print("Press Enter twice when finished")
    print("="*50 + "\n")
    
    links = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                if len(links) > 0:
                    break
                else:
                    continue
            if "instagram.com" in line:
                links.append(line.strip())
            else:
                print(f"⚠️ Skipping non-Instagram link: {line}")
        except EOFError:
            break
    
    return links

def main():
    print("\n" + "="*50)
    print("📱 INSTAGRAM BULK VIDEO DOWNLOADER".center(50))
    print("="*50 + "\n")

    parser = argparse.ArgumentParser(description='Download videos from public Instagram content')
    parser.add_argument('--url', type=str, help='Single Instagram post URL to download')
    parser.add_argument('--file', type=str, help='Text file containing multiple Instagram URLs (one per line)')
    parser.add_argument('--folder', type=str, default="downloads", help='Download folder (default: downloads)')
    parser.add_argument('--delay', type=int, default=5, help='Delay between downloads in seconds (default: 5)')
    
    args = parser.parse_args()

    downloader = InstagramVideoDownloader()
    downloader.delay_between_downloads = args.delay

    if args.url:
        # Single URL download
        downloader.download_single_post(args.url, args.folder)
    elif args.file:
        # Bulk download from file
        try:
            with open(args.file, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
            downloader.download_bulk_posts(urls, args.folder)
        except Exception as e:
            print(f"❌ Error reading file: {str(e)}")
    else:
        # Interactive mode
        print("Choose download mode:")
        print("1. Single post download")
        print("2. Bulk download by pasting multiple links")
        print("3. Bulk download from text file")
        
        choice = input("\nEnter your choice (1-3): ")
        
        if choice == "1":
            url = input("Enter Instagram post URL: ")
            downloader.download_single_post(url, args.folder)
        elif choice == "2":
            urls = get_bulk_links_from_input()
            if urls:
                downloader.download_bulk_posts(urls, args.folder)
            else:
                print("❌ No valid Instagram links provided")
        elif choice == "3":
            file_path = input("Enter path to text file containing URLs: ")
            try:
                with open(file_path, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                downloader.download_bulk_posts(urls, args.folder)
            except Exception as e:
                print(f"❌ Error reading file: {str(e)}")
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
