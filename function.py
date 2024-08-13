import sys
import json
import os
import shutil
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from dotenv import load_dotenv
import openai
import googleapiclient.discovery

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')
DEVELOPER_KEY = os.getenv('DEVELOPER_KEY')

CHROMA_PATH = "chroma"
DATA_PATH = "data/transcript"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

def get_video_id(url):
    """Extract the video ID from a YouTube URL."""
    video_id = None
    if 'v=' in url:
        video_id = url.split('v=')[1].split('&')[0]
    elif 'be/' in url:
        video_id = url.split('be/')[1].split('&')[0]
    return video_id

def get_transcript(video_url):
    """Fetch the transcript for a YouTube video."""
    video_id = get_video_id(video_url)
    if not video_id:
        return "Invalid YouTube URL."

    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([t['text'] for t in transcript])
        return text
    except Exception as e:
        return f"Could not retrieve a transcript: {str(e)}"

def save_transcript_as_markdown(text, filename):
    """Save the transcript as Markdown to a file."""
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text)
        print(f"Transcript saved to {filename}")
    except Exception as e:
        print(f"Could not save the transcript to file: {str(e)}")

def search_youtube_videos(keyword, channel_id=None, filter_keywords=None):
    """Search for YouTube videos and return results."""
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=DEVELOPER_KEY)
    
    search_request = youtube.search().list(
        part="snippet",
        q=keyword,
        maxResults=3,
        type="video",
        channelId=channel_id if channel_id else None
    )

    search_response = search_request.execute()
    results = []

    for item in search_response['items']:
        video_id = item['id']['videoId']
        channel_id = item['snippet']['channelId']

        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        video_response = video_request.execute()

        video_title = video_response['items'][0]['snippet']['title']
        video_description = video_response['items'][0]['snippet']['description']
        video_link = f"https://www.youtube.com/watch?v={video_id}"
        video_views = video_response['items'][0]['statistics']['viewCount']

        channel_request = youtube.channels().list(
            part="statistics",
            id=channel_id
        )
        channel_response = channel_request.execute()

        channel_subscribers = channel_response['items'][0]['statistics']['subscriberCount']

        if filter_keywords:
            if any(keyword.lower() in video_description.lower() for keyword in filter_keywords):
                results.append({
                    "title": video_title,
                    "description": video_description,
                    "link": video_link,
                    # "views": video_views,
                    # "subscribers": channel_subscribers
                })
        else:
            results.append({
                "title": video_title,
                "description": video_description,
                "link": video_link,
                # "views": video_views,
                # "subscribers": channel_subscribers
            })

    with open("search_results.json", "w") as json_file:
        json.dump(results, json_file, indent=4)

    return results

def transcript_analyzer(query_text, youtube_url=None, search_keyword=None):
    if youtube_url:
        transcript_text = get_transcript(youtube_url)
        if isinstance(transcript_text, str) and ("Invalid YouTube URL." in transcript_text or "Could not retrieve a transcript" in transcript_text):
            print(transcript_text)
        else:
            save_transcript_as_markdown(transcript_text, os.path.join(DATA_PATH, "youtube_transcript.md"))
            generate_data_store()
    elif search_keyword:
        results = search_youtube_videos(search_keyword)
        print(json.dumps(results, indent=4))
        return

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    print("QUERY_TEXT:", query_text)
    results = db.similarity_search_with_relevance_scores(query_text, k=3)
    if len(results) == 0 or results[0][1] < 0.7:
        print(f"Unable to find matching results.")
        return

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    model = ChatOpenAI()
    response_text = model.invoke(prompt)
    print(response_text.content)

def generate_data_store():
    documents = load_documents()
    chunks = split_text(documents)
    save_to_chroma(chunks)

def load_documents():
    loader = DirectoryLoader(DATA_PATH, glob="*.md")
    documents = loader.load()
    return documents

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=100,
        length_function=len,
        add_start_index=True,
    )
    chunks = text_splitter.split_documents(documents)
    return chunks

def save_to_chroma(chunks):
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    db = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH)
    db.persist()

