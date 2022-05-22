
from ..ApiManager import PixivAPI
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch
from .ArtistInfo import ArtistInfo
from .helperFunctions import findFirstNonNum, space2lowline
import os
import urllib.parse
import ntpath


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
        self.__api: PixivAPI = PixivAPI.instance()
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
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
            parse2 = ntpath.split(parse1.path)
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
            raise ValueError(f"Cannot determine parent child state base on url: {self.getUrl()}")
        if "error" in j_dict:
            raise ValueError(f"Bad url: {self.getUrl()}")
        elif self.isChild() and j_dict["illust"]["visible"] == False:
            raise ValueError(f"Bad url: {self.getUrl()}")
        
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
                path = ""
                if os.path.isdir(dest_filepath): # dest_filepath is all path without filename
                    path = dest_filepath
                else: # dest_filepath is a path to file or is invalid
                    # assume dest_filepath is a path to file
                    path, name = ntpath.split(dest_filepath)
                    if not os.path.isdir(path): # not specify path, assume dest_filepath is filename
                        path = os.path.curdir
                if path[-1] != '/' or path[-1] != '\\':
                    path += '/'
                self.__api.downloadIllust(url=url, path=path)
    
    def getChildrenUrls(self, max_num: int = 30) -> list:
        """Get all children urls of a parent until reaches max_num. Input -1 means get all children urls without limit"""
        
        # only process if current obj is parent
        if not self.isParent():
            return []
        
        # get user illustration list
        tmp_str = self.__artist_info.getUrl_pixiv()[0]
        pid = int(tmp_str[tmp_str.rfind('/')+1:])
        
        # get all illustrations of this user
        j_list = self.__api.getUserIllustList(pid, max_num)
        counter = 0
        output = []
        
        # generate artwork urls
        for item in j_list:
            output.append("https://pixiv.net/artworks/"+str(item["id"]))
        
        return output
    

