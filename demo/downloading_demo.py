#! /bin/python3

#########################################################
#                                                       #
#   Testing and Demonstrating accessors for WebPicAPI   #
#                                                       #
#   Author: Gavin1937                                   #
#   GitHub: https://github.com/Gavin1937/WebPicAPI      #
#                                                       #
#########################################################


# set path to parent in order to import WebPicAPI
import sys
sys.path.append('..')

from WebPicAPI import url2WebPic, DomainStr2WebPicType, WebPicType
from example_urls import *
from pathlib import Path


if __name__ == "__main__":
    
    download = Path('./test/download/')
    if download.exists() == False:
        download.mkdir()
    
    print("Downloading Child WebPic...")
    
    for idx, url in enumerate(child_urls):
        print(f"\n\nidx = {idx}")
        
        try:
            # get WebPic child objects from url
            child = url2WebPic(url)
            print(f"downloading: {child.getUrl()}")
            
            # download, you can input str path as well
            child.downloadFile(download)
        except Exception as err:
            print(err)
    
    print("Downloading children from Parent WebPic")
    
    for idx, url in enumerate(parent_urls):
        print(f"\n\nidx = {idx}")
        
        try:
            # get WebPic objects from url
            parent = url2WebPic(url)
            print(f"downloading children from: {parent.getUrl()}")
            
            # loop through first 5 pictures of parent obj
            for child_url in parent.getChildrenUrls(5):
                # you can initialize child with parent's ArtistInfo
                # this will save a lot of time in children initialization
                child = url2WebPic(url, parent.getArtistInfo())
                print(f"downloading: {child.getUrl()}")
                
                # download
                child.downloadFile('./test/download/')
        except Exception as err:
            print(err)
    
