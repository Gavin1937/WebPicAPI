

# libs
from urllib3 import PoolManager
import os
import ntpath
import urllib.parse
import json
from enum import IntEnum


# public functions

def getUrlSource(url) -> str:
    """get url source as string"""
    
    if len(url) <= 0:
        return
    
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data

def downloadUrl(url, dest_filepath = None):
    """download url to dest_filepath"""
    
    if len(url) <= 0:
        return
    
    dir = os.getcwd()
    filename = ""
    
    # use original filename in url if user did not provide one in dest_filepath
    if dest_filepath == None:
        p = urllib.parse.urlparse(url)
        u_dir, u_filename = ntpath.split(p.path)
        filename = u_filename
    # user provided dest_filepath
    else:
        tmp_dir,tmp_filename = ntpath.split(dest_filepath)
        # only continue if dest_filepath is a valid filepath (w/ complete dir & filename)
        if len(tmp_filename) > 0 and len(tmp_dir) > 0:
            dir = tmp_dir
            filename = tmp_filename
    
    # download file
    resp = PoolManager().request("GET", url)
    file = open(dir+'/'+filename, "wb")
    file.write(resp.data)
    file.close()


# WebPicType const Table
# Bit Table:
# 0b     1         1       1       1         1         1         1       1
#     Unknown  e-hentai  weibo  konachan  yande.re  danbooru  twitter  pixiv
class WebPicType(IntEnum):
    """Type of different picture/wallpaper websites"""
    PIXIV    = 1,   # 0b00000001
    TWITTER  = 2,   # 0b00000010
    DANBOORU = 4,   # 0b00000100
    YANDERE  = 8,   # 0b00001000
    KONACHAN = 16,  # 0b00010000
    WEIBO    = 32,  # 0b00100000
    EHENTAI  = 64,  # 0b01000000
    UNKNOWN  = 128  # 0b10000000

class ParentChild(IntEnum):
    """Whether a web page is parent, child, or unknown"""
    UNKNOWN = 0,
    PARENT = 1,
    CHILD = 2

def WebPicType2Str(webpic_type: WebPicType) -> str:
    """Convert WebPicType to String"""
    if webpic_type == WebPicType.PIXIV:
        return "pixiv"
    elif webpic_type == WebPicType.TWITTER:
        return "twitter"
    elif webpic_type == WebPicType.DANBOORU:
        return "danbooru"
    elif webpic_type == WebPicType.YANDERE:
        return "yandere"
    elif webpic_type == WebPicType.KONACHAN:
        return "konachan"
    elif webpic_type == WebPicType.WEIBO:
        return "weibo"
    elif webpic_type == WebPicType.EHENTAI:
        return "e-hentai"
    else: # Unknown
        return None

def Str2WebPicType(webpic_type_str: str) -> WebPicType:
    """Convert String to WebPicType"""
    if webpic_type_str == "pixiv":
        return WebPicType.PIXIV
    elif webpic_type_str == "twitter":
        return WebPicType.TWITTER
    elif webpic_type_str == "danbooru":
        return WebPicType.DANBOORU
    elif webpic_type_str == "yandere":
        return WebPicType.YANDERE
    elif webpic_type_str == "konachan":
        return WebPicType.KONACHAN
    elif webpic_type_str == "weibo":
        return WebPicType.WEIBO
    elif webpic_type_str == "e-hentai":
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicType2DomainStr(webpic_type: WebPicType) -> str:
    """Convert DomainStr to WebPicType"""
    if webpic_type == WebPicType.PIXIV:
        return "www.pixiv.net"
    elif webpic_type == WebPicType.TWITTER:
        return "www.twitter.com"
    elif webpic_type == WebPicType.DANBOORU:
        return "danbooru.donmai.us"
    elif webpic_type == WebPicType.YANDERE:
        return "yande.re"
    elif webpic_type == WebPicType.KONACHAN:
        return "konachan.com"
    elif webpic_type == WebPicType.WEIBO:
        return "weibo.com"
    elif webpic_type == WebPicType.EHENTAI:
        return "e-hentai.org"
    else: # Unknown
        return None

