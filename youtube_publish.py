from googleapiclient.discovery import build
from google.oauth2 import service_account
import re

def publish_to_youtube(video_file_path, title, description, tags=[]):
    SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
    SERVICE_ACCOUNT_FILE = "backend/service_keys/youtube-service-account.json"

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    youtube = build('youtube', 'v3', credentials=credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": "22"
            },
            "status": {
                "privacyStatus": "public"
            }
        },
        media_body=video_file_path
    )

    response = request.execute()
    video_id = response.get('id', '')
    # Validate the video id to ensure it contains only safe characters
    if not re.match(r'^[A-Za-z0-9_-]{11}$', video_id):
        raise ValueError("Invalid video id received from YouTube API")
    return f"https://youtube.com/watch?v={video_id}"
