from pytube import Playlist
import os
import re
import sys
from tqdm import tqdm

def download_playlist(url, output_path='./'):
    try:
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        print(f"Downloading playlist: {playlist.title}")

        # Create a directory for the playlist if it doesn't already exist
        playlist_dir = os.path.join(output_path, playlist.title)
        if not os.path.exists(playlist_dir):
            os.makedirs(playlist_dir)

        # List to store links of videos that couldn't be downloaded
        failed_videos = []

        # Total number of videos in the playlist
        total_videos = len(playlist.videos)
        print(f"Total videos: {total_videos}")

        # Iterate over each video in the playlist and download it
        for video in tqdm(playlist.videos, desc="Downloading videos"):
            video_title = video.title
            video_filename = video.streams.get_highest_resolution().default_filename

            # Check if the video file already exists in the directory
            if os.path.exists(os.path.join(playlist_dir, video_filename)):
                print(f"{video_title} is already available in the directory. Skipping...")
                continue

            # Download the video and display progress
            with tqdm(total=100, desc=f"Downloading {video_title}", unit="%", leave=False) as pbar:
                def progress_function(stream, chunk, bytes_remaining):
                    pbar.update((1 - bytes_remaining / video.streams.get_highest_resolution().filesize) * 100)

                stream_360p = video.streams.filter(res="360p").first()
                if stream_360p:
                    stream_360p.download(playlist_dir, on_progress_callback=progress_function)
                else:
                    stream_480p = video.streams.filter(res="480p").first()
                    if stream_480p:
                        stream_480p.download(playlist_dir, on_progress_callback=progress_function)
                    else:
                        stream_720p = video.streams.filter(res="720p").first()
                        if stream_720p:
                            stream_720p.download(playlist_dir, on_progress_callback=progress_function)
                        else:
                            highest_resolution = video.streams.get_highest_resolution()
                            try:
                                highest_resolution.download(playlist_dir, on_progress_callback=progress_function)
                            except:
                                failed_videos.append(video.watch_url)

        print("Download complete!")

        # Print links of videos that couldn't be downloaded
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
