import webbrowser

import requests


class Pocket(object):
    """
    Class to connect to the Pocket app, retrieve the user's article list,
    retrieve their original URLs
    in order for Epubify to convert the original URLs into epub files
    """

    POCKET_REQUEST_HEADERS = {"content-type": "application/json; charset=UTF8", "X-Accept": "application/json"}

    def __init__(self, consumer_key, redirect_url, access_token=None):
        """
        The constructor receives a keyword argument list, which
        will be used to fetch information about the Pocket app,
        credential file path etc
        :param kwargs: keyword arguments
        """

        self.__access_token = None
        self.consumer_key = consumer_key
        self.redirect_url = redirect_url
        self.pocket_list = ""

        if access_token is None:
            self.__access_token = self.__get_access_token()
        else:
            self.__access_token = access_token

    def __post_request(self, params, base_url, headers=None):
        response = requests.post(base_url, json=params, headers=headers)

        if response.headers.get("X-Error"):
            response.raise_for_status()

        return response

    def __get_access_code(self):
        print(">> Executing Pocket step 1 [Authentication].. ")

        url = "https://getpocket.com/v3/oauth/request"

        params = {"consumer_key": self.consumer_key, "redirect_uri": self.redirect_url}

        access_code = (
            self.__post_request(base_url=url, params=params, headers=Pocket.POCKET_REQUEST_HEADERS)
            .json()
            .get("code", None)
        )

        if not access_code:
            raise Exception("missing code in authentication responce")

        url = f"https://getpocket.com/auth/authorize?request_token={access_code}&redirect_uri={self.redirect_url}"

        print(
            """
            Your browser will now open the following URL automatically. Please authorize ePubify
            If the browser doesn't load automatically, please click on the link.
            If you have already authorized ePubify, you will see the \"THANK YOU\" page directly.
            Then, please come back here and <PUSH ANY KEY TO CONTINUE>...
            URL: {url}
            """.format(
                url=url
            )
        )
        webbrowser.open_new_tab(url)
        input()
        print(">> Step 2 [Authorization] complete.")
        return access_code

    def __get_access_token(self):
        if self.__access_token:
            return self.__access_token

        access_code = self.__get_access_code()

        print(">> Executing Pocket step 3 [Authorization].. ")

        params = {
            "consumer_key": self.consumer_key,
            "code": access_code,
        }

        url = "https://getpocket.com/v3/oauth/authorize"
        access_token = (
            self.__post_request(base_url=url, params=params, headers=Pocket.POCKET_REQUEST_HEADERS)
            .json()
            .get("access_token", None)
        )

        if not access_token:
            raise Exception("no valid access token")

        print(">> Step 3 [Authorization] complete.")
        return access_token

    def fetch_pocket_articles(self):
        # http://getpocket.com/developer/docs/v3/retrieve

        url = "https://getpocket.com/v3/get"
        params = {
            "consumer_key": self.consumer_key,
            "access_token": self.__access_token,
            "sort": "newest",
            "contentType": "article",
            "detailType": "simple",
        }

        response = self.__post_request(base_url=url, params=params, headers=Pocket.POCKET_REQUEST_HEADERS)
        articles = response.json().get("list", None)

        if articles is None:
            raise Exception("cannto fetch articles")

        self.articles = articles
        print(">> Article list successfully retrieved from Pocket.")
        return articles

    def get_article_list(self):
        all_articles = self.fetch_pocket_articles()

        return [
            {"url": article["given_url"], "title": article["resolved_title"], "author": "epubify"}
            for _, article in all_articles.items()
        ]
