import os
import json
import argparse
import asyncio
import aiohttp
from typing import List, Dict

# File to store the blocklist
BLOCKLIST_FILE = "adguard_blocklist.txt"

async def fetch_video_ids(session: aiohttp.ClientSession, channel_url: str, verbose: bool) -> List[str]:
    try:
        if verbose:
            print(f"Fetching video IDs for channel: {channel_url}")
        
        cmd = f"yt-dlp -j --flat-playlist {channel_url}"
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        
        if stderr:
            print(f"Error fetching video IDs for {channel_url}: {stderr.decode()}")
            return []
        
        video_data = stdout.decode().splitlines()
        video_ids = [json.loads(video)['id'] for video in video_data]
        
        if verbose:
            print(f"Found {len(video_ids)} videos for channel: {channel_url}")
        
        return video_ids
    except Exception as e:
        print(f"Error fetching video IDs for {channel_url}: {e}")
        return []

async def generate_blocklist(channels: List[str], verbose: bool):
    if verbose:
        print(f"Generating blocklist for {len(channels)} channels")
    
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_video_ids(session, channel, verbose) for channel in channels]
        results = await asyncio.gather(*tasks)
    
    total_videos = sum(len(video_ids) for video_ids in results)
    
    with open(BLOCKLIST_FILE, "w") as file:
        for video_ids in results:
            for video_id in video_ids:
                file.write(f"||youtube.com/watch?v={video_id}^\n")
    
    if verbose:
        print(f"Blocklist generated with {total_videos} video IDs")

def load_channels_from_file(file_path: str, verbose: bool) -> List[str]:
    if verbose:
        print(f"Loading channels from file: {file_path}")
    
    with open(file_path, 'r') as file:
        channels = [line.strip() for line in file if line.strip()]
    
    if verbose:
        print(f"Loaded {len(channels)} channels from file")
    
    return channels

def main():
    parser = argparse.ArgumentParser(description="Generate an AdGuard blocklist for YouTube channels.")
    parser.add_argument("-f", "--file", help="Path to a file containing YouTube channel URLs (one per line)")
    parser.add_argument("-c", "--channels", nargs='+', help="List of YouTube channel URLs")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if args.file:
        channels = load_channels_from_file(args.file, args.verbose)
    elif args.channels:
        channels = args.channels
        if args.verbose:
            print(f"Using {len(channels)} channels provided via command line")
    else:
        print("Error: Please provide either a file (-f) or a list of channels (-c)")
        return

    asyncio.run(generate_blocklist(channels, args.verbose))
    print(f"Blocklist generated: {BLOCKLIST_FILE}")

if __name__ == "__main__":
    main()
