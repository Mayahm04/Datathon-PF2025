from apis.api_news import ApiNews
from apis.api_reddit import ApiReddit
from apis.api_x import ApiX

class Apis:
    def __init__(self):
        self.api_news = ApiNews()
        self.api_reddit = ApiReddit()
        self.api_x = ApiX()

    def set_all_keywords(self, keywords: list[str]):
        self.api_news.setKeywords(keywords)
        self.api_reddit.setKeywords(keywords)
        self.api_reddit.setSubreddits(keywords)
        self.api_x.setKeywords("".join(keywords))

    def create_all_files(self):
        self.api_news.createFiles()
        self.api_reddit.createFile()
        try:
            self.api_x.createFile()
        except Exception as e:
            print(f"API Key for X on cooldown")

apis = Apis()