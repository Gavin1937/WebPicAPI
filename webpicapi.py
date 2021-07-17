

# public functions

def getUrlSource(url) -> str:
    """get url source as string"""
    
    from urllib3 import PoolManager
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data

def downloadUrl(url, dest_filepath = None):
    """download url to dest_filepath"""
    
    from os import getcwd
    dir = getcwd()
    filename = ""
    
    # use original filename in url if user did not provide one in dest_filepath
    import ntpath
    if dest_filepath == None:
        from urllib.parse import urlparse
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
    from urllib3 import PoolManager
    resp = PoolManager().request("GET", url)
    file = open(dir+'/'+filename, "wb")
    file.write(resp.data)
    file.close()


from enum import IntEnum
from os import WEXITED
# WebPicType const Table
# Bit Table:
# 0b        0             0       0       0         0         0         0       0
#    ReserveForFuture  Unknown  weibo  konachan  yande.re  danbooru  twitter  pixiv
class WebPicType(IntEnum):
    """Type of different picture/wallpaper websites"""
    PIXIV = 1,     # 0b00000001
    TWITTER = 2,   # 0b00000010
    DANBOORU = 4,  # 0b00000100
    YANDERE = 8,   # 0b00001000
    KONACHAN = 16, # 0b00010000
    WEIBO = 32,    # 0b00100000
    UNKNOWN = 64   # 0b01000000

def WebPicType2Str(webpic_type: WebPicType) -> str:
    """Convert WebPicType into String"""
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
    else: # Unknown
        return None


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
        else: # Unknown
            self.__webpic_type = WebPicType.UNKNOWN
    
    # public methods
    def getUrl(self):
        return self.__url
    
    def getWebPicType(self):
        return self.__webpic_type



class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    __file_url: str = ""
    __filename: str = ""
    __has_artist_flag: bool = False
    __artist_name: str = ""
    
    def __init__(self, url: str):
        super().__init__(url)
        self.__analyzeUrl()
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistName(self) -> str:
        return self.__artist_name
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)
    
    def __analyzeUrl(self):
        return self.getWebPicType()



