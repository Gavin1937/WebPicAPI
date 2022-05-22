
from .Singleton import Singleton
from .OtherUtil import *
from ..Util import HEADERS, randDelay, getSrcStr
import json
from bs4 import BeautifulSoup
import urllib.parse
import requests


@Singleton
class EHentaiAPI:
    """Singleton class to request from e-hentai.org"""
    
    # private members
    __api_url: str = "https://api.e-hentai.org/api.php"
    __min_delay: float = 5.0
    __max_delay: float = 7.5
    
    # api features
    def searchKeyword(self, keyword: str, max_galleries: int) -> list:
        """Search specific gallery or tag with keyword in E-Hentai, return list of galleries"""
        if keyword is None or len(keyword) <= 0 or max_galleries <= 0:
            return None
        
        search_url = "https://e-hentai.org/?f_search=" + urllib.parse.quote(keyword)
        return self.getGalleriesFromSearch(search_url, max_galleries=max_galleries)
    
    def getGalleryInfo(self, url: str) -> dict:
        """Get basic Gallery Info via E-Hentai API, return json as dict."""
        if not self.isValidGallery(url):
            return None
        
        tmp_dict = self.__getGalleryIdentities(url)
        param = {
            "method": "gdata",
            "gidlist": [
                [tmp_dict["gallery_id"], tmp_dict["gallery_token"]]
            ],
            "namespace": 1
        }
        randDelay(self.__min_delay, self.__max_delay)
        resp = requests.post(url=self.__api_url, json=param, headers=HEADERS)
        return json.loads(resp.text)
    
    def findParentGallery(self, url: str) -> dict:
        """Find parent Gallery Identities (gallery_id & gallery_token) with a picture url."""
        if not self.isValidPicture(url):
            return None
        
        tmp_dict = self.__getPictureIdentities(url)
        param = {
            "method": "gtoken",
            "pagelist": [
                [tmp_dict["gallery_id"], tmp_dict["page_token"], tmp_dict["pagenumber"]]
            ]
        }
        randDelay(self.__min_delay, self.__max_delay)
        resp = requests.post(url=self.__api_url, json=param, headers=HEADERS)
        return json.loads(resp.text)
    
    def findParentGalleryUrl(self, url: str) -> str:
        """Find parent Gallery url with a Picture url."""
        if not self.isValidPicture(url):
            return None
        
        tmp_dict = self.findParentGallery(url)["tokenlist"][0]
        return f"https://e-hentai.org/g/{tmp_dict['gid']}/{tmp_dict['token']}/"
    
    def getPicUrl(self, url: str) -> str:
        """Get picture file url from a picture url. (https://e-hentai.org/s/{page_token}/{gallery_id}-{pagenumber}"""
        if not self.isValidPicture(url):
            return None
        
        soup = BeautifulSoup(self.__reqGet(url=url), 'lxml')
        return self.__picUrlFromHTML(soup=soup)
    
    def getPicsInGallery(self, url: str, max_pics: int) -> list:
        """Get url of pictures from a gallery url. (https://e-hentai.org/g/{gallery_id}/{gallery_token}/"""
        if not self.isValidGallery(url) or max_pics <= 0:
            return None
        
        # get gallery info via api
        j_dict = self.getGalleryInfo(url)
        
        # get total page of this gallery
        # assuming each page has 40 img (default setting)
        total_files = int(j_dict["gmetadata"][0]["filecount"])
        # add an extra page if "tmp" has decimal value
        tmp: float = float(total_files / 40.0)
        total_pages = int(tmp + 1) if ((tmp-int(tmp)) > 0) else int(tmp)
        pic_counter = 0
        output = []
        
        for i in range(total_pages):
            # get page src
            page_url = url + f"?p={i}"
            soup = BeautifulSoup(self.__reqGet(page_url), "lxml")
            divs = soup.find_all(class_ = "gdtm")
            
            # get img src
            for div in divs:
                loc_url = div.a.get("href")
                if loc_url != None:
                    output.append(loc_url)
                    pic_counter += 1
                    if pic_counter >= max_pics:
                        return output
        return output
    
    def getGalleriesFromSearch(self, url: str, max_galleries: int) -> list:
        """Get Galleries from an E-Hentai search url or any E-Hentai pages without /g/ or /s/ until reaches max_galleries."""
        if self.isValidGallery(url) or self.isValidPicture(url) or max_galleries <= 0:
            return None
        
        # setup vars
        output = []
        page_count = 0
        gallery_count = 0
        # extra pure url with search keyword
        parse = urllib.parse.urlparse(url)
        cur1 = parse.query.find("f_search=")
        cur2 = parse.query.find('&', cur1+9)
        if cur2 == -1: # no other query specified
            base_url = parse.scheme+"://" + parse.netloc + parse.path + '?'+parse.query[cur1:]
        else: # has other query, ignore them
            base_url = parse.scheme+"://" + parse.netloc + parse.path + '?'+parse.query[cur1:cur2]
        
        while gallery_count < max_galleries:
            # generate search url
            search_url = base_url + f"&page={page_count}"
            
            # make request
            src = self.__reqGet(search_url)
            
            # parse html
            soup = BeautifulSoup(src, 'lxml')
            
            # get all galleries in current page
            galleries = soup.find_all(class_="gl3c glname")
            
            for gallery in galleries:
                gallery_count += 1
                output.append(gallery.a.get("href"))
                if gallery_count >= max_galleries:
                    break
        return output
    
    
    # booleans
    def isValidEHentai(self, url: str) -> bool:
        """Is Url a valid e-hentai url"""
        if isValidUrl(url) and "e-hentai.org" in url:
            return True
        else: return False
    
    def isValidGallery(self, url: str) -> bool:
        """Is Url a valid Gallery?"""
        if self.isValidEHentai(url) and "/g/" in url:
            return True
        else: return False
    
    def isValidPicture(self, url: str) -> bool:
        """Is Url a valid Picture?"""
        if self.isValidEHentai(url) and "/s/" in url and url[-1] != '/':
            return True
        else: return False
    
    def isValidSearchPage(self, url: str) -> bool:
        """Is Url a valid e-hentai page w/ multiple galleries"""
        if (self.isValidEHentai(url) and
            not self.isValidGallery(url) and
            not self.isValidPicture(url)
            ):
            return True
        else: return False
    
    
    # getters
    def getAPIUrl(self) -> str:
        return self.__api_url
    
    def getMinDelay(self) -> float:
        return self.__min_delay
    
    def getMaxDelay(self) -> float:
        return self.__max_delay
    
    
    # setters
    def setMinDelay(self, delay: float) -> None:
        """Set self.__min_delay for request"""
        self.__min_delay = round(float(delay), 2)
    
    def setMaxDelay(self, delay: float) -> None:
        """Set self.__max_delay for request"""
        self.__max_delay = round(float(delay), 2)
    
    
    # helper functions
    def __reqGet(self, url: str) -> str:
        """Private HTTP request GET method, contains auto delay"""
        if not isValidUrl(url):
            return None
        
        randDelay(self.__min_delay, self.__max_delay)
        return getSrcStr(url)
    
    def __picUrlFromHTML(self, soup: BeautifulSoup) -> str:
        """Get url of a single picture from a picture url, input BeautifulSoup of a image page"""
        img = soup.find_all(id="img")
        return img[0]["src"]
    
    def __getGalleryIdentities(self, url: str) -> dict:
        """Get Identities of a Gallery url. (gallery_id & gallery_token), return dict of them."""
        if not self.isValidGallery(url):
            return None
        
        # get identities
        dirs = urllib.parse.urlparse(url).path.split('/')
        gallery_id = int(dirs[-3])
        gallery_token = dirs[-2]
        
        return {"gallery_id": gallery_id, "gallery_token": gallery_token}
    
    def __getPictureIdentities(self, url: str) -> dict:
        """Get Identities of a Picture url. (page_token, gallery_id, & pagenumber), return dict of them."""
        if not self.isValidPicture(url):
            return None
        
        # get identities
        dirs = urllib.parse.urlparse(url).path.split('/')
        last_part = dirs[-1].split('-')
        page_token = dirs[-2]
        gallery_id = int(last_part[0])
        pagenumber = int(last_part[1])
        
        return {"page_token": page_token, "gallery_id": gallery_id, "pagenumber": pagenumber}
    

