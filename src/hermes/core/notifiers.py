import json
from typing import Tuple
from hermes.core.exceptions import NoNewArticles
from pathlib import PurePath

class BaseNotifier():
    """
    Base Notifier class which all notifiers should inherit from
    """

    def __init__(self, receivers_path: str=None) -> None:
        self.articles = None
        self.receivers = None
        
        if isinstance(receivers_path, PurePath):
            self.receivers_path = receivers_path
        else:
            raise NotImplementedError(f"Add `receivers_path` type {PurePath} argument, not {type(receivers_path)}")

    def notify(self) -> None:
        articles = self.get_articles()
        receivers = self.get_receivers()
        
        articles, receivers = self.pre_notify(articles, receivers)
        
        try: 
            self.send_notifications(articles, receivers)
            ex = None
        except Exception as e:
            ex = e
 

        raise_exception = self.post_notify(ex, articles, receivers)

        if raise_exception and ex:
            raise ex

    def pre_notify(self, articles: list, receivers: list, *args, **kwargs) -> Tuple[list, list]:
        """
        Executes before notifying
        """
        return articles, receivers

    def send_notifications(self, articles: list, receivers: list, *args, **kwargs) -> None:
        raise NotImplementedError()

    def post_notify(self, ex: Exception, articles: list, receivers: list, *args, **kwargs) -> bool:
        """
        Executes after notifying
        """
        return True

    def set_articles(self, articles: list) -> None:
        if isinstance(articles, list):
            self.articles = articles
        else:
            raise TypeError("`articles` must be a list")

    def get_articles(self):
        if self.articles:
            return self.articles
        else:
            raise NoNewArticles("No new articles or articles have not been set")
    
    def read_receivers_from_json(self, json_path: str=None) -> None:
        if json_path == None and self.receivers_path is not None:
            json_path = self.receivers_path
        else:
            raise NotImplementedError("`json_path` must be set at some point before reading file")

        with open(json_path, 'r') as f:
            self.receivers = json.load(f)
            return self.receivers

    def get_receivers(self) -> list:
        if self.receivers:
            return self.receivers
        else:
            raise NotImplementedError("`receivers` not provided")