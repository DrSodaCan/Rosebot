from pytube import YouTube
import os

async def download_video(url, path=""):
    try:
        yt = YouTube(url)
        print(yt.title)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').all()
        d_video = stream[-1]
        stream.download(path)
        d_video.download(path)

        #When done, print where the file is
        print(f"Downloaded video to {os.path.join(path, yt.title)}.mp4")

        return 1
    except Exception as e:
        print("Couldn't download video:")
        print(e)
        return 0

