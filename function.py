import googleapiclient.discovery
import json
import os
from dotenv import load_dotenv

api_service_name = "youtube"
api_version = "v3"
# Load environment variables from .env file
load_dotenv()

# Access the API key from environment variables
developer_key = os.getenv('DEVELOPER_KEY')
DEVELOPER_KEY = developer_key

youtube = googleapiclient.discovery.build(
    api_service_name, api_version, developerKey=DEVELOPER_KEY
)

def search_youtube_videos(keyword, channel_id=None, filter_keywords=None):
    print(keyword)
    # Build the search request
    search_request = youtube.search().list(
        part="snippet",
        q=keyword,
        maxResults=5,  # Get the top 10 search results
        type="video",  # Search for videos only
        channelId=channel_id if channel_id else None  # Add the channelId parameter if provided
    )

    search_response = search_request.execute()

    results = []

    for item in search_response['items']:
        video_id = item['id']['videoId']
        channel_id = item['snippet']['channelId']

        # Get detailed information about the video using the video ID
        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        video_response = video_request.execute()

        video_title = video_response['items'][0]['snippet']['title']
        video_description = video_response['items'][0]['snippet']['description']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        video_views = video_response['items'][0]['statistics']['viewCount']

        # Get channel information to fetch the number of subscribers
        channel_request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()

        channel_subscribers = channel_response['items'][0]['statistics']['subscriberCount']

        # Check if filter keywords are provided
        if filter_keywords:
            # Check if any filter keyword is present in the video description
            if any(keyword.lower() in video_description.lower() for keyword in filter_keywords):
                results.append({
                    "title": video_title,
                    "description": video_description,
                    "link": video_link,
                    # "views": video_views,
                    # "subscribers": channel_subscribers
                })
        else:
            # No filter keywords provided, add all results
            results.append({
                "title": video_title,
                "description": video_description,
                "link": video_link,
                # "views": video_views,
                # "subscribers": channel_subscribers
            })

    # Output results as JSON and save to a file
    with open("search_results.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    return results
