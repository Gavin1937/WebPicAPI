
from ..Util.httpUtilities import randDelay, getSrcStr, downloadFile
from .WebPic import WebPic
from .types import WebPicType, ParentChild, WebPicTypeMatch, WebPicType2DomainStr, DomainStr2WebPicType
from .ArtistInfo import ArtistInfo
from .helperFunctions import findFirstNonNum
import urllib.parse
import ntpath
import json
import os



class YanderePic(WebPic):
    """handle artist identifications & downloading for yande.re"""
    
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
        super(YanderePic, self).__init__(url)
        # input url is not a yandere url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.YANDERE) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"yande.re\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self) -> None:
        super(YanderePic, self).clear()
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
        cur = self.getUrl().find("/post/show/")
        
        # determine ParentChild status
        if cur != -1: # found pattern
            self.__parent_child = ParentChild.CHILD
        elif "/post" in self.getUrl() or "/pool" in self.getUrl():
            self.__parent_child = ParentChild.PARENT
        else:
            self.__parent_child = ParentChild.UNKNOWN
        
        # get url source
        randDelay(1.0, 2.5)
        src = getSrcStr(self.getUrl())
        
        # get json data
        j_dict = {}
        tmp_str = "["
        cur = 0
        while cur != -1:
            cur = src.find("Post.register", cur)
            if cur == -1:
                break
            cur = src.find('(', cur) + 1
            tmp_str += src[cur:src.find('\n', cur)]
            tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
        if len(tmp_str) > 1:
            tmp_str = tmp_str[:-1] + ']'
            j_dict = json.loads(tmp_str)
        else: # bad url
            raise ValueError(f"Cannot process url: {self.getUrl()}")
        
        # whether has artist
        tmp_str = ""
        tmp_dict = {}
        if "tags" in j_dict[0]:
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        # found artist name
        for k, v in tmp_dict.items():
            if v == "artist":
                tmp_str = k
                break
        # get artist info
        if len(tmp_str) > 0:
            # generate artist wiki page
            tmp_str = "https://" + WebPicType2DomainStr(WebPicType.YANDERE) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url.append(j_dict[0]["posts"][0]["file_url"])
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url[-1])
            parse2 = ntpath.split(parse1.path)
            self.__filename.append(parse2[1])
            
            # finding src_url
            tmp_str = str(j_dict[0]["posts"][0]["source"])
            parse1 = urllib.parse.urlparse(tmp_str)
            if DomainStr2WebPicType(parse1.netloc) == WebPicType.PIXIV:
                # use pixiv id for pixiv source
                # handle new url
                cur = tmp_str.find("pixiv.net/artworks/")
                if cur != -1: 
                    self.__src_url = tmp_str
                # handle new url with /en/
                cur = tmp_str.find("pixiv.net/en/artworks/")
                if cur != -1:
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle old page url
                cur = tmp_str.find("illust_id=")
                if cur != -1: 
                    cur += 10
                    loc_cur = cur
                    for i in range(len(tmp_str)-cur):
                        loc_cur += i
                        if loc_cur >= len(tmp_str) or tmp_str[loc_cur].isalpha():
                            break
                    pid = tmp_str[cur:loc_cur]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                # handle raw img url
                cur = tmp_str.find("pximg.net")
                if cur != -1: 
                    parse2 = ntpath.split(parse1.path)
                    pid = parse2[1]
                    pid = pid[:pid.find('_')]
                    self.__src_url = "https://www.pixiv.net/artworks/" + pid
                pass
            elif len(parse1.netloc) > 0: # twitter and other
                self.__src_url = tmp_str
        
        # get tags
        tmp_dict = {}
        if self.isChild():
            tmp_dict = j_dict[0]["tags"]
        elif self.isParent():
            tmp_dict = j_dict[0]
        for k, v in tmp_dict.items():
            self.__tags.append(k)
    
    
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
        
        counter = 0
        page_count = 1
        last_post_id = 0
        output = []
        while counter != max_num:
            # generate loc_url
            loc_url = url.replace("page=#", f"page={page_count}")
            page_count += 1
            
            # get url source
            randDelay(1.0, 2.5)
            src = getSrcStr(loc_url)
            
            # get json data
            j_dict = {}
            tmp_str = "["
            cur = 0
            # ignore bad url from pool
            if "/pool" in self.getUrl() and "var thumb = $(\"hover-thumb\");" in src:
                return 
            while cur != -1:
                cur = src.find("Post.register", cur)
                if cur == -1:
                    break
                cur = src.find('(', cur) + 1
                tmp_str += src[cur:src.find('\n', cur)]
                tmp_str = tmp_str[:tmp_str.rfind(')')] + ','
            if len(tmp_str) > 1:
                tmp_str = tmp_str[:-1] + ']'
                j_dict = json.loads(tmp_str)
            else: # bad url
                return []
            
            # make sure we didn't reaches end of pages
            if "/post" in loc_url and len(j_dict[0]) == 0:
                break # reaches end of page
            elif "/pool/" in loc_url and j_dict[0]["posts"] == None:
                break # reaches end of page
            elif "/pool/" in loc_url:
                for item in j_dict[0]["posts"]:
                    if last_post_id == item["id"]:
                        return output
            
            # find post id from j_dict & build post url w/ it
            if len(j_dict) == 1 and "/pool/" in loc_url: # current parent is like "/pool/show/"
                for item in j_dict[0]["posts"]:
                    post_id = str(item["id"])
                    output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
                    counter += 1
                    last_post_id = item["id"]
                    if counter == max_num:
                        return output
            elif len(j_dict) > 1 and "/post" in loc_url: # current parent is like "/post?tags="
                for item in j_dict[1:]:
                    post_id = str(item["id"])
                    output.append("https://"+WebPicType2DomainStr(WebPicType.YANDERE)+"/post/show/"+post_id)
                    counter += 1
                    last_post_id = item["id"]
                    if counter == max_num:
                        return output
            if counter == max_num:
                return output
        
        return output
    

