
from ..Util.httpUtilities import randDelay, getSrcStr, downloadFile, getSrcJson
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch, WebPicType2DomainStr
from .ArtistInfo import ArtistInfo
import urllib.parse
import ntpath
import os



class WeiboPic(WebPic):
    """handle artist identifications & downloading for weibo"""
    
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
        super(WeiboPic, self).__init__(url)
        # input url is not a konachan url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.WEIBO) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"weibo\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(WeiboPic, self).clear()
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
        
        # loc var
        url = self.getUrl()
        user_id = 0
        status_id = 0
        
        # determine domain type
        cur = url.find(WebPicType2DomainStr(WebPicType.WEIBO))
        
        if cur == -1:
            # input weibo url is "www.weibo.com" domain
            # assume input url is parent
            self.__parent_child = ParentChild.PARENT
            
            # get user_id
            randDelay(2.5, 5.0)
            src = getSrcStr(self.getUrl())
            cur = src.find("$CONFIG[\'oid\']=\'")
            if cur != -1:
                cur += 16
                user_id = int(src[cur:src.find("\'", cur)])
            
        else: # input weibo url is "m.weibo.cn"
            parse1 = urllib.parse.urlparse(url)
            parse2 = ntpath.split(parse1.path)
            
            # determine ParentChild status for "m.weibo.cn"
            if "/detail/" in url or "/status/" in url: # found pattern
                self.__parent_child = ParentChild.CHILD
                # set status_id
                status_id = int(parse2[1])
            elif "/u/" in url:
                self.__parent_child = ParentChild.PARENT
                # set user_id
                user_id = int(parse2[1])
            else:
                self.__parent_child = ParentChild.UNKNOWN
        
        # get json data
        j_dict = {}
        tmp_str = ""
        try:
            randDelay(2.5, 5.0)
            if self.__parent_child == ParentChild.PARENT:
                j_dict = getSrcJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&value={user_id}&containerid=100505{user_id}")
            elif self.__parent_child == ParentChild.CHILD:
                j_dict = getSrcJson(f"https://m.weibo.cn/statuses/show?id={status_id}")
            if j_dict["ok"] != 1:
                raise ValueError("Unable to fetch json data from weibo")
        except Exception as err:
            raise err
        
        if self.isParent():
                parse1 = urllib.parse.urlparse(self.getUrl())
                tmp_str = "https://" + parse1.netloc + parse1.path
                # has artist
                self.__has_artist_flag = True
                # initialize ArtistInfo
                self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        elif self.isChild():
            # whether has artist & get artistInfo
            if "user" in j_dict["data"]:
                # generate "m.weibo.cn" user url
                tmp_str = "https://m.weibo.cn/u/" + str(j_dict["data"]["user"]["id"])
                # has artist
                self.__has_artist_flag = True
                # initialize ArtistInfo
                self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
            
            # finding file_url & filename
            for pic in j_dict["data"]["pics"]:
                self.__file_url.append(pic["large"]["url"])
                parse1 = urllib.parse.urlparse(pic["large"]["url"])
                parse2 = ntpath.split(parse1.path)
                self.__filename.append(parse2[1])
            
            # assume weibo as a source, set src_url
            self.__src_url = "https://m.weibo.cn/status/" + j_dict["data"]["id"]
        
        # get tags
        if self.isParent():
            self.__tags.append(j_dict["data"]["userInfo"]["screen_name"])
        elif self.isChild():
            self.__tags.append(j_dict["data"]["user"]["screen_name"])
    
    
    # getters 
    def getFileUrl(self) -> str:
        return self.__file_url
    
    def getFileName(self) -> str:
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
        
        # loc var
        user_id = 0
        page_count = 1
        item_count = 0
        j_dict = {}
        output = []
        
        # get user_id
        parse1 = urllib.parse.urlparse(self.getUrl())
        parse2 = ntpath.split(parse1.path)
        user_id = int(parse2[1])
        
        # getting children urls
        while item_count < max_num:
            # get user timeline
            try:
                randDelay(2.5, 5.0)
                j_dict = getSrcJson(f"https://m.weibo.cn/api/container/getIndex?uid={user_id}&type=uid&page={page_count}&containerid=107603{user_id}")
                if j_dict["ok"] != 1:
                    break
            except Exception as err:
                raise err
            
            # record each status with image
            for status in j_dict["data"]["cards"]:
                if ("mblog" in status and
                    "pics" in status["mblog"] and
                    len(status["mblog"]["pics"]) > 0
                    ): # status has image
                    
                    output.append("https://m.weibo.cn/status/"+status["mblog"]["id"])
                    item_count += 1
                if item_count >= max_num:
                    break
            page_count += 1
        
        return output
    

