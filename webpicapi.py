#! /bin/python3

# ##################################################################
# 
# A simple API to fetch basic info and download pictures from
# popular picture/wallpaper websites.
# 
# Author: Gavin1937
# GitHub: https://github.com/Gavin1937/WebPicAPI
# 
# ##################################################################


# libs
import os
import ntpath
import urllib.parse
import requests
import json
from enum import IntEnum
from ApiManager import *


# public functions

def findFirstNonNum(s: str, start_idx: int = 0) -> int:
    """Find the first non numberic character of input string from start_idx, return index"""
    while start_idx < len(s):
        if not s[start_idx].isnumeric():
            return start_idx
        start_idx += 1
    return start_idx

def space2lowline(s: str) -> str:
    """Convert all spaces \' \' in input string to lowline \'_\' and return as a new string"""
    l = str(s).split(' ')
    output = ""
    for i in l:
        output += i + '_'
    return output[:-1]

def rmListDuplication(l: list) -> list:
    output = []
    for item in l:
        if item not in output:
            output.append(item)
    return output

def isEmptyWebPic(webpic: any) -> bool:
    return (
        len(webpic.getFileUrl()) == 0 and
        len(webpic.getFileName()) == 0 and
        webpic.getSrcUrl() == 0 and
        webpic.hasArtist() == False and
        len(webpic.getTags()) == 0
    )

# WebPicType const Table
# Bit Table:
# 0b     1         1       1       1         1         1         1       1
#     Unknown  e-hentai  weibo  konachan  yande.re  danbooru  twitter  pixiv
class WebPicType(IntEnum):
    """Type of different picture/wallpaper websites"""
    PIXIV    = 1,   # 0b00000001
    TWITTER  = 2,   # 0b00000010
    DANBOORU = 4,   # 0b00000100
    YANDERE  = 8,   # 0b00001000
    KONACHAN = 16,  # 0b00010000
    WEIBO    = 32,  # 0b00100000
    EHENTAI  = 64,  # 0b01000000
    UNKNOWN  = 128  # 0b10000000

class ParentChild(IntEnum):
    """Whether a web page is parent, child, or unknown"""
    UNKNOWN = 0,
    PARENT = 1,
    CHILD = 2

def WebPicType2Str(webpic_type: WebPicType) -> str:
    """Convert WebPicType to String"""
    if webpic_type == WebPicType.PIXIV:
        return "pixiv"
    elif webpic_type == WebPicType.TWITTER:
        return "twitter"
    elif webpic_type == WebPicType.DANBOORU:
        return "danbooru"
    elif webpic_type == WebPicType.YANDERE:
        return "yandere"
    elif webpic_type == WebPicType.KONACHAN:
        return "konachan"
    elif webpic_type == WebPicType.WEIBO:
        return "weibo"
    elif webpic_type == WebPicType.EHENTAI:
        return "ehentai"
    else: # Unknown
        return None

def Str2WebPicType(webpic_type_str: str) -> WebPicType:
    """Convert String to WebPicType"""
    if webpic_type_str == "pixiv":
        return WebPicType.PIXIV
    elif webpic_type_str == "twitter":
        return WebPicType.TWITTER
    elif webpic_type_str == "danbooru":
        return WebPicType.DANBOORU
    elif webpic_type_str == "yandere":
        return WebPicType.YANDERE
    elif webpic_type_str == "konachan":
        return WebPicType.KONACHAN
    elif webpic_type_str == "weibo":
        return WebPicType.WEIBO
    elif webpic_type_str == "ehentai":
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicType2DomainStr(webpic_type: WebPicType) -> str:
    """Convert DomainStr to WebPicType"""
    if webpic_type == WebPicType.PIXIV:
        return "www.pixiv.net"
    elif webpic_type == WebPicType.TWITTER:
        return "www.twitter.com"
    elif webpic_type == WebPicType.DANBOORU:
        return "danbooru.donmai.us"
    elif webpic_type == WebPicType.YANDERE:
        return "yande.re"
    elif webpic_type == WebPicType.KONACHAN:
        return "konachan.com"
    elif webpic_type == WebPicType.WEIBO:
        # we mainly support "m.weibo.cn"
        return "m.weibo.cn"
    elif webpic_type == WebPicType.EHENTAI:
        return "e-hentai.org"
    else: # Unknown
        return None

