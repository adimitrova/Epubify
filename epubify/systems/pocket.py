import logging
import re
import webbrowser

import requests

logger = logging.getLogger(__name__)


class Pocket(object):
    """
    Class to connect to the Pocket app, retrieve the user's article list,
    retrieve their original URLs
    in order for Epubify to convert the original URLs into epub files
    """

    def __init__(self, **kwargs):
        """
        The constructor receives a keyword argument list, which
        will be used to fetch information about the Pocket app,
        credential file path etc
        :param kwargs: keyword arguments
        """
        # self.cred_filename = getcwd() + '/vault/' + kwargs.get('credsFileName', "ani_keys.json")
        # Define epubify CONSTANTS
        self.config = kwargs
        self.EPUBIFY_KEY = "92033-7e774220ee6e0a96bc04ed2d"
        self.REDIRECT_URL = "http://worldofinspiration.net/epubify.html"
        self.user_name = ""
        self.access_code = None
        self.authenticated = self.authenticate()
        self.pocket_list = ""

    def fetch_pocket_articles(self):
        # http://getpocket.com/developer/docs/v3/retrieve

        url = "https://getpocket.com/v3/get"
        params = {
            "consumer_key": self.EPUBIFY_KEY,
            "access_token": self.access_code,
            "sort": "newest",
            "contentType": "article",
            "detailType": "simple",
        }
        response = self.__post_req(base_url=url, params=params)
        self.pocket_list = response.json().get("list")
        print(">> Article list successfully retrieved from Pocket.")
        return self

    def get_article_list(self):
        article_urls = [str(self.pocket_list.get(item).get("given_url")) for item in self.pocket_list]
        article_titles = [str(self.pocket_list.get(item).get("resolved_title")) for item in self.pocket_list]
        articles = dict(zip(article_titles, article_urls))
        return articles

    def authenticate(self):
        self._step_one_access_code()
        self._step_two_user_authorization()
        self._step_three_authorize()
        return True

    # PRIVATE METHODS
    def __get_req(self, params, base_url):
        response = requests.get(base_url, data=params)

        # if response_code not in [200, 201, 202, 204]:
        if not response.headers.get("X-Error"):
            return response
        else:
            response.raise_for_status()

    def __post_req(self, params, base_url, headers=None):
        response = requests.post(base_url, data=params, headers=headers)
        if not response.headers.get("X-Error"):
            return response
        else:
            response.raise_for_status()

    def _step_one_access_code(self):
        print(">> Executing Pocket step 1 [Authentication].. ")
        url = "https://getpocket.com/v3/oauth/request"
        params = {"consumer_key": self.EPUBIFY_KEY, "redirect_uri": self.REDIRECT_URL}

        access_code = self.__post_req(base_url=url, params=params).text.split("=")[1]

        print(">> Step 1 [Authentication]: Access code received successfully. ")
        self.access_code = access_code

    def _step_two_user_authorization(self):
        print(">> Executing Pocket step 2 [Authorization].. ")
        url = "https://getpocket.com/auth/authorize?request_token={code}&redirect_uri={redirect_uri}".format(
            redirect_uri=self.REDIRECT_URL,
            code=self.access_code,
        )
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

    def _step_three_authorize(self):
        print(">> Executing Pocket step 3 [Authorization].. ")
        params = {
            "consumer_key": self.EPUBIFY_KEY,
            "code": self.access_code,
        }
        url = "https://getpocket.com/v3/oauth/authorize"
        response = self.__post_req(base_url=url, params=params)
        self.access_code = re.findall("(?:access_token=)(.+)(?:&.+)", response.text)

        print(">> Step 3 [Authorization] complete.")
