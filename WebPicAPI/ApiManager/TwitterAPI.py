
from .Singleton import Singleton
from .template import *
import tweepy
import os, shutil
import json


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