def DomainStr2WebPicType(domain_str: str) -> WebPicType:
    """Convert DomainStr to WebPicType"""
    if "www.pixiv.net" in domain_str or "pximg.net" in domain_str:
        return WebPicType.PIXIV
    elif "twitter.com" in domain_str or "twimg.com" in domain_str:
        return WebPicType.TWITTER
    elif "danbooru.donmai.us" in domain_str:
        return WebPicType.DANBOORU
    elif "yande.re" in domain_str:
        return WebPicType.YANDERE
    elif "konachan.com" in domain_str:
        return WebPicType.KONACHAN
    elif "www.weibo.com" in domain_str or "weibo.com" in domain_str or "m.weibo.cn" in domain_str:
        return WebPicType.WEIBO
    elif "e-hentai.org" in domain_str:
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicTypeMatch(src_type: WebPicType, dest_type: WebPicType) -> bool:
    """Check wether src_type is same as dest_type"""
    # handle String dest_type
    loc_dest_type = WebPicType.UNKNOWN
    if type(dest_type) == str:
        loc_dest_type = Str2WebPicType(dest_type)
    else: # dest_type is WebPicType
        loc_dest_type = dest_type
    return bool(src_type == loc_dest_type)


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
                src = getUrlSrc(loc_url)
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
        src = getUrlSrc(url)
        
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
        src = getUrlSrc(url)
        
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
        src = getUrlSrc(url)
        
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
            j_dict = getUrlJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&value={user_id}&containerid=100505{user_id}")
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
    


class WebPic:
    """Online Picture/Wallpaper website template class"""
    
    # private variables
    __url: str = ""
    __webpic_type: WebPicType = WebPicType.UNKNOWN
    
    # constructor
    def __init__(self, url: str):
        self.__url = url
        # identify __webpic_type
        p = urllib.parse.urlparse(self.getUrl())
        netloc = p.netloc
        if "pixiv.net" in p.netloc:
            self.__webpic_type = WebPicType.PIXIV
        elif "twitter.com" in p.netloc or "twimg.com" in p.netloc:
            self.__webpic_type = WebPicType.TWITTER
        elif "danbooru.donmai.us" in p.netloc:
            self.__webpic_type = WebPicType.DANBOORU
        elif "yande.re" in p.netloc:
            self.__webpic_type = WebPicType.YANDERE
        elif "konachan.com" in p.netloc:
            self.__webpic_type = WebPicType.KONACHAN
        elif "weibo.c" in p.netloc:
            self.__webpic_type = WebPicType.WEIBO
        elif "e-hentai.org" in p.netloc:
            self.__webpic_type = WebPicType.EHENTAI
        else: # Unknown
            self.__webpic_type = WebPicType.UNKNOWN
    
    # clear obj
    def clear(self) -> None:
        self.__url = 0
        self.__webpic_type = WebPicType.UNKNOWN
    
    # public methods
    def getUrl(self) -> str:
        return self.__url
    
    def getWebPicType(self) -> WebPicType:
        return self.__webpic_type


