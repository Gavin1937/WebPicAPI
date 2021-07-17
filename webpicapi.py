

# public functions

def getUrlSource(url) -> str:
    """get url source as string"""
    
    from urllib3 import PoolManager
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data

def downloadUrl(url, dest_filepath = None):
    """download url to dest_filepath"""
    
    from os import getcwd
    dir = getcwd()
    filename = ""
    
    # use original filename in url if user did not provide one in dest_filepath
    import ntpath
    if dest_filepath == None:
        from urllib.parse import urlparse
        p = urlparse(url)
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
    from urllib3 import PoolManager
    resp = PoolManager().request("GET", url)
    file = open(dir+'/'+filename, "wb")
    file.write(resp.data)
    file.close()

class WebPic:
    """Online Picture/Wallpaper website template class"""
    
    # private variables
    __url: str = ""
    
    # constructor
    def __init__(self, url: str):
        self.__url = url
    
    # public methods
    def getUrl(self):
        return self.__url


class DanbooruPic(WebPic):
    """handle artist identifications & downloading for danbooru"""
    
    __file_url: str = ""
    __has_artist_flag: bool = False
    __artist_name: str = ""
    
    def __init__(self, url: str):
        super().__init__(url)
    
    def hasArtist(self) -> bool:
        return self.__has_artist_flag
    
    def getArtistName(self) -> str:
        return self.__artist_name
    
    def downloadPic(self, dest_filepath):
        downloadUrl(self.__file_url, dest_filepath)
    
    def __analyzeUrl(self):
        pass
