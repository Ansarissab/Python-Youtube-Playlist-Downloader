import re
from pytube import Playlist
import sys
import os

def download_playlist(url, output_path='./'):
    try:
        playlist = Playlist(url)
        playlist._video_regex = re.compile(r"\"url\":\"(/watch\?v=[\w-]*)")
        print(f"Downloading playlist: {playlist.title}")

        # Create a directory for the playlist
        playlist_dir = os.path.join(output_path, playlist.title)
        os.makedirs(playlist_dir, exist_ok=True)

        # Iterate over each video in the playlist and download it
        for video in playlist.videos:
            print(f"Downloading {video.title}...")
            video.streams.get_highest_resolution().download(playlist_dir)

        print("Download complete!")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# def get_playlist_size(url):
#     try:
#         playlist = Playlist(url)
#         total_size_bytes = sum(video.streams.get_highest_resolution().filesize for video in playlist.videos)
#         total_size_gb = total_size_bytes / (1024 * 1024 * 1024)  # Convert bytes to GB
#         return total_size_gb
#     except Exception as e:
#         print(f"An error occurred: {str(e)}")
#         return None

# if __name__ == "__main__":
#     playlist_url = input("Enter the YouTube playlist URL: ")
#     total_size = get_playlist_size(playlist_url)
#     if total_size is not None:
#         print(f"Total size of the playlist: {total_size:.2f} GB")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <playlist_url>")
        sys.exit(1)

    playlist_url = sys.argv[1]
    download_playlist(playlist_url)