def DomainStr2WebPicType(domain_str: str) -> WebPicType:
    """Convert DomainStr to WebPicType"""
    if "www.pixiv.net" in domain_str or "pximg.net" in domain_str:
        return WebPicType.PIXIV
    elif "twitter.com" in domain_str or "twimg.com" in domain_str:
        return WebPicType.TWITTER
    elif "danbooru.donmai.us" in domain_str:
        return WebPicType.DANBOORU
    elif "yande.re" in domain_str:
        return WebPicType.YANDERE
    elif "konachan.com" in domain_str:
        return WebPicType.KONACHAN
    elif "weibo.com" in domain_str:
        return WebPicType.WEIBO
    elif "e-hentai.org" in domain_str:
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicTypeMatch(src_type: WebPicType, dest_type) -> bool:
    """Check wether src_type is same as dest_type"""
    # handle String dest_type
    loc_dest_type = WebPicType.UNKNOWN
    if type(dest_type) == str:
        loc_dest_type = Str2WebPicType(dest_type)
    else: # dest_type is WebPicType
        loc_dest_type = dest_type
    return bool(src_type == loc_dest_type)


class ArtistInfo:
    """Process & Hold Artist Information"""
    
    # private variables
    __artist_names: list = []
    __pixiv_urls: list = []
    __twitter_urls: list = []
    
    # constructor
    def __init__(self, webpic_type: WebPicType, url: str):
        if webpic_type == WebPicType.PIXIV:
            self.__analyzeInfo_pixiv(url)
        elif webpic_type == WebPicType.TWITTER:
            self.__analyzeInfo_twitter(url)
        elif webpic_type == WebPicType.DANBOORU:
            self.__analyzeInfo_danbooru(url)
        elif webpic_type == WebPicType.YANDERE:
            self.__analyzeInfo_yandere(url)
        elif webpic_type == WebPicType.KONACHAN:
            self.__analyzeInfo_konachan(url)
        elif webpic_type == WebPicType.WEIBO:
            self.__analyzeInfo_weibo(url)
        elif webpic_type == WebPicType.EHENTAI:
            self.__analyzeInfo_ehentai(url)
        else: # Unknown
            return None
    
    # clear obj
    def clear(self):
        self.__artist_names.clear()
        self.__pixiv_urls.clear()
        self.__twitter_urls.clear()
    
    # getters
    def getArtistNames(self) -> list:
        return self.__artist_names
        
    def getUrl_pixiv(self) -> list:
        return self.__pixiv_urls
    
    def getUrl_twitter(self) -> list:
        return self.__twitter_urls
    
    # helper functions
    def __analyzeInfo_pixiv(self, url):
        pass
    
    def __analyzeInfo_twitter(self, url):
        pass
    
    def __analyzeInfo_danbooru(self, url: str):
        cur = 0
        
        # get url source
        src = getUrlSource(url)
        
        # finding artist names
        cur = src.find("Other Names")
        if cur != -1:
            names_src = src[cur:src.find("/li", cur)]
            cur = 0
            while cur != -1:
                cur = names_src.find("artist-other-name", cur)
                if cur == -1:
                    break
                cur = names_src.find("any_name_matches%5D=", cur) + 20
                tmp_str = names_src[cur:names_src.find('\"', cur)]
                self.__artist_names.append(urllib.parse.unquote(tmp_str))
                cur += 3
        else:
            cur = src.find("og:title\" content=\"") + 19
            self.__artist_names.append(src[cur:src.find(" | Artist Profile", cur)])
        
        # finding pixiv & twitter url
        tmp_url = ""
        had_pixiv = False
        had_twitter = False
        cur = src.find("list-bulleted")
        url_src = src[cur:src.find("/ul", cur)]
        cur = 0
        while cur != -1:
            cur = url_src.find("href=\"", cur)
            if cur == -1:
                break
            cur += 6
            tmp_url = url_src[cur:url_src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
    
    def __analyzeInfo_yandere(self, url: str):
        # get 1st name from url
        tmp_name = url[url.find("title=")+6:]
        self.__artist_names.append(urllib.parse.unquote(tmp_name))
        
        # get wiki page source
        src = getUrlSource(url)
        
        # get urls
        cur = 0
        tmp_url = ""
        while cur != -1:
            cur = src.find("<th>URL</th>", cur)
            if cur == -1:
                break
            cur = src.find("href=\"", cur) + 6
            tmp_url = src[cur:src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
                
        # get artist names
        cur = src.find("<th>Aliases</th>")
        tmp_str = src[cur:src.find("</tr>", cur)]
        cur = 0
        while cur != -1:
            cur = tmp_str.find("/wiki/show?title=", cur)
            if cur == -1:
                break
            cur += 17
            self.__artist_names.append(
                urllib.parse.unquote(tmp_str[cur:tmp_str.find('\"', cur)])
            )
    
    def __analyzeInfo_konachan(self, url):
        # get 1st name from url
        tmp_name = url[url.find("title=")+6:]
        self.__artist_names.append(urllib.parse.unquote(tmp_name))
        
        # get wiki page source
        src = getUrlSource(url)
        
        # get urls
        cur = 0
        tmp_url = ""
        while cur != -1:
            cur = src.find("<th>URL</th>", cur)
            if cur == -1:
                break
            cur = src.find("href=\"", cur) + 6
            tmp_url = src[cur:src.find('\"', cur)]
            # checking url
            if ("pixiv.net/member.php?id=" in tmp_url or
                "pixiv.net/users/" in tmp_url):
                self.__pixiv_urls.append(tmp_url)
            elif "twitter.com/" in tmp_url:
                tmp_str = tmp_url[tmp_url.find("twitter.com/")+12:]
                if '/' not in tmp_str and '?' not in tmp_str:
                    self.__twitter_urls.append(tmp_url)
                
        # get artist names
        cur = src.find("<th>Aliases</th>")
        tmp_str = src[cur:src.find("</tr>", cur)]
        cur = 0
        while cur != -1:
            cur = tmp_str.find("/wiki/show?title=", cur)
            if cur == -1:
                break
            cur += 17
            self.__artist_names.append(
                urllib.parse.unquote(tmp_str[cur:tmp_str.find('\"', cur)])
            )

    
    def __analyzeInfo_weibo(self, url):
        pass
    
    def __analyzeInfo_ehentai(self, url):
        pass
    


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
    def clear(self):
        self.__url = 0
        self.__webpic_type = WebPicType.UNKNOWN
    
    # public methods
    def getUrl(self) -> str:
        return self.__url
    
    def getWebPicType(self) -> WebPicType:
        return self.__webpic_type


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
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
    def clear(self):
        super(DanbooruPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            tmp_url = WebPicType2DomainStr(self.getWebPicType()) + tmp_url
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_url)
        
        # finding file_url & filename
        cur = src.find("post-info-size")
        if cur != -1: # found file_url
            cur = src.find("href=\"", cur) + 6
            # set file url
            self.__file_url = src[cur:src.find('\"', cur)]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
        
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)


class YanderePic(WebPic):
    """handle artist identifications & downloading for yande.re"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(YanderePic, self).__init__(url)
        # input url is not a danbooru url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.YANDERE) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"yande.re\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self):
        super(YanderePic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            return
        
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
            tmp_str = WebPicType2DomainStr(WebPicType.YANDERE) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url = j_dict[0]["posts"][0]["file_url"]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
            
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
                        if tmp_str[loc_cur].isalpha():
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)


class KonachanPic(WebPic):
    """handle artist identifications & downloading for konachan"""
    
    # private variables
    __parent_child: ParentChild = ParentChild.UNKNOWN
    __file_url: str = ""
    __filename: str = ""
    __src_url: str = ""
    __has_artist_flag: bool = False
    __artist_info: ArtistInfo = None
    __tags: list = []
    
    # constructor
    def __init__(self, url: str, super_class: WebPic = None):
        super(KonachanPic, self).__init__(url)
        # input url is not a danbooru url
        if WebPicTypeMatch(self.getWebPicType(), WebPicType.KONACHAN) == False:
            raise ValueError("Wrong url input. Input url must be under domain of \"konachan\".")
        self.__analyzeUrl()
    
    # clear obj
    def clear(self):
        super(KonachanPic, self).clear()
        self.__parent_child = ParentChild.UNKNOWN
        self.__file_url = 0
        self.__filename = 0
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
        src = getUrlSource(self.getUrl())
        
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
            return
        
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
            tmp_str = WebPicType2DomainStr(WebPicType.KONACHAN) + "/wiki/show?title=" + tmp_str
            # has artist
            self.__has_artist_flag = True
            # initialize ArtistInfo
            self.__artist_info = ArtistInfo(self.getWebPicType(), tmp_str)
        
        if self.isChild():
            # finding file_url & filename
            
            # set file url
            self.__file_url = j_dict[0]["posts"][0]["file_url"]
            # set filename
            parse1 = urllib.parse.urlparse(self.__file_url)
            parse2 = ntpath.split(parse1.path)
            self.__filename = parse2[1]
            
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
                        if tmp_str[loc_cur].isalpha():
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
    
    def downloadPic(self, dest_filepath = None):
        downloadUrl(self.__file_url, dest_filepath)

