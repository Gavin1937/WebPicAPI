#! /bin/python3

# libs
from urllib3 import PoolManager
import os
import ntpath
import urllib.parse
import json
from enum import IntEnum
from ApiManager import *


# public functions

def getUrlSource(url) -> str:
    """get url source as string"""
    
    if len(url) <= 0:
        return
    
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data

def downloadUrl(url, dest_filepath = os.path.curdir):
    """download url to dest_filepath"""
    
    # check url
    if len(url) <= 0:
        return
    
    # get dir & filrname from dest_filepath
    dir, filename = ntpath.split(dest_filepath)
    
    # no filename, use filename from url
    if filename == None or len(filename) <= 0: 
        p = urllib.parse.urlparse(url)
        u_dir, u_filename = ntpath.split(p.path)
        filename = u_filename
    # has filename but no dir
    elif dir == None or len(dir) <= 0:
        return
    # has filename & dir
    else:
        # download file
        resp = PoolManager().request("GET", url)
        file = open(dir+'/'+filename, "wb")
        file.write(resp.data)
        file.close()

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
        return "e-hentai"
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
    elif webpic_type_str == "e-hentai":
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
        return "weibo.com"
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
    elif "weibo.com" in domain_str:
        return WebPicType.WEIBO
    elif "e-hentai.org" in domain_str:
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicTypeMatch(src_type: WebPicType, dest_type) -> bool:
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
    def clear(self):
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
        pass
    
    def __analyzeInfo_danbooru(self, url: str):
        cur = 0
        
        # get url source
        src = getUrlSource(url)
        
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
        src = getUrlSource(url)
        
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
        src = getUrlSource(url)
        
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
        pass
    
    def __analyzeInfo_ehentai(self, url: str):
        pass
    


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
    def clear(self):
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
        self.__api = PixivAPI.instance()
        self.__analyzeUrl()
    
    # clear obj
    def clear(self):
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
            parse2 = ntpath.split(parse1.path())
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
            return
        if "error" in j_dict:
            return
        
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
                path, name = ntpath.split(dest_filepath)
                self.__api.downloadIllust(url=url, path=path)
    
    def getChildrenUrls(self) -> list:
        """Get all children urls of a parent"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        output = []
        
        # get user illustration list
        tmp_str = self.__artist_info.getUrl_pixiv()[0]
        pid = int(tmp_str[tmp_str.rfind('/')+1:])
        
        # get all illustrations of this user
        j_dict = self.__api.getUserIllustList(pid)
        while "next_url" in j_dict:
            for item in j_dict["illusts"]:
                output.append("https://pixiv.net/artworks/"+str(item["id"]))
            if j_dict["next_url"] == None:
                return output
            j_dict = self.__api.getUserIllustList_nextPage(j_dict["next_url"])
        
        return output


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
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
    def clear(self):
        super(DanbooruPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            tmp_url = WebPicType2DomainStr(self.getWebPicType()) + tmp_url
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_url)
        
        # finding file_url & filename
        cur = src.find("post-info-size")
        if cur != -1: # found file_url
            cur = src.find("href=\"", cur) + 6
            # set file url
            self.__file_url = src[cur:src.find('\"', cur)]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
        
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)
    
    def getChildrenUrls(self) -> list:
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get url source
        src = getUrlSource(self.getUrl())
        
        # find post id from src & build post url w/ it
        output = []
        cur = 0
        while cur != -1:
            cur = src.find("data-id=\"", cur)
            if cur == -1:
                break
            cur += 9
            post_id = src[cur:src.find('\"', cur)]
            output.append("https://"+WebPicType2DomainStr(WebPicType.DANBOORU)+"/posts/"+post_id)
        
        return output


class YanderePic(WebPic):
    """handle artist identifications & downloading for yande.re"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
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
    def clear(self):
        super(YanderePic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            return
        
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
            tmp_str = WebPicType2DomainStr(WebPicType.YANDERE) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url = j_dict[0]["posts"][0]["file_url"]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
            
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)
    
    def getChildrenUrls(self) -> list:
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get url source
        src = getUrlSource(self.getUrl())
        
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
        
        # find post id from j_dict & build post url w/ it
        output = []
        if len(j_dict) == 1: # current parent is like "/pool/show/"
            for item in j_dict[0]["posts"]:
                post_id = str(item["id"])
                output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
        elif len(j_dict) > 1: # current parent is like "/post?tags="
            for item in j_dict[1:]:
                post_id = str(item["id"])
                output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
        
        return output


class KonachanPic(WebPic):
    """handle artist identifications & downloading for konachan"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
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
    def clear(self):
        super(KonachanPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            return
        
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
            tmp_str = WebPicType2DomainStr(WebPicType.KONACHAN) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url = j_dict[0]["posts"][0]["file_url"]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
            
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)
    
    def getChildrenUrls(self) -> list:
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get url source
        src = getUrlSource(self.getUrl())
        
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
        
        # find post id from j_dict & build post url w/ it
        output = []
        if len(j_dict) == 1: # current parent is like "/pool/show/"
            for item in j_dict[0]["posts"]:
                post_id = str(item["id"])
                output.append("https://"+WebPicType2DomainStr(WebPicType.KONACHAN)+"/post/show/"+post_id)
        elif len(j_dict) > 1: # current parent is like "/post?tags="
            for item in j_dict[1:]:
                post_id = str(item["id"])
                output.append("https://"+WebPicType2DomainStr(WebPicType.KONACHAN)+"/post/show/"+post_id)
        
        return output


