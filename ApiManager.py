

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
        
    }
}
"""


# libs
import os
import json
from webpicapi import PixivPic
# api libs
from pixivpy3 import *


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
    
    def getUserIllustList(self, pid: int) -> dict:
        return self.__api.user_illusts(pid)
    
    def downloadIllust(self, url: str, path: str=os.path.curdir, name: str=None) -> bool:
        return self.__api.download(url=url, path=path, name=name)
    
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





