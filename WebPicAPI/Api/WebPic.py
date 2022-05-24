
from ..Util.httpUtilities import randDelay
from ..Util import urlHandler
from .types import WebPicType

class WebPic:
    """Online Picture/Wallpaper website template class"""
    
    # constructor
    def __init__(self, url:str, min_delay:float=0.0, max_delay:float=1.0):
        """
            Initialize WebPic.\n
            \n
            :Param:\n
                url          => str url from supported websites\n
                min_delay    => float minimum delay time in seconds (default 0.0)\n
                max_delay    => float maximum delay time in seconds (default 1.0)\n
            \n
            :About Delay:\n
                Every WebPic subclasses need to perform HTTP Requests in order to 
                fetch necessary data. Delays are designed to insert between requests 
                to avoid ip banning. In all the WebPic subclasses, the number of 
                requests will be labeled if it needs to perform requests. 
        """
        
        # private variable
        self.__url:str = url
        self.__webpic_type:WebPicType = WebPicType.UNKNOWN
        self.__min_delay:float = min_delay
        self.__max_delay:float = max_delay
        
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
    
    def getMinDelay(self) -> float:
        return self.__min_delay
    
    def setMinDelay(self, delay:float):
        self.__min_delay = delay
    
    def getMaxDelay(self) -> float:
        return self.__max_delay
    
    def setMaxDelay(self, delay:float):
        self.__max_delay = delay
    
    def _delay(self):
        "Run randDelay with __min_delay and __max_delay"
        randDelay(self.__min_delay, self.__max_delay)

