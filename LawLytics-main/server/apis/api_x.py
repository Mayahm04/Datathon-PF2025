import requests
from dotenv import load_dotenv
import os
from apis.helper import helper
import json

class ApiX:
    def __init__(self):
        ENV_PATH = "../api_x.env"
        load_dotenv(dotenv_path=ENV_PATH)
        self.BEARER_TOKEN = os.getenv("BEARER_TOKEN")
        self.url = "https://api.x.com/2/tweets/search/recent"

    def getTweets(self, keywords: str):
        headers = {
            "Authorization": f"Bearer {self.BEARER_TOKEN}"
        }

        params = {
            "query": keywords,
            "max_results": 10,
            "tweet.fields": "text"
        }

        response = requests.get(self.url, headers=headers, params=params)
        if response.status_code != 200:
            raise Exception(f"Request returned {response.status_code}: {response.text}")

        data = response.json()

        return data
    
    def setKeywords(self, keywords):
        self.keywords = keywords

    def createFile(self):
        data = self.getTweets(self.keywords)

        file_name = "x.json"

        with open(file_name, 'w') as json_file:
            json.dump(data, json_file, indent=4)

        helper.sendDataToBucket(source="x", file_path=file_name)

        os.remove(file_name)