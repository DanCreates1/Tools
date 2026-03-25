import os
import sys
import subprocess
from pytubefix import YouTube


current_stage = "Downloading"

def progress_callback(stream, chunk, bytes_remaining):
    total_size = stream.filesize or stream.filesize_approx
    bytes_downloaded = total_size - bytes_remaining
    percent = bytes_downloaded / total_size * 100

    bar_length = 30
    filled_length = int(bar_length * percent // 100)
    bar = "█" * filled_length + "-" * (bar_length - filled_length)


    sys.stdout.write(f"\r{current_stage}: |{bar}| {percent:5.1f}%")
    sys.stdout.flush()


try:
    url = input("Enter YouTube URL: ")

   
    yt = YouTube(url, on_progress_callback=progress_callback)
    title = yt.title
    print(f"\nVideo found: {title}\n")

    
    base_path = os.path.dirname(os.path.abspath(__file__))
    download_folder = os.path.join(base_path, "downloads")
    os.makedirs(download_folder, exist_ok=True)

    
    print("Trying fast mode (progressive stream)...")
    progressive_stream = (
        yt.streams.filter(progressive=True, file_extension="mp4", res="720p").first()
        or yt.streams.filter(progressive=True, file_extension="mp4")
                     .order_by("resolution").desc().first()
    )

    if progressive_stream:
        current_stage = f"Downloading {progressive_stream.resolution}"
        output_path = os.path.join(download_folder, f"{title}.mp4")
        progressive_stream.download(output_path=download_folder, filename=f"{title}.mp4")
        sys.stdout.write("\n")  # new line after progress bar
        print(f"\n✅ Done (fast mode). Saved to:\n{output_path}")

    else:
       
        print("No progressive stream with audio found. Using merge mode...")

        
        current_stage = "Downloading video"
        video_stream = (
            yt.streams.filter(only_video=True, file_extension="mp4")
                      .order_by("resolution").desc().first()
        )
        video_path = video_stream.download(
            output_path=download_folder,
            filename="temp_video.mp4"
        )
        sys.stdout.write("\n")  
        
        current_stage = "Downloading audio"
        audio_stream = (
            yt.streams.filter(only_audio=True)
                      .order_by("abr").desc().first()
        )
        audio_path = audio_stream.download(
            output_path=download_folder,
            filename="temp_audio.mp3"
        )
        sys.stdout.write("\n")  

        
        print("Merging video + audio (FFmpeg)...")
        final_output = os.path.join(download_folder, f"{title}.mp4")

        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",   
            "-c:a", "aac",    
            final_output
        ]

        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        
        os.remove(video_path)
        os.remove(audio_path)

        print(f"\n✅ Done (merge mode). Saved to:\n{final_output}")

except Exception as e:
    print(f"\n❌ Error: {e}")
