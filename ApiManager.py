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
        \"consumer_api_key\": \"\",
        \"consumer_secret\": \"\",
        \"bearer_token\": \"\",
        \"access_token\": \"\",
        \"access_token_secret\": \"\"
    }
}
"""


# libs
from collections import UserDict
import os
import shutil
import json
# api libs
from pixivpy3 import *
import tweepy
from pixiv_auth import refresh_returnDict


@Singleton
class PixivAPI:
    """Singleton class to create & manage pixivpy3 api instance and auth"""
    
    # private members
    __api: AppPixivAPI = None
    __auto_refresh_flag: bool = False
    __apitoken_life: int = None
    __last_update_life: int = None
    
    # constructor
    def __init__(self, enable_autoRefreshToken: bool = True):
        apitoken_dict = {}
        # check whether apitoken.json exist
        if not os.path.isfile("./apitoken.json"): # file does not exist, create a new one
            if not os.path.isfile("./apitoken.json.bak"): # no backup file
                file = open("./apitoken.json", 'w')
                file.write(apitoken_template)
                file.close()
            else: # has backup file
                shutil.copyfile("./apitoken.json.bak", "./apitoken.json")
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
        
        # backup apitoken.json
        file = open("./apitoken.json.bak", 'w')
        json.dump(apitoken_dict, file)
        file.close()
        
        # authorize api
        self.__api = AppPixivAPI()
        try:
            self.__api.auth(refresh_token=apitoken_dict["pixiv_token"]["refresh_token"])
        except Exception as err:
            self.__api = None
            raise err
        
        # get current apitoken life time
        self.__apitoken_life = apitoken_dict["pixiv_token"]["expires_in"]
        self.__last_update_life = self.__apitoken_life
        
        # setting __auto_refresh_flag
        self.setAutoRefreshToken(enable_autoRefreshToken)
    
    def refreshApiToken(self):
        # load apitoken from file
        file = open("./apitoken.json", 'r')
        apitoken_dict = json.load(file)
        file.close()
        # refresh token
        res = refresh_returnDict(apitoken_dict["pixiv_token"]["refresh_token"])
        # update token
        apitoken_dict["pixiv_token"]["access_token"] = res["access_token"]
        apitoken_dict["pixiv_token"]["refresh_token"] = res["refresh_token"]
        apitoken_dict["pixiv_token"]["expires_in"] = res["expires_in"]
        # write to apitoken.json
        file = open("./apitoken.json", 'w')
        json.dump(apitoken_dict, file)
        file.close()
        # backup apitoken.json
        file = open("./apitoken.json.bak", 'w')
        json.dump(apitoken_dict, file)
        file.close()
    
    def updateApiTokenLifetime(self, new_lifetime: int):
        if self.__auto_refresh_flag and new_lifetime <= 100: # refresh apitoken as needed
            self.refreshApiToken()
            self.__last_update_life = self.__apitoken_life
        else: # healthy token, update lifetime
            # modify lifetime
            self.__apitoken_life = new_lifetime
            if abs(self.__apitoken_life - self.__last_update_life) > 30: # minimize file writing
                # load apitoken from file
                file = open("./apitoken.json", 'r')
                apitoken_dict = json.load(file)
                file.close()
                # update token
                apitoken_dict["pixiv_token"]["expires_in"] = self.__apitoken_life
                # write to file
                file = open("./apitoken.json", 'w')
                json.dump(apitoken_dict, file)
                file.close()
                # update last_update_life
                self.__last_update_life = self.__apitoken_life
    
    def setAutoRefreshToken(self, flag):
        """Whether Enable or Disable auto refreshing pixiv api token"""
        self.__auto_refresh_flag = flag
    
    def getApiTokenLifetime(self) -> int:
        return self.__apitoken_life
    
    # api features
    def getIllustDetail(self, pid: int) -> dict:
        self.updateApiTokenLifetime(self.__apitoken_life-1)
        return self.__api.illust_detail(pid)
    
    def getUserDetail(self, pid: int) -> dict:
        self.updateApiTokenLifetime(self.__apitoken_life-1)
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
        # update apitoken lifetime
        self.updateApiTokenLifetime(self.__apitoken_life-len(output))
        return output
    
    def searchIllust(
            self, word,
            search_target='partial_match_for_tags',
            sort='date_desc', duration=None,
            start_date=None, end_date=None,
            filter='for_ios', offset=None):
        output = self.__api.search_illust(
                word, search_target=search_target,
                sort=sort, duration=duration,
                start_date=start_date, end_date=end_date,
                filter=filter, offset=offset)
        # update apitoken lifetime
        self.updateApiTokenLifetime(self.__apitoken_life-len(output))
        return output
    
    def searchUser(
            self, word,
            sort='date_desc',
            duration=None,
            filter='for_ios',
            offset=None):
        output = self.__api.search_user(
                word, sort=sort,
                duration=duration,
                filter=filter, offset=offset)
        # update apitoken lifetime
        self.updateApiTokenLifetime(self.__apitoken_life-len(output))
        return output
    
    def downloadIllust(self, url: str, path: str=os.path.curdir, name: str=None) -> bool:
        self.updateApiTokenLifetime(self.__apitoken_life-1)
        return self.__api.download(url=url, path=path, name=name)
    
    def followUser(self, pid: int):
        self.updateApiTokenLifetime(self.__apitoken_life-1)
        self.__api.user_follow_add(user_id=pid)
    
    def unfollowUser(self, pid: int):
        self.updateApiTokenLifetime(self.__apitoken_life-1)
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
    



@Singleton
class TwitterAPI:
    """Singleton class to create & manage tweepy api instance and auth"""
    
    # private members
    __api: tweepy.API = None
    
    # constructor
    def __init__(self):
        apitoken_dict = {}
        # check whether apitoken.json exist
        if not os.path.isfile("./apitoken.json"): # file does not exist, create a new one
            if not os.path.isfile("./apitoken.json.bak"): # no backup file
                file = open("./apitoken.json", 'w')
                file.write(apitoken_template)
                file.close()
            else: # has backup file
                shutil.copyfile("./apitoken.json.bak", "./apitoken.json")
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
        
        # backup apitoken.json
        file = open("./apitoken.json.bak", 'w')
        json.dump(apitoken_dict, file)
        file.close()
        
        # authorize api
        try:
            auth = tweepy.OAuthHandler(
                consumer_key=apitoken_dict["twitter_token"]["consumer_api_key"],
                consumer_secret=apitoken_dict["twitter_token"]["consumer_secret"]
            )
            auth.set_access_token(
                apitoken_dict["twitter_token"]["access_token"],
                apitoken_dict["twitter_token"]["access_token_secret"]
            )
            self.__api: tweepy.API = tweepy.API(auth)
        except Exception as err:
            self.__api = None
            raise err
    
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
    
    def searchTweets(self, keyword: str, max_count: int = 10):
        output = []
        for item in tweepy.Cursor(self.__api.search, q=keyword, tweet_mode="extended").items(max_count):
            if item._json not in output:
                output.append(item._json)
            break
        return output
    
    def searchUsers(self, keyword: str, max_count: int = 10):
        output = []
        for item in tweepy.Cursor(self.__api.search_users, q=keyword).items(max_count):
            if item._json not in output:
                output.append(item._json)
            break
        return output
    
    def followUser(self, screen_name: str):
        try:
            self.__api.create_friendship(screen_name=screen_name)
        except Exception as err:
            raise err
    
    def unfollowUser(self, screen_name: str):
        try:
            self.__api.destroy_friendship(screen_name=screen_name)
        except Exception as err:
            raise err
    
    def api(self) -> tweepy.API:
        return self.__api
    
    # helper functions
    def __has_valid_twitter_token(self, apitoken_dict: dict) -> bool:
        return (
            len(apitoken_dict["twitter_token"]["consumer_api_key"]) > 0 and
            len(apitoken_dict["twitter_token"]["consumer_secret"]) > 0 and
            len(apitoken_dict["twitter_token"]["bearer_token"]) > 0 and
            len(apitoken_dict["twitter_token"]["access_token"]) > 0 and
            len(apitoken_dict["twitter_token"]["access_token_secret"]) > 0 
        )


