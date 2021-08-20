#! /bin/python3

# ##################################################################
# 
# A simple API manager/wrapper to setup & provide a easy interface
# for other APIs used in webpicapi.py
# 
# Author: Gavin1937
# GitHub: https://github.com/Gavin1937/WebPicAPI
# 
# ##################################################################


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
import os
import shutil
import ntpath
import json
import time
import random
import urllib.parse
import requests
from bs4 import BeautifulSoup
# api libs
from pixivpy3 import *
import tweepy
from pixiv_auth import refresh_returnDict


# public const
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Connection': 'keep-alive',
    'Refer': 'https://www.google.com'
}

# public functions

def getUrlSrc(url: str) -> str:
    """get url source as string"""
    
    if len(url) <= 0:
        return
    
    resp = requests.get(url=url, headers=HEADERS)
    resp.encoding = resp.apparent_encoding
    return resp.text

def getUrlJson(url: str) -> str:
    """get json data form url"""
    
    if len(url) <= 0:
        return
    
    resp = requests.get(url=url, headers=HEADERS)
    resp.encoding = resp.apparent_encoding
    return resp.json()

def downloadUrl(url, dest_filepath = os.path.curdir):
    """download url to dest_filepath"""
    
    # check url
    if len(url) <= 0:
        return
    
    # get dir & filename from dest_filepath
    dir, filename = ntpath.split(dest_filepath)
    
    # no filename, use filename from url
    if filename == None or len(filename) <= 0: 
        p = urllib.parse.urlparse(url)
        u_dir, u_filename = ntpath.split(p.path)
        filename = u_filename
    # has filename but no dir
    elif dir == None or len(dir) <= 0:
        return
    
    # has filename & dir, download file
    if dir[-1] != '/':
        dir += '/'
    resp = requests.get(url=url, headers=HEADERS)
    file = open(dir+filename, "wb")
    file.write(resp.content)
    file.close()

def randDelay(min: float, max: float) -> None:
    """generate random delay in seconds"""
    sec = round(random.uniform(min, max), 2)
    time.sleep(sec)

def isValidUrl(url: str) -> bool:
    if url is not None and len(url) > 0:
        return True
    else: return False


# API Classes

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



