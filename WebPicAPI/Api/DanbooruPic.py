
from ..Util import getSrcStr, findFirstNonNum
from ..Util.httpUtilities import randDelay, downloadFile
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch, WebPicType2DomainStr
from .ArtistInfo import ArtistInfo
import urllib.parse
import ntpath
import os


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
        src = getSrcStr(self.getUrl())
        
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
                downloadFile(url, path+name)
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
            src = getSrcStr(url)
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
    

