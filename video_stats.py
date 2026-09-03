import requests
import json

import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

api_key = os.getenv("API_KEY")
channel_handle = os.getenv("CHANNEL_HANDLE")

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


if __name__ == "__main__":
    get_playlist_id()

    

# if __name__ == "__main__":
#     print("get_playlist_id will be executed when this script is run directly.")
#     get_playlist_id()
# else:
#     print("get_playlist_id will not be executed when this script is imported as a module.")