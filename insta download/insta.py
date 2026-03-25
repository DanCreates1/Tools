import os
from yt_dlp import YoutubeDL

DOWNLOAD_DIR = "downloads"

def download_reel(url: str):
    # Create download folder if it doesn't exist
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    ydl_opts = {
        # Best video + best audio, merged into MP4
        "format": "bv*+ba/best",
        "merge_output_format": "mp4",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "quiet": False,
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    url = input("Enter Instagram Reel URL: ").strip()
    download_reel(url)
    print("Download complete. File saved to /downloads.")
