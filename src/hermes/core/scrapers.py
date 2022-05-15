import requests
from time import ctime

class BaseScraper():
    """
    Base Scraper class, which should be used as a parent for all scrapers
    """


    name = None
    verbose_name = None

    def __init__(self, url: str=None) -> None:
        if self.name == None:
            raise NotImplementedError("Add `name` attribute, to scraper class")

        if self.verbose_name == None:
            self.verbose_name = self.name

        self.HTML_PARSER = 'html.parser'

        if url is None:
            raise Exception('URL not provided, add url argument')
        else:
            self.url = url

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0',
            'Accept-Language': 'pl,en-US;q=0.7,en;q=0.3',
        }

        self.cookies = {
        }

    def get_html(self, url: str=None, headers: dict=None, cookies: dict=None) -> str:
        """
        Makes a request to `url` if it succeds, returns html, otherwise raises Exception
        """


        if url is None:
            url = self.url

        if headers is None:
            headers = self.headers

        if cookies is None:
            cookies = self.cookies


        req = requests.get(url, headers=headers, cookies=cookies)

        # check if request was successful
        if req.ok:
            return req.text
        else:
            raise Exception(f"Request failed, code: {req.status_code}, url {req.url}")


    def get_data_from_html(self, html: str, max_items: int=None) -> list:
        raise NotImplementedError()

    def get_cleaned_data(self, data: list) -> list:
        raise NotImplementedError()

    def __str__(self) -> str:
        return self.name

    def get_attrs_as_dict(self) -> dict:
        return {
            "scraper_name": self.name,
            "scraper_verbose_name": self.verbose_name,
            "scraper_url": self.url,
            "scraper_cookies": self.cookies,
            "scraper_headers": self.headers,
        }

