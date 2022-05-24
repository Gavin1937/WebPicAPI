
from ..Util.httpUtilities import downloadFile, getSrcStr
from ..Util import urlHandler
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch, WebPicType2DomainStr
from .ArtistInfo import ArtistInfo
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Union


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    # constructor
    def __init__(self, url:str, artist_info:ArtistInfo=None, min_delay:float=0.0, max_delay:float=1.0):
        """
            Initializing DanbooruPic.\n
            \n
            :Param:\n
                url          => str url to a danbooru page\n
                artist_info  => ArtistInfo from a parent. \n
                                If given, class will use given ArtistInfo instead of requesting new one.\n
                                This parameter is only for child url to save time.\n
                min_delay    => float minimum delay time in seconds (default 0.0)\n
                max_delay    => float maximum delay time in seconds (default 1.0)\n
            \n
            :Number of Requests: [2]\n
        """
        
        # private members
        self.__parent_child:ParentChild = ParentChild.UNKNOWN
        self.__file_url:list = []
        self.__filename:list = []
        self.__src_url:str = ""
        self.__has_artist_flag:bool = False
        self.__artist_info:ArtistInfo = None
        self.__tags:list = []
        
        # init super class & analyze url
        super(DanbooruPic, self).__init__(url, min_delay, max_delay)
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.DANBOORU) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"danbooru.donmai.us\".")
        self.__analyzeUrl(artist_info)
    
    
    # clear obj
    def clear(self) -> None:
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url.clear()
        self.__filename.clear()
        self.__src_url = None
        self.__has_artist_flag = False
        if self.__artist_info != None:
            self.__artist_info.clear()
        self.__tags.clear()
        super(DanbooruPic, self).clear()
    
    # private helper function
    def __analyzeUrl(self, artist_info:ArtistInfo=None):
        
        tmp_url = None
        
        # determine ParentChild status
        url = urlHandler(self.getUrl())
        if url.isPatternInPathR(r".*/posts/\d+$"):
            self.__parent_child = ParentChild.CHILD
        elif url.isPatternInPathR(r".*/posts$"):
            self.__parent_child = ParentChild.PARENT
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # get url source soup
        self._delay()
        soup = BeautifulSoup(getSrcStr(self.getUrl()), 'lxml')
        
        # handle given artist_info
        if self.isChild() and artist_info:
            self.__has_artist_flag = True
            self.__artist_info = artist_info
        
        # finding artist if don't have one 
        if (self.__has_artist_flag == False and self.__artist_info is None):
            if self.isChild():
                tmp_url = soup.select_one("ul.artist-tag-list a")
            elif self.isParent():
                tmp_url = soup.select_one("a.artist-excerpt-link")
            # found artist
            if tmp_url:
                tmp_url = "https://" + WebPicType2DomainStr(self.getWebPicType()) + tmp_url.get('href')
                self.__has_artist_flag = True
                self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_url)
        
        # finding file_url & filename
        tmp_url = soup.select_one("li#post-info-size a")
        if tmp_url: # found file_url
            self.__file_url.append(tmp_url.get('href'))
            tmp_url = urlHandler(tmp_url.get('href'))
            self.__filename.append(tmp_url.getPathPart(-1))
        
        # finding src_url
        tmp_url = soup.select_one("li#post-info-source a")
        if tmp_url: # found source
            self.__src_url = tmp_url.get('href')
        
        # get tags
        tags = soup.select("li[data-tag-name]")
        for t in tags:
            self.__tags.append(t.get('data-tag-name'))
        self.__tags = list(set(self.__tags))
    
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
    
    def isEmpty(self) -> bool:
        return (
            len(self.__file_url) == 0 and
            len(self.__filename) == 0 and
            self.__src_url == 0 and
            self.__has_artist_flag == False and
            len(self.__tags) == 0
        )
    
    def getParentChildStatus(self) -> ParentChild:
        return self.__parent_child
    
    def downloadPic(self, dest_filepath:Union[str,Path]=None, overwrite:bool=False) -> bool:
        """
            Download pictures in a child.\n
            \n
            :Param:\n
                dest_filepath    => str | Path filepath to destination\n
                overwrite        => bool flag whether to overwrite duplicate file\n
            \n
            :Number of Requests: [1]\n
            \n
            :Return:\n
                if download success yield True, otherwise yield False\n
        """
        if self.isChild():
            for url in self.__file_url:
                try:
                    yield downloadFile(url, dest_filepath, overwrite)
                except Exception: # dest_filepath invalid or duplicate file
                    raise
    
    def getChildrenUrls(self, limit:int=30) -> list:
        """
            Get all children urls of a parent until reaches limit.\n
            \n
            :Param:\n
                limit => maximum number of children to fetch. (default 30, set to -1 to fetch all)\n
            \n
            :Number of Requests: [limit]\n
            \n
            :Return:\n
                if current WebPic is Child, return a list of str urls (list[str])\n
                if current WebPic is Parent, return empty list\n
        """
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # setup
        pic_count = 0
        output = []
        
        soup = BeautifulSoup(getSrcStr(self.getUrl()), 'lxml')
        
        while pic_count != limit:
            
            # get all pictures in current page
            for a in soup.select("article[id^='post_'] a"):
                url = urlHandler("https://"+WebPicType2DomainStr(WebPicType.DANBOORU)+a.get('href'))
                output.append(url.clearParam().toString())
                pic_count += 1
                
                # reaches limit
                if pic_count == limit:
                    break
            
            # get next page url & fetch next page
            next_link = soup.select_one("link[rel='next']")
            if next_link:
                next_link = "https://"+WebPicType2DomainStr(WebPicType.DANBOORU)+next_link.get('href')
                soup = BeautifulSoup(getSrcStr(next_link), 'lxml')
            else:
                break
        
        return output
    

