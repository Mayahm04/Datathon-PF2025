from eventregistry import EventRegistry, QueryArticlesIter
from dotenv import load_dotenv
import os
from apis.helper import helper
from datetime import date, timedelta

class ApiNews:
    def __init__(self, keywords=[]):
        ENV_PATH = "../api_news.env"
        load_dotenv(dotenv_path=ENV_PATH)
        API_KEY = os.getenv("API_KEY")

        self.er = EventRegistry(apiKey=API_KEY)
        self.keywords = keywords

    def getRecentNews(self, days=5, max_articles=20):
        all_text = []
        today = date.today()
        start_date = today - timedelta(days=days)
        for keyword in self.keywords:
            q = QueryArticlesIter(
                keywords=keyword,
                dateStart=start_date.strftime("%Y-%m-%d"),
                dateEnd=today.strftime("%Y-%m-%d"),
                lang="eng"
            )
            count = 0
            for art in q.execQuery(self.er, sortBy="date", maxItems=max_articles):
                title = art.get("title", "")
                body = art.get("body", "")
                if body:
                    all_text.append(f"{title}\n{body}\n\n")
                    count += 1
                if count >= max_articles:
                    break
        return "".join(all_text)

    def setKeywords(self, keywords):
        self.keywords = keywords

    def createFiles(self):
        text = self.getRecentNews(days=5, max_articles=5)

        file_name = "news.txt"
        with open(file_name, "w", encoding="utf-8") as f:
            f.write(text)

        helper.sendDataToBucket(source="news", file_path=file_name)
        os.remove(file_name)