import requests
import json
from datetime import date # we will import the data once a day

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

api_key = os.getenv("API_KEY")
channel_handle = os.getenv("CHANNEL_HANDLE")
maxResults=50

def get_playlist_id():
    try:
        url=f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={channel_handle}&key={api_key}"

        response= requests.get(url)

        response.raise_for_status()  # Raise an exception for HTTP errors
                
        data=response.json()
                
        # print(json.dumps(data, indent=4))
                
        channel_items=data['items'][0]   
                
        channel_playlistId=channel_items['contentDetails']['relatedPlaylists']['uploads'] 

        return channel_playlistId
    
    except requests.exceptions.RequestException as e:
        print("Error occurred while making the API request:", e)
        raise e


def get_video_ids(playlist_id):
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResults}&playlistId={playlist_id}&key={api_key}"

    video_ids = []

    page_token = None

    try:

        while True:
            url = base_url
            if page_token:
                url += f"&pageToken={page_token}"# if pageToken is not None, append it to the URL (this means the API will return the next page of results)

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()
            # video_ids.extend([item['contentDetails']['videoId'] for item in data['items']])#this line extracts the video IDs from the API response and adds them to the video_ids list    

            for item in data['items']:
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            page_token = data.get('nextPageToken')
            if not page_token:
                break

        return video_ids

        # response = requests.get(base_url)
        # response.raise_for_status()  # Raise an exception for HTTP errors

        # data = response.json()
        # video_ids = [item['contentDetails']['videoId'] for item in data['items']]
        # return video_ids

    except requests.exceptions.RequestException as e:
        print("Error occurred while making the API request:", e)
        raise e


def extract_video_data(video_ids):
    extracted_data = []

    def batch_list(video_id_list, batch_size=50):# this function takes a list of video IDs and yields batches of the specified size (default is 50). It uses a generator to yield each batch one at a time, which is memory-efficient for large lists.
        for video_id in range(0, len(video_id_list), batch_size):
            yield video_id_list[video_id: video_id + batch_size]

    
    try:

        for batch in batch_list(video_ids):
            video_ids_str = ",".join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={api_key}"

            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            data = response.json()


            for item in data['items']:
                video_id=item['id']
                snippet=item['snippet']
                content_details=item['contentDetails']
                statistics=item['statistics']

                video_data = {
                    "video_id": video_id,
                    "title": snippet.get('title'),
                    "description": snippet.get('description'),
                    "published_at": snippet.get('publishedAt'),
                    "duration": content_details.get('duration'),
                    "view_count": statistics.get('viewCount', None),#this means that if the 'viewCount' key is not present in the statistics dictionary, it will return None instead of raising a KeyError
                    "like_count": statistics.get('likeCount', None),
                    "comment_count": statistics.get('commentCount', None),
                }    

            extracted_data.append(video_data)

        return extracted_data
    
    except requests.exceptions.RequestException as e:
        print("Error occurred while making the API request:", e)
        raise e


def save_to_json(extracted_data):
    file_path=f"./data/YT_data_{date.today()}.json"

    with open(file_path, 'w', encoding="utf-8") as json_outfile: #utf-8 ensure that the file can handle special characters
        json.dump(extracted_data, json_outfile, indent=4, ensure_ascii=False) #ensure_ascii=False ensures that non-ASCII characters are preserved in the output file



if __name__ == "__main__":
    playlist_id = get_playlist_id()  
    video_ids=get_video_ids(playlist_id)
    video_data=extract_video_data(video_ids)
    save_to_json(video_data)
    

# if __name__ == "__main__":
#     print("get_playlist_id will be executed when this script is run directly.")
#     get_playlist_id()
# else:
#     print("get_playlist_id will not be executed when this script is imported as a module.")