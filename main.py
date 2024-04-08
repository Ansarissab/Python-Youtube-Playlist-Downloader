from concurrent.futures import ThreadPoolExecutor
from pytube import Playlist
import os
import re
import sys
from tqdm import tqdm
import requests

def download_file(url, filepath):
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    with open(filepath, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(filepath), ncols=100) as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))

def download_video(video, output_path, index):
    video_title = f"{index:02d} - {video.title}"

    resolution = None
    stream_360p = video.streams.filter(res="360p").first()
    stream_480p = video.streams.filter(res="480p").first()
    stream_720p = video.streams.filter(res="720p").first()
    if stream_360p:
        resolution = "360"
        stream = stream_360p
    elif stream_480p:
        resolution = "480"
        stream = stream_480p
    elif stream_720p:
        resolution = "720"
        stream = stream_720p
    else:
        resolution = "unknown"
        stream = video.streams.get_highest_resolution()

    video_filename = f"{index:02d}_{video.title}_{resolution}p.mp4"
    video_filepath = os.path.join(output_path, video_filename)

    # Check if the file already exists in the directory
    if os.path.exists(video_filepath):
        print(f"{video_title} is already available in the directory. Skipping...")
        return

    download_file(stream.url, video_filepath)

def download_playlist(url, output_path='./', max_workers=5):
    try:
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        print(f"Downloading playlist: {playlist.title}")
        playlist_dir = os.path.join(output_path, playlist.title)
        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)
        failed_videos = []
        total_videos = len(playlist.videos)
        print(f"Total videos: {total_videos}")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for i, video in enumerate(playlist.videos, start=1):
                futures.append(executor.submit(download_video, video, playlist_dir, i))
            for future in tqdm(futures, desc="Downloading videos", total=total_videos):
                try:
                    future.result()
                except Exception as e:
                    failed_videos.append(str(e))

        print("Download complete!")

        if failed_videos:
            print("The following videos could not be downloaded:")
            for link in failed_videos:
                print(link)
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <playlist_url>")
        sys.exit(1)
    playlist_url = sys.argv[1]
    download_playlist(playlist_url)
