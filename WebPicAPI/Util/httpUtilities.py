
#######################################################################################
#                                                                                     #
#   Utilities associate with http request                                             #
#   Including get url source/content and download                                     #
#   Requires Python 3.8 or above                                                      #
#   GitHub Gist: https://gist.github.com/Gavin1937/73dff133906a14be632aa63b2f946f82   #
#                                                                                     #
#######################################################################################

# public variable for http request
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36',
    'Connection': 'keep-alive',
    'Refer': 'https://www.google.com'
}

from time import sleep
from random import uniform
import requests
from urllib.parse import urlparse
from ntpath import basename
from typing import Union
from pathlib import Path


def pathCvt(p:Union[str,Path]) -> Path:
    if type(p) is str:
        return Path(p)
    return p

def randDelay(min:float, max:float) -> None:
    n = uniform(min, max)
    sleep(round(n, 2))

def getSrc(url:str) -> Union[str,bytes]:
    resp = requests.get(url=url, headers=HEADERS)
    return resp.content

def getSrcStr(url:str) -> str:
    resp = requests.get(url=url, headers=HEADERS)
    return resp.content.decode('utf-8')

def getSrcJson(url:str) -> Union[dict,list]:
    resp = requests.get(url=url, headers=HEADERS)
    return resp.json()

def writeStr2File(data:str, filepath:Union[str,Path], encoding="ascii") -> None:
    filepath = pathCvt(filepath)
    with open(filepath, 'w', encoding=encoding) as file:
        file.write(data)

def writeBytes2File(data:bytes, filepath:Union[str,Path]) -> None:
    filepath = pathCvt(filepath)
    with open(filepath, 'wb') as file:
        file.write(data)

def downloadFile(url:str, filepath:Union[str,Path], overwrite:bool=False) -> bool:
    """
        Download File from input url and save it to input filepath\n
        \n
        :Param:\n
            url      => string url to a file to download\n
            filepath => string or Path of where to save downloaded file\n
                        if filepath is a directory, save file with its default name under that directory\n
                        if filepath is a file and,\n
                            if filepath does not exists, save file with input filename\n
                            if filepath exists and overwrite == True, save file with input filename\n
                            if filepath exists and overwrite == False, return False\n
                        if filepath is invalid, raise ValueError\n
            overwrite => boolean flag, whether overwrite file when duplication happens\n
        \n
        :Return:\n
            return True if success, otherwise return False\n
    """
    
    filepath = pathCvt(filepath)
    data = getSrc(url)
    
    # filepath exists, duplicate file
    if filepath.exists() and filepath.is_file():
        if overwrite:
            writeBytes2File(data, filepath)
        else:
            return False
    
    # filepath exists, and it is dir
    elif filepath.exists() and filepath.is_dir():
        # assume filepath is parent dir and use filename in url path
        filename = basename(urlparse(url).path)
        writeBytes2File(data, filepath/filename)
    
    # filepath not exists & its parent exists
    elif not filepath.exists() and filepath.parent.exists():
        # assume filepath is a file that haven't been create
        writeBytes2File(data, filepath)
    
    # filepath not exists & its parent not exists
    else:
        raise ValueError("Invalid filepath.")
    
    return True

