

# libs
from urllib3 import PoolManager
import os
import ntpath
from urllib.parse import urlparse
from enum import IntEnum


# public functions

def getUrlSource(url) -> str:
    """get url source as string"""
    
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data

def downloadUrl(url, dest_filepath = None):
    """download url to dest_filepath"""
    
    dir = os.getcwd()
    filename = ""
    
    # use original filename in url if user did not provide one in dest_filepath
    if dest_filepath == None:
        p = urlparse(url)
        u_dir, u_filename = ntpath.split(p.path)
        filename = u_filename
    # user provided dest_filepath
    else:
        tmp_dir,tmp_filename = ntpath.split(dest_filepath)
        # only continue if dest_filepath is a valid filepath (w/ complete dir & filename)
        if len(tmp_filename) > 0 and len(tmp_dir) > 0:
            dir = tmp_dir
            filename = tmp_filename
    
    # download file
    resp = PoolManager().request("GET", url)
    file = open(dir+'/'+filename, "wb")
    file.write(resp.data)
    file.close()


# WebPicType const Table
# Bit Table:
# 0b        1             1       1       1         1         1         1       1
#        Unknown      e-hentai  weibo  konachan  yande.re  danbooru  twitter  pixiv
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

def WebPicTypeMatch(src_type: WebPicType, dest_type) -> bool:
    """Check wether src_type is same as dest_type"""
    # handle String dest_type
    loc_dest_type = WebPicType.UNKNOWN
    if type(dest_type) == str:
        print("is str")
        loc_dest_type = Str2WebPicType(dest_type)
    else: # dest_type is WebPicType
        loc_dest_type = dest_type
    return bool(src_type == loc_dest_type)


class ArtistInfo:
    """Process & Hold Artist Information"""
    
    # private variables
    __artist_names: list = []
    __artist_has_fixed_name: bool = False
    __artist_fixed_name: str = ""
    __pixiv_url: str = ""
    __twitter_url: str = ""
    
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
    
    # getters
    def getArtistNames(self) -> list:
        return self.__artist_names
    
    def artistHasFixedName(self) -> bool:
        return self.__artist_has_fixed_name
    
    def getArtistFixedName(self) -> str:
        return self.__artist_fixed_name
    
    def getUrl_pixiv(self) -> str:
        return self.__pixiv_url
    
    def getUrl_twitter(self) -> str:
        return self.__twitter_url
    
    # helper functions
    def __analyzeInfo_pixiv(self, url):
        pass
    
    def __analyzeInfo_twitter(self, url):
        pass
    
    def __analyzeInfo_danbooru(self, url):
        pass
    
    def __analyzeInfo_yandere(self, url):
        pass
    
    def __analyzeInfo_konachan(self, url):
        pass
    
    def __analyzeInfo_weibo(self, url):
        pass
    
    def __analyzeInfo_ehentai(self, url):
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
        from urllib.parse import urlparse
        p = urlparse(self.getUrl())
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
    
    # public methods
    def getUrl(self):
        return self.__url
    
    def getWebPicType(self):
        return self.__webpic_type


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
    __has_artist_flag: bool = False
    __artist_name: str = ""
    __tags: list = []
    
    # constructor
    def __init__(self, url: str):
        super().__init__(url)
        # input url is not a danbooru url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.DANBOORU) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"danbooru.donmai.us\".")
        self.__analyzeUrl()
    
    # private helper function
    def __analyzeUrl(self):
        # determine ParentChild
        pos1 = self.getUrl().find("/posts") + 6
        pos2 = self.getUrl().find("?", pos1)
        
        # determine ParentChild status
        if pos1 == -1:
            self.__parent_child == ParentChild.UNKNOWN
        elif self.getUrl()[pos1] == '/':
            self.__parent_child == ParentChild.CHILD
        else:
            self.__parent_child == ParentChild.PARENT
        
        # get url source
        src = getUrlSource(self.getUrl())
        
        # 
        
        
        pass
    
    # getters 
    def getFileUrl(self) -> str:
        return self.__file_url
    
    def getFileName(self) -> str:
        return self.__filename
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistName(self) -> str:
        return self.__artist_name
    
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


