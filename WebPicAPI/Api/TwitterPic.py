
from ..ApiManager import TwitterAPI
from ..Util import space2lowline
from ..Util.httpUtilities import downloadFile
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch
from .ArtistInfo import ArtistInfo
import urllib.parse
import ntpath
import os


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
                downloadFile(url+":orig", path+name)
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
    