class PixivPic(WebPic):
    """handle artist identifications & downloading for pixiv"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # api handles
    __api: PixivAPI = None
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(PixivPic, self).__init__(url)
        # input url isn't a pixiv url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.PIXIV) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"pixiv.net\".")
        self.__api: PixivAPI = PixivAPI.instance()
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(PixivPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
        self.__api = None
    
    # private helper function
    def __analyzeUrl(self):
        cur = 0
        url = self.getUrl()
        j_dict = {}
        pid = 0
        
        # determine ParentChild status & grab pid
        if "/users/" in url:
            self.__parent_child = ParentChild.PARENT
            cur = url.rfind('/')+1
            pid = int(url[cur:findFirstNonNum(url, cur)])
        elif "/member.php" in url:
            self.__parent_child = ParentChild.PARENT
            cur = url.find("member.php?id=") + 14
            pid = int(url[cur:findFirstNonNum(url, cur)])
        elif "/artworks/" in url:
            self.__parent_child = ParentChild.CHILD
            cur = url.rfind('/')+1
            pid = int(url[cur:findFirstNonNum(url, cur)])
        elif "/member_illust.php" in url:
            self.__parent_child = ParentChild.CHILD
            cur = url.find("member_illust.php?id=") + 21
            pid = int(url[cur:findFirstNonNum(url, cur)])
        elif "pximg.net/" in url:
            self.__parent_child = ParentChild.CHILD
            parse1 = urllib.parse.urlparse(url)
            parse2 = ntpath.split(parse1.path)
            cur = parse2[1].find('/')
            pid = int(parse2[1][cur:parse2[1].rfind("_p")])
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # check for bad url
        if self.isChild():
            j_dict = self.__api.getIllustDetail(pid)
        elif self.isParent():
            j_dict = self.__api.getUserDetail(pid)
        else:
            raise ValueError(f"Cannot determine parent child state base on url: {self.getUrl()}")
        if "error" in j_dict:
            raise ValueError(f"Bad url: {self.getUrl()}")
        elif self.isChild() and j_dict["illust"]["visible"] == False:
            raise ValueError(f"Bad url: {self.getUrl()}")
        
        # whether has artist & init ArtistInfo
        tmp_str = ""
        if self.isChild():
            # find parent
            parent_pid = j_dict["illust"]["user"]["id"]
            tmp_dict = self.__api.getUserDetail(parent_pid)
            if "error" not in tmp_dict:
                self.__has_artist_flag = True
                tmp_str = "https://pixiv.net/users/" + str(parent_pid)
                self.__artist_info = ArtistInfo(WebPicType.PIXIV, tmp_str)
        elif self.isParent():
            self.__has_artist_flag = True
            tmp_str = "https://pixiv.net/users/" + str(pid)
            self.__artist_info = ArtistInfo(WebPicType.PIXIV, tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            single_ori_url = j_dict["illust"]["meta_single_page"]
            if single_ori_url != None and len(single_ori_url) > 0:
                self.__file_url.append(single_ori_url["original_image_url"])
                parse1 = urllib.parse.urlparse(self.__file_url[-1])
                parse2 = ntpath.split(parse1.path)
                self.__filename.append(parse2[1])
            else:
                for img in j_dict["illust"]["meta_pages"]:
                    self.__file_url.append(img["image_urls"]["original"])
                    parse1 = urllib.parse.urlparse(self.__file_url[-1])
                    parse2 = ntpath.split(parse1.path)
                    self.__filename.append(parse2[1])
                
            # get tags
            for item in j_dict["illust"]["tags"]:
                self.__tags.append(space2lowline(item["name"]))
                self.__tags.append(space2lowline(item["translated_name"]))
        
        # finding src_url
        if self.isChild():
            self.__src_url = "https://pixiv.net/artworks/" + str(j_dict["illust"]["id"])
        elif self.isParent():
            self.__src_url = self.__artist_info.getUrl_pixiv()
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = os.path.curdir):
        if self.isChild():
            for url in self.__file_url:
                path = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                self.__api.downloadIllust(url=url, path=path)
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get user illustration list
        tmp_str = self.__artist_info.getUrl_pixiv()[0]
        pid = int(tmp_str[tmp_str.rfind('/')+1:])
        
        # get all illustrations of this user
        j_list = self.__api.getUserIllustList(pid, max_num)
        counter = 0
        output = []
        
        # generate artwork urls
        for item in j_list:
            output.append("https://pixiv.net/artworks/"+str(item["id"]))
        
        return output


class TwitterPic(WebPic):
    """handle artist identifications & downloading for twitter"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # api handles
    __api: TwitterAPI = None
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(TwitterPic, self).__init__(url)
        # input url isn't a pixiv url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.TWITTER) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"twitter.com\".")
        self.__api: TwitterAPI = TwitterAPI.instance()
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(TwitterPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
        self.__api = None
    
    # private helper function
    def __analyzeUrl(self):
        cur = 0
        url = self.getUrl()
        j_dict = {}
        screen_name = ""
        status_id = ""
        
        # determine ParentChild status & grab screen_name, status_id
        parse1 = urllib.parse.urlparse(url)
        cur = parse1.path.find("/status/")
        if cur != -1: # found /status/ in url
            self.__parent_child = ParentChild.CHILD
            screen_name = parse1.path[1:cur]
            status_id = parse1.path[cur+8:]
        elif cur == -1: # not found /status in url
            self.__parent_child = ParentChild.PARENT
            screen_name = parse1.path[1:]
        else:
            self.__parent_child = ParentChild.UNKNOWN
        if len(screen_name) <= 0 and len(status_id) <= 0:
            raise ValueError(f"Unable to determine ParentChild base on URL{url}.")
        
        # check for bad url
        try:
            if self.isChild():
                j_dict = self.__api.getStatusJson(status_id=status_id)
                screen_name = j_dict["user"]["screen_name"]
            elif self.isParent():
                j_dict = self.__api.getUserJson(screen_name=screen_name)
            else:
                raise ValueError(f"Unable to fetch data from URL{url}")
        except Exception as err:
            raise err
        
        
        # whether has artist & init ArtistInfo
        tmp_str = ""
        if self.isChild():
            try:
                self.__api.getUserJson(screen_name=screen_name)
            except Exception as err:
                raise err
            self.__has_artist_flag = True
            tmp_str = "https://twitter.com/" + screen_name
            self.__artist_info = ArtistInfo(WebPicType.TWITTER, tmp_str)
        elif self.isParent():
            self.__has_artist_flag = True
            tmp_str = "https://twitter.com/" + screen_name
            self.__artist_info = ArtistInfo(WebPicType.TWITTER, tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            if "extended_entities" in j_dict and "media" in j_dict["extended_entities"]:
                for media in j_dict["extended_entities"]["media"]:
                    if len(media["media_url"]) > 0:
                        self.__file_url.append(media["media_url"])
                        parse1 = urllib.parse.urlparse(self.__file_url[-1])
                        parse2 = ntpath.split(parse1.path)
                        self.__filename.append(parse2[1])
            
            # get tags
            self.__tags.append(space2lowline(screen_name))
            for item in j_dict["entities"]["hashtags"]:
                self.__tags.append(item["text"])
        
        # finding src_url
        if self.isChild():
            self.__src_url = "https://twitter.com/" + screen_name + "/status/" + status_id
        elif self.isParent():
            self.__src_url = "https://twitter.com/" + screen_name
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = os.path.curdir):
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                downloadUrl(url+":orig", path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get user illustration list
        tmp_str = self.__artist_info.getUrl_twitter()[0]
        
        # get all illustrations of this user
        j_list = self.__api.getUserTimeline(screen_name=self.__artist_info.getArtistNames()[1], count=max_num)
        counter = 0
        output = []
        for stat in j_list:
            output.append(
                "https://twitter.com/" +
                self.__artist_info.getArtistNames()[1] +
                "/status/" + stat["id_str"])
            if counter >= max_num:
                break
            counter += 1
        
        return output


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(DanbooruPic, self).__init__(url)
        # input url is not a danbooru url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.DANBOORU) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"danbooru.donmai.us\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(DanbooruPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
    
    # private helper function
    def __analyzeUrl(self):
        # determine ParentChild
        cur = self.getUrl().find("/posts") + 6
        
        # determine ParentChild status
        if cur == -1:
            self.__parent_child = ParentChild.UNKNOWN
        elif self.getUrl()[cur] == '/':
            self.__parent_child = ParentChild.CHILD
        else:
            self.__parent_child = ParentChild.PARENT
        
        # get url source
        randDelay(1.0, 2.5)
        src = getUrlSrc(self.getUrl())
        
        # whether has artist
        if self.isChild():
            cur = src.find("artist-tag-list")
            if cur != -1:
                cur = src.find("class=\"wiki-link\"", cur)
        elif self.isParent():
            cur = src.find("artist-excerpt-link")
        # found artist
        if cur != -1:
            cur = src.find("href=\"", cur) + 6
            tmp_url = src[cur:src.find('\"', cur)]
            tmp_url = "https://" + WebPicType2DomainStr(self.getWebPicType()) + tmp_url
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_url)
        
        # finding file_url & filename
        cur = src.find("post-info-size")
        if cur != -1: # found file_url
            cur = src.find("href=\"", cur) + 6
            # set file url
            self.__file_url.append(src[cur:src.find('\"', cur)])
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url[-1])
            parse2 = ntpath.split(parse1.path)
            self.__filename.append(parse2[1])
        
        # finding src_url
        cur = src.find("post-info-source", cur)
        if cur != -1: # found source
            cur = src.find("href=\"", cur) + 6
            # set src_url
            self.__src_url = src[cur:src.find('\"', cur)]
        
        # get tags
        cur = 0
        while cur > -1:
            cur = src.find("data-tag-name=\"", cur)
            if cur < 0:
                break
            cur += 15
            tmp = src[cur:src.find('\"', cur)]
            self.__tags.append(tmp)
            cur += 3
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = None) -> None:
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                downloadUrl(url, path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        counter = 0
        # process url
        url = self.getUrl()
        parse1 = urllib.parse.urlparse(url)
        if parse1.query == None:
            url += "?page=#"
        elif "page=" not in parse1.query: # no page indicator
            url += "&page=#"
        else: # "page=" in parse1.query
            cur = url.find("page=")
            cur2 = findFirstNonNum(url, cur+5)
            url = url.replace(url[cur:cur2], "page=#")
        
        # fetching urls
        output = []
        page_count = 1
        while counter != max_num:
            # generate url for current page
            loc_url = url.replace("page=#", f"page={page_count}")
            page_count += 1
            
            # get url source
            randDelay(1.0, 2.5)
            src = getUrlSrc(url)
            cur = 0
            if "data-id" not in src: # reaches end of pages
                break
            
            # find post id from src & build post url w/ it
            while cur != -1:
                cur = src.find("data-id=\"", cur)
                if cur == -1:
                    break
                cur += 9
                post_id = src[cur:src.find('\"', cur)]
                output.append("https://"+WebPicType2DomainStr(WebPicType.DANBOORU)+"/posts/"+post_id)
                counter += 1
                if counter == max_num:
                    return output
            
        return output


class YanderePic(WebPic):
    """handle artist identifications & downloading for yande.re"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(YanderePic, self).__init__(url)
        # input url is not a yandere url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.YANDERE) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"yande.re\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(YanderePic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
    
    # private helper function
    def __analyzeUrl(self):
        # determine ParentChild
        cur = self.getUrl().find("/post/show/")
        
        # determine ParentChild stcatus
        if cur != -1: # found pattern
            self.__parent_child = ParentChild.CHILD
        elif "/post" in self.getUrl() or "/pool" in self.getUrl():
            self.__parent_child = ParentChild.PARENT
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # get url source
        randDelay(1.0, 2.5)
        src = getUrlSrc(self.getUrl())
        
        # get json data
        j_dict = {}
        tmp_str = "["
        cur = 0
        while cur != -1:
            cur = src.find("Post.register", cur)
            if cur == -1:
                break
            cur = src.find('(', cur) + 1
            tmp_str += src[cur:src.find('\n', cur)]
            tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
        if len(tmp_str) > 1:
            tmp_str = tmp_str[:-1] + ']'
            j_dict = json.loads(tmp_str)
        else: # bad url
            raise ValueError(f"Cannot process url: {self.getUrl()}")
        
        # whether has artist
        tmp_str = ""
        tmp_dict = {}
        if "tags" in j_dict[0]:
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        # found artist name
        for k, v in tmp_dict.items():
            if v == "artist":
                tmp_str = k
                break
        # get artist info
        if len(tmp_str) > 0:
            # generate artist wiki page
            tmp_str = "https://" + WebPicType2DomainStr(WebPicType.YANDERE) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url.append(j_dict[0]["posts"][0]["file_url"])
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url[-1])
            parse2 = ntpath.split(parse1.path)
            self.__filename.append(parse2[1])
            
            # finding src_url
            tmp_str = str(j_dict[0]["posts"][0]["source"])
            parse1 = urllib.parse.urlparse(tmp_str)
            if DomainStr2WebPicType(parse1.netloc) == WebPicType.PIXIV:
                # use pixiv id for pixiv source
                # handle new url
                cur = tmp_str.find("pixiv.net/artworks/")
                if cur != -1: 
                    self.__src_url = tmp_str
                # handle new url with /en/
                cur = tmp_str.find("pixiv.net/en/artworks/")
                if cur != -1:
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle old page url
                cur = tmp_str.find("illust_id=")
                if cur != -1: 
                    cur += 10
                    loc_cur = cur
                    for i in range(len(tmp_str)-cur):
                        loc_cur += i
                        if loc_cur >= len(tmp_str) or tmp_str[loc_cur].isalpha():
                            break
                    pid = tmp_str[cur:loc_cur]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle raw img url
                cur = tmp_str.find("pximg.net")
                if cur != -1: 
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    pid = pid[:pid.find('_')]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                pass
            elif len(parse1.netloc) > 0: # twitter and other
                self.__src_url = tmp_str
        
        # get tags
        tmp_dict = {}
        if self.isChild():
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        for k, v in tmp_dict.items():
            self.__tags.append(k)
    
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = None) -> None:
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                downloadUrl(url, path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # process url
        url = self.getUrl()
        parse1 = urllib.parse.urlparse(url)
        if parse1.query == None:
            url += "?page=#"
        elif "page=" not in parse1.query: # no page indicator
            url += "&page=#"
        else: # "page=" in parse1.query
            cur = url.find("page=")
            cur2 = findFirstNonNum(url, cur+5)
            url = url.replace(url[cur:cur2], "page=#")
        
        counter = 0
        page_count = 1
        last_post_id = 0
        output = []
        while counter != max_num:
            # generate loc_url
            loc_url = url.replace("page=#", f"page={page_count}")
            page_count += 1
            
            # get url source
            randDelay(1.0, 2.5)
            src = getUrlSrc(loc_url)
            
            # get json data
            j_dict = {}
            tmp_str = "["
            cur = 0
            # ignore bad url from pool
            if "/pool" in self.getUrl() and "var thumb = $(\"hover-thumb\");" in src:
                return 
            while cur != -1:
                cur = src.find("Post.register", cur)
                if cur == -1:
                    break
                cur = src.find('(', cur) + 1
                tmp_str += src[cur:src.find('\n', cur)]
                tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
            if len(tmp_str) > 1:
                tmp_str = tmp_str[:-1] + ']'
                j_dict = json.loads(tmp_str)
            else: # bad url
                return []
            
            # make sure we didn't reaches end of pages
            if "/post" in loc_url and len(j_dict[0]) == 0:
                break # reaches end of page
            elif "/pool/" in loc_url and j_dict[0]["posts"] == None:
                break # reaches end of page
            elif "/pool/" in loc_url:
                for item in j_dict[0]["posts"]:
                    if last_post_id == item["id"]:
                        return output
            
            # find post id from j_dict & build post url w/ it
            if len(j_dict) == 1 and "/pool/" in loc_url: # current parent is like "/pool/show/"
                for item in j_dict[0]["posts"]:
                    post_id = str(item["id"])
                    output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
                    counter += 1
                    last_post_id = item["id"]
                    if counter == max_num:
                        return output
            elif len(j_dict) > 1 and "/post" in loc_url: # current parent is like "/post?tags="
                for item in j_dict[1:]:
                    post_id = str(item["id"])
                    output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
                    counter += 1
                    last_post_id = item["id"]
                    if counter == max_num:
                        return output
            if counter == max_num:
                return output
        
        return output


class KonachanPic(WebPic):
    """handle artist identifications & downloading for konachan"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(KonachanPic, self).__init__(url)
        # input url is not a konachan url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.KONACHAN) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"konachan\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(KonachanPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
    
    # private helper function
    def __analyzeUrl(self):
        # determine ParentChild
        cur = self.getUrl().find("/post/show/")
        
        # determine ParentChild status
        if cur != -1: # found pattern
            self.__parent_child = ParentChild.CHILD
        elif "/post" in self.getUrl() or "/pool" in self.getUrl():
            self.__parent_child = ParentChild.PARENT
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # get url source
        randDelay(1.0, 2.5)
        src = getUrlSrc(self.getUrl())
        
        # get json data
        j_dict = {}
        tmp_str = "["
        cur = 0
        # ignore bad url from pool
        if "/pool" in self.getUrl() and "var thumb = $(\"hover-thumb\");" in src:
            raise ValueError(f"Bad konachan pool. Url: {self.getUrl()}")
        while cur != -1:
            cur = src.find("Post.register", cur)
            if cur == -1:
                break
            cur = src.find('(', cur) + 1
            tmp_str += src[cur:src.find('\n', cur)]
            tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
        if len(tmp_str) > 1:
            tmp_str = tmp_str[:-1] + ']'
            j_dict = json.loads(tmp_str)
        else: # bad url
            raise ValueError(f"Cannot process url: {self.getUrl()}")
        
        # whether has artist
        tmp_str = ""
        tmp_dict = {}
        if "tags" in j_dict[0]:
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        # found artist name
        for k, v in tmp_dict.items():
            if v == "artist":
                tmp_str = k
                break
        # get artist info
        if len(tmp_str) > 0:
            # generate artist wiki page
            tmp_str = "https://" + WebPicType2DomainStr(WebPicType.KONACHAN) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url.append(j_dict[0]["posts"][0]["file_url"])
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url[-1])
            parse2 = ntpath.split(parse1.path)
            self.__filename.append(parse2[1])
            
            # finding src_url
            tmp_str = str(j_dict[0]["posts"][0]["source"])
            parse1 = urllib.parse.urlparse(tmp_str)
            if DomainStr2WebPicType(parse1.netloc) == WebPicType.PIXIV:
                # use pixiv id for pixiv source
                # handle new url
                cur = tmp_str.find("pixiv.net/artworks/")
                if cur != -1: 
                    self.__src_url = tmp_str
                # handle new url with /en/
                cur = tmp_str.find("pixiv.net/en/artworks/")
                if cur != -1:
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle old page url
                cur = tmp_str.find("illust_id=")
                if cur != -1: 
                    cur += 10
                    loc_cur = cur
                    for i in range(len(tmp_str)-cur):
                        loc_cur += i
                        if loc_cur >= len(tmp_str) or tmp_str[loc_cur].isalpha():
                            break
                    pid = tmp_str[cur:loc_cur]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle raw img url
                cur = tmp_str.find("pximg.net")
                if cur != -1: 
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    pid = pid[:pid.find('_')]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                pass
            elif len(parse1.netloc) > 0: # twitter and other
                self.__src_url = tmp_str
        
        # get tags
        tmp_dict = {}
        if self.isChild():
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        for k, v in tmp_dict.items():
            self.__tags.append(k)
    
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = None) -> None:
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                downloadUrl(url, path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # process url
        url = self.getUrl()
        parse1 = urllib.parse.urlparse(url)
        if parse1.query == None:
            url += "?page=#"
        elif "page=" not in parse1.query: # no page indicator
            url += "&page=#"
        else: # "page=" in parse1.query
            cur = url.find("page=")
            cur2 = findFirstNonNum(url, cur+5)
            url = url.replace(url[cur:cur2], "page=#")
        
        counter = 0
        page_count = 1
        last_post_id = 0
        output = []
        while counter != max_num:
            # generate loc_url
            loc_url = url.replace("page=#", f"page={page_count}")
            page_count += 1
            
            # get url source
            randDelay(1.0, 2.5)
            src = getUrlSrc(loc_url)
            
            # get json data
            j_dict = {}
            tmp_str = "["
            cur = 0
            # ignore bad url from pool
            if "/pool" in self.getUrl() and "var thumb = $(\"hover-thumb\");" in src:
                return 
            while cur != -1:
                cur = src.find("Post.register", cur)
                if cur == -1:
                    break
                cur = src.find('(', cur) + 1
                tmp_str += src[cur:src.find('\n', cur)]
                tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
            if len(tmp_str) > 1:
                tmp_str = tmp_str[:-1] + ']'
                j_dict = json.loads(tmp_str)
            else: # bad url
                return []
            
            # make sure we didn't reaches end of pages
            if "/post" in loc_url and len(j_dict[0]) == 0:
                break # reaches end of page
            elif "/pool/" in loc_url and j_dict[0]["posts"] == None:
                break # reaches end of page
            elif "/pool/" in loc_url:
                for item in j_dict[0]["posts"]:
                    if last_post_id == item["id"]:
                        return output
            
            # find post id from j_dict & build post url w/ it
            if len(j_dict) == 1 and "/pool/" in loc_url: # current parent is like "/pool/show/"
                for item in j_dict[0]["posts"]:
                    post_id = str(item["id"])
                    last_post_id = item["id"]
                    output.append("https://"+WebPicType2DomainStr(WebPicType.KONACHAN)+"/post/show/"+post_id)
                    counter += 1
                    if counter == max_num:
                        return output
            elif len(j_dict) > 1 and "/post" in loc_url: # current parent is like "/post?tags="
                for item in j_dict[1:]:
                    post_id = str(item["id"])
                    last_post_id = item["id"]
                    output.append("https://"+WebPicType2DomainStr(WebPicType.KONACHAN)+"/post/show/"+post_id)
                    counter += 1
                    if counter == max_num:
                        return output
            if counter == max_num:
                return output
        
        return output


class WeiboPic(WebPic):
    """handle artist identifications & downloading for weibo"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(WeiboPic, self).__init__(url)
        # input url is not a konachan url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.WEIBO) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"weibo\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(WeiboPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
    
    # private helper function
    def __analyzeUrl(self):
        
        # loc var
        url = self.getUrl()
        user_id = 0
        status_id = 0
        
        # determine domain type
        cur = url.find(WebPicType2DomainStr(WebPicType.WEIBO))
        
        if cur == -1:
            # input weibo url is "www.weibo.com" domain
            # assume input url is parent
            self.__parent_child = ParentChild.PARENT
            
            # get user_id
            randDelay(2.5, 5.0)
            src = getUrlSrc(self.getUrl())
            cur = src.find("$CONFIG[\'oid\']=\'")
            if cur != -1:
                cur += 16
                user_id = int(src[cur:src.find("\'", cur)])
            
        else: # input weibo url is "m.weibo.cn"
            parse1 = urllib.parse.urlparse(url)
            parse2 = ntpath.split(parse1.path)
            
            # determine ParentChild status for "m.weibo.cn"
            if "/detail/" in url or "/status/" in url: # found pattern
                self.__parent_child = ParentChild.CHILD
                # set status_id
                status_id = int(parse2[1])
            elif "/u/" in url:
                self.__parent_child = ParentChild.PARENT
                # set user_id
                user_id = int(parse2[1])
            else:
                self.__parent_child = ParentChild.UNKNOWN
        
        # get json data
        j_dict = {}
        tmp_str = ""
        try:
            randDelay(2.5, 5.0)
            if self.__parent_child == ParentChild.PARENT:
                j_dict = getUrlJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&value={user_id}&containerid=100505{user_id}")
            elif self.__parent_child == ParentChild.CHILD:
                j_dict = getUrlJson(f"https://m.weibo.cn/statuses/show?id={status_id}")
            if j_dict["ok"] != 1:
                raise ValueError("Unable to fetch json data from weibo")
        except Exception as err:
            raise err
        
        if self.isParent():
                parse1 = urllib.parse.urlparse(self.getUrl())
                tmp_str = "https://" + parse1.netloc + parse1.path
                # has artist
                self.__has_artist_flag = True
                # initialize ArtistInfo
                self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        elif self.isChild():
            # whether has artist & get artistInfo
            if "user" in j_dict["data"]:
                # generate "m.weibo.cn" user url
                tmp_str = "https://m.weibo.cn/u/" + str(j_dict["data"]["user"]["id"])
                # has artist
                self.__has_artist_flag = True
                # initialize ArtistInfo
                self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
            
            # finding file_url & filename
            for pic in j_dict["data"]["pics"]:
                self.__file_url.append(pic["large"]["url"])
                parse1 = urllib.parse.urlparse(pic["large"]["url"])
                parse2 = ntpath.split(parse1.path)
                self.__filename.append(parse2[1])
            
            # assume weibo as a source, set src_url
            self.__src_url = "https://m.weibo.cn/status/" + j_dict["data"]["id"]
        
        # get tags
        if self.isParent():
            self.__tags.append(j_dict["data"]["userInfo"]["screen_name"])
        elif self.isChild():
            self.__tags.append(j_dict["data"]["user"]["screen_name"])
    
    
    # getters 
    def getFileUrl(self) -> str:
        return self.__file_url
    
    def getFileName(self) -> str:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = None) -> None:
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                downloadUrl(url, path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # loc var
        user_id = 0
        page_count = 1
        item_count = 0
        j_dict = {}
        output = []
        
        # get urser_id
        parse1 = urllib.parse.urlparse(self.getUrl())
        parse2 = ntpath.split(parse1.path)
        user_id = int(parse2[1])
        
        # getting children urls
        while item_count < max_num:
            # get user timeline
            try:
                randDelay(2.5, 5.0)
                j_dict = getUrlJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&page={page_count}&containerid=107603{user_id}")
                if j_dict["ok"] != 1:
                    break
            except Exception as err:
                raise err
            
            # record each status with image
            for status in j_dict["data"]["cards"]:
                if ("mblog" in status and
                    "pics" in status["mblog"] and
                    len(status["mblog"]["pics"]) > 0
                    ): # status has image
                    
                    output.append("https://m.weibo.cn/status/"+status["mblog"]["id"])
                    item_count += 1
                if item_count >= max_num:
                    break
            page_count += 1
        
        return output


class EHentaiPic(WebPic):
    """handle artist identifications & downloading for e-hentai"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: list = []
    __filename: list = []
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # api handles
    __api: EHentaiAPI = None
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(EHentaiPic, self).__init__(url)
        # input url is not a konachan url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.EHENTAI) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"e-hentai\".")
        self.__api: EHentaiAPI = EHentaiAPI.instance()
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(EHentaiPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = 0
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
        self.__api = None
    
    # private helper function
    def __analyzeUrl(self):
        # loc vars
        url = self.getUrl()
        
        # determine ParentChild status
        if self.__api.isValidPicture(url):
            self.__parent_child = ParentChild.CHILD
        elif self.__api.isValidGallery(url) or isValidUrl(url):
            self.__parent_child = ParentChild.PARENT
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # get parent json data
        j_dict = {}
        if self.isParent():
            j_dict = self.__api.getGalleryInfo(url)
        elif self.isChild():
            j_dict = self.__api.getGalleryInfo(
                self.__api.findParentGalleryUrl(url))
        else:
            return
        
        # finding tags & artist
        if self.__api.isValidGallery(url) or self.__api.isValidPicture(url):
            j_list = []
            for tag in j_dict["gmetadata"][0]["tags"]:
                cur = tag.find(':')
                left = ""
                right = ""
                if cur >= 0:
                    left = tag[:cur]
                    right = tag[cur+1:]
                else:
                    left = ""
                    right = tag
                
                # whether has artist in the gallery
                if "artist" in left: 
                    # has artist
                    self.__has_artist_flag = True
                    # store josn list of artist names for ArtistInfo
                    j_list.append(right)
                
                # store tag
                self.__tags.append(right)
            
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), json.dumps(j_list, ensure_ascii=False))
        
        if self.isChild():
            # finding file_url & filename
            self.__file_url.append(self.__api.getPicUrl(url))
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url[-1])
            parse2 = ntpath.split(parse1.path)
            self.__filename.append(parse2[1])
            
            # assume e-hentai do not have src_url
    
    
    # getters 
    def getFileUrl(self) -> list:
        return self.__file_url
    
    def getFileName(self) -> list:
        return self.__filename
    
    def getSrcUrl(self) -> str:
        return self.__src_url
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistInfo(self) -> ArtistInfo:
        return self.__artist_info
    
    def getTags(self) -> list:
        return self.__tags
    
    def isParent(self) -> bool:
        return bool(self.__parent_child == ParentChild.PARENT)
    
    def isChild(self) -> bool:
        return bool(self.__parent_child == ParentChild.CHILD)
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath = None) -> None:
        if self.isChild():
            count = 0
            for url, filename in zip(self.__file_url, self.__filename):
                path = ""
                name = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                    name = filename
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                    # add number indicator to the end of specified filename
                    if '.' in name: # filename has extension
                        name.replace('.', f"_{count}.", 1)
                    else: # filename does not has extension
                        name += f"_{count}.jpg"
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                randDelay(self.__api.getMinDelay(), self.__api.getMaxDelay())
                downloadUrl(url, path+name)
                count += 1
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        url = self.getUrl()
        
        if self.__api.isValidGallery(url):
            return self.__api.getPicsInGallery(url, max_num)
        else: # current url is a search page url
            return self.__api.getGalleriesFromSearch(url, max_num)


