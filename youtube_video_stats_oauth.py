import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import json

# If you want to cache the token so users don’t re-auth every time
TOKEN_FILE = "token.json"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

def get_authenticated_service():
    creds = None
    # Load credentials from file if available
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as token:
            creds_data = json.load(token)
        creds = creds_data  # You can refresh token logic later if needed
    else:
        # Run the OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            "client_secret.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        # Save token
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)

def get_uploads_playlist_id(youtube):
    response = youtube.channels().list(
        part="contentDetails",
        mine=True
    ).execute()

    items = response.get("items", [])
    if not items:
        raise ValueError("No channels found for this user.")

    return items[0]["contentDetails"]["relatedPlaylists"]["uploads"]

def get_video_ids(youtube, playlist_id):
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

def get_video_stats(youtube, video_ids):
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
    youtube = get_authenticated_service()
    playlist_id = get_uploads_playlist_id(youtube)
    video_ids = get_video_ids(youtube, playlist_id)
    videos = get_video_stats(youtube, video_ids)
    find_extremes(videos)
    return videos

if __name__ == "__main__":
    main()
