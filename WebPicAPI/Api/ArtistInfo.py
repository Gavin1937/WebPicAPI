
from ..ApiManager import *
from ..Util import *
from ..Util.httpUtilities import randDelay, getSrcStr, getSrcJson
from .types import WebPicType
import urllib.parse
import ntpath
import requests
import json


class ArtistInfo:
    """Process & Hold Artist Information"""
    
    # private variables
    __artist_names: list = []
    __pixiv_urls: list = []
    __twitter_urls: list = []
    
    # constructor
    def __init__(self, webpic_type: WebPicType, url: str):
        if webpic_type == WebPicType.PIXIV:
            self.__analyzeInfo_pixiv(url)
        elif webpic_type == WebPicType.TWITTER:
            self.__analyzeInfo_twitter(url)
        elif webpic_type == WebPicType.DANBOORU:
            self.__analyzeInfo_danbooru(url)
        elif webpic_type == WebPicType.YANDERE:
            self.__analyzeInfo_yandere(url)
        elif webpic_type == WebPicType.KONACHAN:
            self.__analyzeInfo_konachan(url)
        elif webpic_type == WebPicType.WEIBO:
            self.__analyzeInfo_weibo(url)
        elif webpic_type == WebPicType.EHENTAI:
            self.__analyzeInfo_ehentai(url)
        else: # Unknown
            return None
    
    # clear obj
    def clear(self) -> None:
        self.__artist_names.clear()
        self.__pixiv_urls.clear()
        self.__twitter_urls.clear()
    
    # getters
    def getArtistNames(self) -> list:
        return self.__artist_names
        
    def getUrl_pixiv(self) -> list:
        return self.__pixiv_urls
    
    def getUrl_twitter(self) -> list:
        return self.__twitter_urls
    
    # helper functions
    def __analyzeInfo_pixiv(self, url: str):
        # get uid from url
        uid = url[url.rfind('/')+1:]
        
        # setup api instance
        api: PixivAPI = PixivAPI.instance()
        
        # get user_res as python dict
        user_res = api.getUserDetail(uid)
        
        # set artist name
        self.__artist_names.append(user_res["user"]["name"])
        
        # set artist pixiv url
        self.__pixiv_urls.append("https://pixiv.net/users/"+str(user_res["user"]["id"]))
        
        # set artist twitter url (if has one)
        possible_url = user_res["profile"]["twitter_url"]
        # user has twitter url in profile section
        if possible_url != None and len(possible_url) > 0:
            self.__twitter_urls.append(possible_url)
        else: # try to find twitter url from comment
            possible_url = str(user_res["user"]["comment"])
            cur = possible_url.find("twitter.com/")
            if cur != -1:
                cur += 12
                cur2 = cur
                while (
                    possible_url[cur2].isalpha() or
                    possible_url[cur2].isnumeric() or
                    possible_url[cur2] == '_'
                    ): 
                    cur2 += 1
                    if cur2 >= len(possible_url):
                        break
                
                if cur2 <= len(possible_url):
                    self.__twitter_urls.append("https://twitter.com/" + possible_url[cur:cur2])
    
    def __analyzeInfo_twitter(self, url: str):
        # get screen_name from url
        parse1 = urllib.parse.urlparse(url)
        parse2 = ntpath.split(parse1.path)
        screen_name = parse2[1]
        
        # setup api instance
        api: TwitterAPI = TwitterAPI.instance()
        
        # get user_res as python dict
        user_res = api.getUserJson(screen_name=screen_name)
        
        # set artist name
        self.__artist_names.append(user_res["name"])
        self.__artist_names.append(user_res["screen_name"])
        
        # set artist pixiv url (if has one)
        # get all urls existing urls
        urls_founded: list = []
        if "url" in user_res["entities"]:
            for item in user_res["entities"]["url"]["urls"]:
                urls_founded.append(item["expanded_url"])
        if "description" in user_res["entities"]:
            for item in user_res["entities"]["description"]["urls"]:
                urls_founded.append(item["expanded_url"])
        # get urls from description
        description_str: str = user_res["description"]
        cur = 0
        while cur != -1:
            cur = description_str.find("https://", cur)
            if cur == -1:
                break
            cur += 8
            old_cur = cur
            while description_str[cur] != ' ' or description_str[cur] != '\n':
                cur += 1
                if cur >= len(description_str):
                    break
            urls_founded.append("https://"+description_str[old_cur:cur])
        # remove duplicates
        urls_founded = rmListDuplication(urls_founded)
        # get final urls after redirection
        final_urls: list = []
        for loc_url in urls_founded:
            try:
                req = requests.get(loc_url)
                final_urls.append(req.url)
            except Exception as err:
                pass
        final_urls = rmListDuplication(final_urls)
        # search through all urls and finding pixiv id
        for loc_url in final_urls:
            if "pixiv.net/users/" in loc_url:
                self.__pixiv_urls.append(loc_url)
            elif ".fanbox.cc" in loc_url:
                randDelay(1.0, 2.5)
                src = getSrcStr(loc_url)
                cur = src.find("fanbox/public/images/creator/")
                if cur == -1:
                    break
                cur += 29
                self.__pixiv_urls.append("https://pixiv.net/users/"+src[cur:src.find("/cover", cur)])
        
        # set artist twitter url
        self.__twitter_urls.append(url)
    
    def __analyzeInfo_danbooru(self, url: str):
        cur = 0
        
        # get url source
        randDelay(1.0, 2.5)
        src = getSrcStr(url)
        
        # finding artist names
        cur = src.find("Other Names")
        if cur != -1:
            names_src = src[cur:src.find("/li", cur)]
            cur = 0
            while cur != -1:
                cur = names_src.find("artist-other-name", cur)
                if cur == -1:
                    break
                cur = names_src.find("any_name_matches%5D=", cur) + 20
                tmp_str = names_src[cur:names_src.find('\"', cur)]
                self.__artist_names.append(urllib.parse.unquote(tmp_str))
                cur += 3
        else:
            cur = src.find("og:title\" content=\"") + 19
            self.__artist_names.append(src[cur:src.find(" | Artist Profile", cur)])
        
        # finding pixiv & twitter url
        tmp_url = ""
        had_pixiv = False
        had_twitter = False
        cur = src.find("list-bulleted")
        url_src = src[cur:src.find("/ul", cur)]
        cur = 0
        while cur != -1:
            cur = url_src.find("href=\"", cur)
            if cur == -1:
                break
            cur += 6
            tmp_url = url_src[cur:url_src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
    
    def __analyzeInfo_yandere(self, url: str):
        # get 1st name from url
        tmp_name = url[url.find("title=")+6:]
        self.__artist_names.append(urllib.parse.unquote(tmp_name))
        
        # get wiki page source
        randDelay(1.0, 2.5)
        src = getSrcStr(url)
        
        # get urls
        cur = 0
        tmp_url = ""
        while cur != -1:
            cur = src.find("<th>URL</th>", cur)
            if cur == -1:
                break
            cur = src.find("href=\"", cur) + 6
            tmp_url = src[cur:src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
                
        # get artist names
        cur = src.find("<th>Aliases</th>")
        tmp_str = src[cur:src.find("</tr>", cur)]
        cur = 0
        while cur != -1:
            cur = tmp_str.find("/wiki/show?title=", cur)
            if cur == -1:
                break
            cur += 17
            self.__artist_names.append(
                urllib.parse.unquote(tmp_str[cur:tmp_str.find('\"', cur)])
            )
    
    def __analyzeInfo_konachan(self, url: str):
        # get 1st name from url
        tmp_name = url[url.find("title=")+6:]
        self.__artist_names.append(urllib.parse.unquote(tmp_name))
        
        # get wiki page source
        randDelay(1.0, 2.5)
        src = getSrcStr(url)
        
        # get urls
        cur = 0
        tmp_url = ""
        while cur != -1:
            cur = src.find("<th>URL</th>", cur)
            if cur == -1:
                break
            cur = src.find("href=\"", cur) + 6
            tmp_url = src[cur:src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
                
        # get artist names
        cur = src.find("<th>Aliases</th>")
        tmp_str = src[cur:src.find("</tr>", cur)]
        cur = 0
        while cur != -1:
            cur = tmp_str.find("/wiki/show?title=", cur)
            if cur == -1:
                break
            cur += 17
            self.__artist_names.append(
                urllib.parse.unquote(tmp_str[cur:tmp_str.find('\"', cur)])
            )
    
    def __analyzeInfo_weibo(self, url: str):
        # get user_id from url
        parse1 = urllib.parse.urlparse(url)
        parse2 = ntpath.split(parse1.path)
        user_id = int(parse2[1])
        
        # get j_dict
        j_dict = {}
        try:
            randDelay(2.5, 5.0)
            j_dict = getSrcJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&value={user_id}&containerid=100505{user_id}")
            if j_dict["ok"] != 1:
                raise ValueError("Unable to fetch json data from weibo")
        except Exception as err:
            raise err
        
        # finding urls
        desc_str = j_dict["data"]["userInfo"]["description"]
        if "pixiv.net" in desc_str:
            cur1 = desc_str.find("pixiv.net")
            cur2 = cur1 + 9
            while (
                desc_str[cur2].isalnum() or
                desc_str[cur2] == '.' or
                desc_str[cur2] == '?' or
                desc_str[cur2] == '/'):
                cur2 += 1
            self.__pixiv_urls.append("https://www." + desc_str[cur1:cur2])
        elif "twitter.com" in desc_str:
            cur1 = desc_str.find("twitter.com")
            cur2 = cur1 + 9
            while (
                desc_str[cur2].isalnum() or
                desc_str[cur2] == '.' or
                desc_str[cur2] == '?' or
                desc_str[cur2] == '/'):
                cur2 += 1
            self.__twitter_urls.append("https://www." + desc_str[cur1:cur2])
        
        # get artist names
        self.__artist_names.append(j_dict["data"]["userInfo"]["screen_name"])
        
    def __analyzeInfo_ehentai(self, json_str: str):
        """Takes a list of artists names in json string"""
        self.__artist_names = json.loads(json_str)
        # assume e-hentai does not have pixiv & twitter url
    