def url2WebPic(url: str) -> any:
    """Get WebPic object from any supported url"""
    webpic_type = DomainStr2WebPicType(url)
    if webpic_type == WebPicType.PIXIV:
        return PixivPic(url)
    elif webpic_type == WebPicType.TWITTER:
        return TwitterPic(url)
    elif webpic_type == WebPicType.DANBOORU:
        return DanbooruPic(url)
    elif webpic_type == WebPicType.YANDERE:
        return YanderePic(url)
    elif webpic_type == WebPicType.KONACHAN:
        return KonachanPic(url)
    elif webpic_type == WebPicType.WEIBO:
        return WeiboPic(url)
    elif webpic_type == WebPicType.EHENTAI:
        return EHentaiPic(url)
    else: # Unknown
        return None

def printInfo(webpic: any) -> None:
    """Printing all info of a supported WebPic"""
    try:
        if (webpic is None or
            DomainStr2WebPicType(webpic.getUrl()) == WebPicType.UNKNOWN or
            isEmptyWebPic(webpic)
            ):
            return
    except: # ignore if caught exceptions
        return
    
    print(f"{webpic.getUrl() = }")
    print(f"{webpic.getWebPicType() = }")
    print(f"{webpic.getParentChildStatus() = }")
    print(f"{webpic.getFileUrl() = }")
    print(f"{webpic.getFileName() = }")
    print(f"{webpic.getSrcUrl() = }")
    print(f"{webpic.hasArtist() = }")
    if webpic.hasArtist():
        print(f"{webpic.getArtistInfo().getArtistNames() = }")
        print(f"{webpic.getArtistInfo().getUrl_pixiv() = }")
        print(f"{webpic.getArtistInfo().getUrl_twitter() = }")
    print(f"{webpic.getTags() = }")

