import praw
import prawcore
from dotenv import load_dotenv
import os
from apis.helper import helper

class ApiReddit:
    def __init__(self, keywords=[], subreddits=[]):
        ENV_PATH = "../api_reddit.env"

        load_dotenv(dotenv_path=ENV_PATH)

        CLIENT_ID = os.getenv("CLIENT_ID")
        CLIENT_SECRET = os.getenv("SECRET")
        USER_AGENT = os.getenv("USER_AGENT")
        self.reddit = praw.Reddit(client_id=CLIENT_ID,
                                  client_secret=CLIENT_SECRET,
                                  user_agent=USER_AGENT)

        self.keywords = keywords
        self.subreddits = subreddits

    def setKeywords(self, keywords: list[str]):
        self.keywords = keywords

    def setSubreddits(self, subreddits):
        valid_subreddits = []
        for sub in subreddits:
            try:
                subreddit = self.reddit.subreddit(sub)
                _ = subreddit.id
                valid_subreddits.append(sub)
            except prawcore.exceptions.NotFound:
                print(f"⚠️ Subreddit '{sub}' introuvable.")
            except prawcore.exceptions.Forbidden:
                print(f"🚫 Subreddit '{sub}' est privé ou restreint.")
            except Exception as e:
                print(f"⚠️ Erreur sur '{sub}': {e}")
        self.subreddits = valid_subreddits

    def getPosts(self):
        text = []
        for subreddit_name in self.subreddits:
            subreddit = self.reddit.subreddit(subreddit_name)
            for keyword in self.keywords:
                for submission in subreddit.search(keyword, sort="new", limit=5):
                    text.append(submission.selftext)
                    text.append("\n")
        return "".join(text)

    def createFile(self):
        text = self.getPosts()
        file_name = "reddit.txt"

        with open(file_name, 'w') as file:
            file.write(text)

        helper.sendDataToBucket(source="reddit", file_path=file_name)
        os.remove(file_name)