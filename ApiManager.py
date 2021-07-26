#! /bin/python3

# source: https://stackoverflow.com/questions/31875/is-there-a-simple-elegant-way-to-define-singletons
class Singleton:
    """
    A non-thread-safe helper class to ease implementing singletons.
    This should be used as a decorator -- not a metaclass -- to the
    class that should be a singleton.
    
    The decorated class can define one `__init__` function that
    takes only the `self` argument. Also, the decorated class cannot be
    inherited from. Other than that, there are no restrictions that apply
    to the decorated class.
    
    To get the singleton instance, use the `instance` method. Trying
    to use `__call__` will result in a `TypeError` being raised.
    
    """
    
    def __init__(self, decorated):
        self._decorated = decorated
    
    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance
    
    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')
    
    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)


# apitoken.json file template
apitoken_template = """
{
    \"pixiv_token\": {
        \"code\": "",
        \"access_token\": "",
        \"refresh_token\": "",
        \"expires_in\": 0
    },
    \"twitter_token\": {
        \"api_key\": \"\",
        \"api_secret_key\": \"\",
        \"bearer_token\": \"\",
        \"access_token\": \"\",
        \"access_token_secret\": \"\"
    }
}
"""


# libs
from collections import UserDict
import os
import json
# api libs
from pixivpy3 import *
import tweepy


@Singleton
class PixivAPI:
    """Singleton class to create & manage pixivpy3 api instance and auth"""
    
    # private members
    __api: AppPixivAPI = None
    __auto_refresh_flag: bool = False
    
    # constructor
    def __init__(self):
        apitoken_dict = {}
        # check whether apitoken.json exist
        if not os.path.isfile("./apitoken.json"): # file does not exist, create a new one
            file = open("./apitoken.json", 'w')
            file.write(apitoken_template)
            file.close()
        # file exist
        file = open("./apitoken.json", 'r')
        apitoken_dict = json.load(file)
        file.close()
        
        # checking apitoken.json
        while not self.__has_valid_pixiv_token(apitoken_dict): # prompt user to fill in tokens
            input("Please fill in all values under \"pixiv_token\" in \"apitoken.json\" under current directory.\nPress any key to refresh.\n\n")
            file = open("./apitoken.json", 'r')
            apitoken_dict = json.load(file)
            file.close()
        
        # authorize api
        self.__api = AppPixivAPI()
        try:
            self.__api.auth(refresh_token=apitoken_dict["pixiv_token"]["refresh_token"])
        except Exception as err:
            self.__api = None
            raise err
        
        self.__autoRefreshing_token()
    
    def setAutoRefreshToken(self, flag):
        """Whether Enable or Disable auto refreshing pixiv api token"""
        self.__auto_refresh_flag = flag
    
    # api features
    def getIllustDetail(self, pid: int) -> dict:
        return self.__api.illust_detail(pid)
    
    def getUserDetail(self, pid: int) -> dict:
        return self.__api.user_detail(pid)
    
    def getUserIllustList(self, pid: int, count: int) -> dict:
        output: list = []
        counter = 0
        cur_page = self.__api.user_illusts(pid)
        next_url = ""
        while "next_url" in cur_page:
            for item in cur_page["illusts"]:
                output.append(item)
                counter += 1
                if counter == count:
                    return output
            # reaches end of page
            if cur_page["next_url"] == None:
                return output
            # move to next page
            next = self.__api.parse_qs(cur_page["next_url"])
            cur_page = self.__api.user_illusts(user_id=pid, offset=next["offset"])
        return output
    
    def searchIllust(
            self, word,
            search_target='partial_match_for_tags',
            sort='date_desc', duration=None,
            start_date=None, end_date=None,
            filter='for_ios', offset=None):
        return self.__api.search_illust(
                word, search_target=search_target,
                sort=sort, duration=duration,
                start_date=start_date, end_date=end_date,
                filter=filter, offset=offset)
    
    def searchUser(
            self, word,
            sort='date_desc',
            duration=None,
            filter='for_ios',
            offset=None):
        return self.__api.search_user(
                word, sort=sort,
                duration=duration,
                filter=filter, offset=offset)
    
    def downloadIllust(self, url: str, path: str=os.path.curdir, name: str=None) -> bool:
        return self.__api.download(url=url, path=path, name=name)
    
    def followUser(self, pid: int):
        self.__api.user_follow_add(user_id=pid)
    
    def unfollowUser(self, pid: int):
        self.__api.user_follow_delete(user_id=pid)
    
    def api(self) -> AppPixivAPI:
        return self.__api
    
    # helper functions
    def __has_valid_pixiv_token(self, apitoken_dict: dict) -> bool:
        return (
            len(apitoken_dict["pixiv_token"]["code"]) > 0 and
            len(apitoken_dict["pixiv_token"]["access_token"]) > 0 and
            len(apitoken_dict["pixiv_token"]["refresh_token"]) > 0 and
            apitoken_dict["pixiv_token"]["expires_in"] > 0 
        )
    
    def __autoRefreshing_token(self):
        pass



