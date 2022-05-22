
from ..ApiManager import EHentaiAPI, isValidUrl
from ..Util.httpUtilities import randDelay, downloadFile
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch
from .ArtistInfo import ArtistInfo
import urllib.parse
import ntpath
import json
import os



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
                    # store json list of artist names for ArtistInfo
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
                downloadFile(url, path+name)
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
    

