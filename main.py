from pytube import Playlist
import os
import re
import sys
from tqdm import tqdm
import requests

def download_file(url, filepath):
    # Download the file using requests library
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))

    # Open the file and write the contents of the response
    with open(filepath, 'wb') as f:
        with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(filepath), ncols=100) as pbar:
            for data in response.iter_content(chunk_size=1024):
                f.write(data)
                pbar.update(len(data))

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
        for i, video in enumerate(playlist.videos):
            video_title = f"{i+1:02d} - {video.title}"

            # Get the resolution of the downloaded stream
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

            video_filename = f"{i+1:02d}_{video.title}_{resolution}p.mp4"
            video_filepath = os.path.join(playlist_dir, video_filename)

            # Check if the video file already exists in the directory
            if os.path.exists(video_filepath):
                print(f"{video_title} is already available in the directory. Skipping...")
                continue

            # Download the video and display progress
            print(f"Downloading {video_title}...")
            download_file(stream.url, video_filepath)

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