@Singleton
class EHentaiAPI:
    """Singleton class to request from e-hentai.org"""
    
    # private members
    __api_url: str = "https://api.e-hentai.org/api.php"
    __min_delay: float = 5.0
    __max_delay: float = 7.5
    
    # api features
    def searchKeyword(self, keyword: str, max_galleries: int) -> list:
        """Search specific gallery or tag with keyword in E-Hentai, return list of galleries"""
        if keyword is None or len(keyword) <= 0 or max_galleries <= 0:
            return None
        
        search_url = "https://e-hentai.org/?f_search=" + urllib.parse.quote(keyword)
        return self.getGalleriesFromSearch(search_url, max_galleries=max_galleries)
    
    def getGalleryInfo(self, url: str) -> dict:
        """Get basic Gallery Info via E-Hentai API, return json as dict."""
        if not self.isValidGallery(url):
            return None
        
        tmp_dict = self.__getGalleryIdentities(url)
        param = {
            "method": "gdata",
            "gidlist": [
                [tmp_dict["gallery_id"], tmp_dict["gallery_token"]]
            ],
            "namespace": 1
        }
        randDelay(self.__min_delay, self.__max_delay)
        resp = requests.post(url=self.__api_url, json=param, headers=HEADERS)
        return json.loads(resp.text)
    
    def findParentGallery(self, url: str) -> dict:
        """Find parent Gallery Identities (gallery_id & gallery_token) with a picture url."""
        if not self.isValidPicture(url):
            return None
        
        tmp_dict = self.__getPictureIdentities(url)
        param = {
            "method": "gtoken",
            "pagelist": [
                [tmp_dict["gallery_id"], tmp_dict["page_token"], tmp_dict["pagenumber"]]
            ]
        }
        randDelay(self.__min_delay, self.__max_delay)
        resp = requests.post(url=self.__api_url, json=param, headers=HEADERS)
        return json.loads(resp.text)
    
    def findParentGalleryUrl(self, url: str) -> str:
        """Find parent Gallery url with a Picture url."""
        if not self.isValidPicture(url):
            return None
        
        tmp_dict = self.findParentGallery(url)["tokenlist"][0]
        return f"https://e-hentai.org/g/{tmp_dict['gid']}/{tmp_dict['token']}/"
    
    def getPicUrl(self, url: str) -> str:
        """Get picture file url from a picture url. (https://e-hentai.org/s/{page_token}/{gallery_id}-{pagenumber}"""
        if not self.isValidPicture(url):
            return None
        
        soup = BeautifulSoup(self.__reqGet(url=url), 'lxml')
        return self.__picUrlFromHTML(soup=soup)
    
    def getPicsInGallery(self, url: str, max_pics: int) -> list:
        """Get url of pictures from a gallery url. (https://e-hentai.org/g/{gallery_id}/{gallery_token}/"""
        if not self.isValidGallery(url) or max_pics <= 0:
            return None
        
        # get gallery info via api
        j_dict = self.getGalleryInfo(url)
        
        # get total page of this gallery
        # assuming each page has 40 img (default setting)
        total_files = int(j_dict["gmetadata"][0]["filecount"])
        # add an extra page if "tmp" has decimal value
        tmp: float = float(total_files / 40.0)
        total_pages = int(tmp + 1) if ((tmp-int(tmp)) > 0) else int(tmp)
        pic_counter = 0
        output = []
        
        for i in range(total_pages):
            # get page src
            page_url = url + f"?p={i}"
            soup = BeautifulSoup(self.__reqGet(page_url), "lxml")
            divs = soup.find_all(class_ = "gdtm")
            
            # get img src
            for div in divs:
                loc_url = div.a.get("href")
                if loc_url != None:
                    output.append(loc_url)
                    pic_counter += 1
                    if pic_counter >= max_pics:
                        return output
        return output
    
    def getGalleriesFromSearch(self, url: str, max_galleries: int) -> list:
        """Get Galleries from an E-Hentai search url or any E-Hentai pages without /g/ or /s/ until reaches max_galleries."""
        if self.isValidGallery(url) or self.isValidPicture(url) or max_galleries <= 0:
            return None
        
        # setup vars
        output = []
        page_count = 0
        gallery_count = 0
        # extra pure url with search keyword
        parse = urllib.parse.urlparse(url)
        cur1 = parse.query.find("f_search=")
        cur2 = parse.query.find('&', cur1+9)
        if cur2 == -1: # no other query specified
            base_url = parse.scheme+"://" + parse.netloc + parse.path + '?'+parse.query[cur1:]
        else: # has other query, ignore them
            base_url = parse.scheme+"://" + parse.netloc + parse.path + '?'+parse.query[cur1:cur2]
        
        while gallery_count < max_galleries:
            # generate search url
            search_url = base_url + f"&page={page_count}"
            
            # make request
            src = self.__reqGet(search_url)
            
            # parse html
            soup = BeautifulSoup(src, 'lxml')
            
            # get all galleries in current page
            galleries = soup.find_all(class_="gl3c glname")
            
            for gallery in galleries:
                gallery_count += 1
                output.append(gallery.a.get("href"))
                if gallery_count >= max_galleries:
                    break
        return output
    
    
    # booleans
    def isValidEHentai(self, url: str) -> bool:
        """Is Url a valid e-hentai url"""
        if isValidUrl(url) and "e-hentai.org" in url:
            return True
        else: return False
    
    def isValidGallery(self, url: str) -> bool:
        """Is Url a valid Gallery?"""
        if self.isValidEHentai(url) and "/g/" in url:
            return True
        else: return False
    
    def isValidPicture(self, url: str) -> bool:
        """Is Url a valid Picture?"""
        if self.isValidEHentai(url) and "/s/" in url and url[-1] != '/':
            return True
        else: return False
    
    def isValidSearchPage(self, url: str) -> bool:
        """Is Url a valid e-hentai page w/ multiple galleries"""
        if (self.isValidEHentai(url) and
            not self.isValidGallery(url) and
            not self.isValidPicture(url)
            ):
            return True
        else: return False
    
    
    # getters
    def getAPIUrl(self) -> str:
        return self.__api_url
    
    def getMinDelay(self) -> float:
        return self.__min_delay
    
    def getMaxDelay(self) -> float:
        return self.__max_delay
    
    
    # setters
    def setMinDelay(self, delay: float) -> None:
        """Set self.__min_delay for request"""
        self.__min_delay = round(float(delay), 2)
    
    def setMaxDelay(self, delay: float) -> None:
        """Set self.__max_delay for request"""
        self.__max_delay = round(float(delay), 2)
    
    
    # helper functions
    def __reqGet(self, url: str) -> str:
        """Private HTTP request GET method, contains auto delay"""
        if not isValidUrl(url):
            return None
        
        randDelay(self.__min_delay, self.__max_delay)
        return getUrlSrc(url)
    
    def __picUrlFromHTML(self, soup: BeautifulSoup) -> str:
        """Get url of a single picture from a picture url, input BeautifulSoup of a image page"""
        img = soup.find_all(id="img")
        return img[0]["src"]
    
    def __getGalleryIdentities(self, url: str) -> dict:
        """Get Identities of a Gallery url. (gallery_id & gallery_token), return dict of them."""
        if not self.isValidGallery(url):
            return None
        
        # get identities
        dirs = urllib.parse.urlparse(url).path.split('/')
        gallery_id = int(dirs[-3])
        gallery_token = dirs[-2]
        
        return {"gallery_id": gallery_id, "gallery_token": gallery_token}
    
    def __getPictureIdentities(self, url: str) -> dict:
        """Get Identities of a Picture url. (page_token, gallery_id, & pagenumber), return dict of them."""
        if not self.isValidPicture(url):
            return None
        
        # get identities
        dirs = urllib.parse.urlparse(url).path.split('/')
        last_part = dirs[-1].split('-')
        page_token = dirs[-2]
        gallery_id = int(last_part[0])
        pagenumber = int(last_part[1])
        
        return {"page_token": page_token, "gallery_id": gallery_id, "pagenumber": pagenumber}
    


