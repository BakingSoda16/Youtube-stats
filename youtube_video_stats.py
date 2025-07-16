import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load environment variables from .env
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")
CHANNEL_ID = os.getenv("CHANNEL_ID")

if not API_KEY or not CHANNEL_ID:
    raise EnvironmentError("Missing YOUTUBE_API_KEY or CHANNEL_ID in .env file")

# Set up YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

def get_uploads_playlist_id(channel_id):
    response = youtube.channels().list(
        part="contentDetails",
        id=channel_id
    ).execute()

    items = response.get("items", [])
    if not items:
        raise ValueError("Channel not found or no contentDetails returned")

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_video_ids_from_playlist(playlist_id):
    video_ids = []
    next_page_token = None

    while True:
        response = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        ).execute()

        for item in response.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return video_ids

def get_video_stats(video_ids):
    videos = []
    for i in range(0, len(video_ids), 50):
        chunk = video_ids[i:i+50]
        response = youtube.videos().list(
            part="snippet,statistics",
            id=",".join(chunk)
        ).execute()

        for item in response.get("items", []):
            stats = item["statistics"]
            snippet = item["snippet"]
            videos.append({
                "title": snippet["title"],
                "videoId": item["id"],
                "views": int(stats.get("viewCount", 0))
            })
    return videos

def find_extremes(videos):
    if not videos:
        print("No videos found.")
        return

    sorted_videos = sorted(videos, key=lambda x: x["views"])
    lowest = sorted_videos[0]
    highest = sorted_videos[-1]

    print("\n🔻 Lowest Viewed Video:")
    print(f"{lowest['title']} ({lowest['views']} views)")
    print(f"https://youtu.be/{lowest['videoId']}")

    print("\n🔺 Highest Viewed Video:")
    print(f"{highest['title']} ({highest['views']} views)")
    print(f"https://youtu.be/{highest['videoId']}")

def main():
    try:
        uploads_playlist_id = get_uploads_playlist_id(CHANNEL_ID)
        video_ids = get_video_ids_from_playlist(uploads_playlist_id)
        videos = get_video_stats(video_ids)
        find_extremes(videos)
        return videos  # ← Return for use in other scripts
    except Exception as e:
        print(f"❌ Error occurred: {e}")
        return []

if __name__ == "__main__":
    main()
