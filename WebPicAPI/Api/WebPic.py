
from ..Util import urlHandler
from .types import WebPicType


class WebPic:
    """Online Picture/Wallpaper website template class"""
    
    # constructor
    def __init__(self, url: str):
        
        # private variable
        self.__url: str = url
        self.__webpic_type: WebPicType = WebPicType.UNKNOWN
        
        # identify __webpic_type
        p = urlHandler(self.__url)
        if p.isPatternInDomain("pixiv.net"):
            self.__webpic_type = WebPicType.PIXIV
        elif p.isPatternInDomain("twitter.com") or p.isPatternInDomain("twimg.com"):
            self.__webpic_type = WebPicType.TWITTER
        elif p.isPatternInDomain("danbooru.donmai.us"):
            self.__webpic_type = WebPicType.DANBOORU
        elif p.isPatternInDomain("yande.re"):
            self.__webpic_type = WebPicType.YANDERE
        elif p.isPatternInDomain("konachan.com"):
            self.__webpic_type = WebPicType.KONACHAN
        elif p.isPatternInDomain("weibo.c"):
            self.__webpic_type = WebPicType.WEIBO
        elif p.isPatternInDomain("e-hentai.org"):
            self.__webpic_type = WebPicType.EHENTAI
        else: # Unknown
            self.__webpic_type = WebPicType.UNKNOWN
    
    def clear(self) -> None:
        self.__url = 0
        self.__webpic_type = WebPicType.UNKNOWN
    
    def getUrl(self) -> str:
        return self.__url
    
    def getWebPicType(self) -> WebPicType:
        return self.__webpic_type

