
from .types import WebPicType, ParentChild
import urllib.parse


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