@Singleton
class TwitterAPI:
    """Singleton class to create & manage tweepy api instance and auth"""
    
    # private members
    __api: tweepy.API = None
    __auto_refresh_flag: bool = False
    
    # constructor
    def __init__(self):
        apitoken_dict = {}
        # check whether apitoken.json exist
        if not os.path.isfile("./apitoken.json"): # file does not exist, create a new one
            file = open("./apitoken.json", 'w')
            file.write(apitoken_template)
            file.close()
        # file exist
        file = open("./apitoken.json", 'r')
        apitoken_dict = json.load(file)
        file.close()
        
        # checking apitoken.json
        while not self.__has_valid_twitter_token(apitoken_dict): # prompt user to fill in tokens
            input("Please fill in all values under \"twitter_token\" in \"apitoken.json\" under current directory.\nPress any key to refresh.\n\n")
            file = open("./apitoken.json", 'r')
            apitoken_dict = json.load(file)
            file.close()
        
        # authorize api
        try:
            auth = tweepy.OAuthHandler(
                consumer_key=apitoken_dict["twitter_token"]["api_key"],
                consumer_secret=apitoken_dict["twitter_token"]["api_secret_key"]
            )
            auth.set_access_token(
                apitoken_dict["twitter_token"]["access_token"],
                apitoken_dict["twitter_token"]["access_token_secret"]
            )
            self.__api: tweepy.API = tweepy.API(auth)
        except Exception as err:
            self.__api = None
            raise err
        
        self.__autoRefreshing_token()
    
    def setAutoRefreshToken(self, flag):
        """Whether Enable or Disable auto refreshing pixiv api token"""
        self.__auto_refresh_flag = flag
    
    # api features
    def getStatusJson(self, status_id: str) -> dict:
        try:
            return self.__api.get_status(status_id, tweet_mode="extended")._json
        except Exception as err:
            raise err
    
    def getUserJson(self, user_id: int = None, screen_name: str = None) -> dict:
        try:
            if user_id != None:
                return self.__api.get_user(user_id=user_id)._json
            elif screen_name !=None:
                return self.__api.get_user(screen_name=screen_name)._json
        except Exception as err:
            raise err
    
    def getUserTimeline(
            self, user_id: int = None,
            screen_name: str = None,
            count: int = None
        ) -> list:
        
        output = []
        counter = 0
        for item in tweepy.Cursor(
                    self.__api.user_timeline,
                    user_id=user_id,
                    screen_name=screen_name,
                    tweet_mode="extended", count=1).items():
            if counter >= count:
                break
            counter += 1
            output.append(item._json)
        
        return output
    
    # def getUserIllustList_nextPage(self, next_url: str) -> dict:
    #     next = self.__api.parse_qs(next_url)
    #     return self.__api.user_illusts(user_id=next["user_id"], offset=next["offset"])
    
    # def searchStatus(self, screen_name: str = None, status_id: str = None):
    #     j_res = self.__api.user_timeline(screen_name=screen_name, )
    
    # def searchUser(
    #         self, word,
    #         sort='date_desc',
    #         duration=None,
    #         filter='for_ios',
    #         offset=None):
    #     return self.__api.search_user(
    #             word, sort=sort,
    #             duration=duration,
    #             filter=filter, offset=offset)
    
    # def downloadIllust(self, url: str, path: str=os.path.curdir, name: str=None) -> bool:
    #     return self.__api.download(url=url, path=path, name=name)
    
    # def followUser(self, pid: int):
    #     self.__api.user_follow_add(user_id=pid)
    
    # def unfollowUser(self, pid: int):
    #     self.__api.user_follow_delete(user_id=pid)
    
    def api(self) -> AppPixivAPI:
        return self.__api
    
    # helper functions
    def __has_valid_twitter_token(self, apitoken_dict: dict) -> bool:
        return (
            len(apitoken_dict["twitter_token"]["api_key"]) > 0 and
            len(apitoken_dict["twitter_token"]["api_secret_key"]) > 0 and
            len(apitoken_dict["twitter_token"]["bearer_token"]) > 0 and
            len(apitoken_dict["twitter_token"]["access_token"]) > 0 and
            len(apitoken_dict["twitter_token"]["access_token_secret"]) > 0 
        )
    
    def __autoRefreshing_token(self):
        pass


