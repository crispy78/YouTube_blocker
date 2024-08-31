import os
import subprocess

# List of YouTube channel URLs
channels = [
    "https://www.youtube.com/c/ChannelName1",
    "https://www.youtube.com/c/ChannelName2",
    # Add more channels as needed
]

# File to store the blocklist
blocklist_file = "adguard_blocklist.txt"

def get_video_urls(channel_url):
    try:
        # Use yt-dlp to get video URLs from the channel
        result = subprocess.run(['yt-dlp', '-j', '--flat-playlist', channel_url], capture_output=True, text=True)
        video_data = result.stdout.splitlines()
        video_urls = [f"https://www.youtube.com/watch?v={json.loads(video)['id']}" for video in video_data]
        return video_urls
    except Exception as e:
        print(f"Error fetching video URLs for {channel_url}: {e}")
        return []

def generate_blocklist(channels):
    with open(blocklist_file, "w") as file:
        for channel in channels:
            video_urls = get_video_urls(channel)
            for url in video_urls:
                # Extract the base domain to block entire YouTube video page for that channel's videos
                domain = url.replace("https://www.youtube.com/watch?v=", "")
                file.write(f"||youtube.com/watch?v={domain}^\n")

if __name__ == "__main__":
    generate_blocklist(channels)
    print(f"Blocklist generated: {blocklist_file}")
