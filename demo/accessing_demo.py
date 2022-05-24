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


# this function is copied from /WebPicAPI/Api/helperFunctions.py to here
# for demonstration, you can always import it from the package
# from WebPicAPI import printInfo
def printInfo(webpic: any) -> None:
    """Printing all info of a supported WebPic"""
    try:
        if (
            webpic is None or
            DomainStr2WebPicType(webpic.getUrl()) == WebPicType.UNKNOWN or
            webpic.isEmpty()
        ):
            return
    except: # ignore if caught exceptions
        return
    
    print(f"{webpic.getUrl() = }")
    print(f"{webpic.getWebPicType() = }")
    print(f"{webpic.getMinDelay() = }")
    print(f"{webpic.getMaxDelay() = }")
    print(f"{webpic.getFileUrl() = }")
    print(f"{webpic.getFileName() = }")
    print(f"{webpic.getSrcUrl() = }")
    print(f"{webpic.hasArtist() = }")
    if webpic.hasArtist():
        print(f"{webpic.getArtistInfo().getArtistNames() = }")
        print(f"{webpic.getArtistInfo().getUrl_pixiv() = }")
        print(f"{webpic.getArtistInfo().getUrl_twitter() = }")
    print(f"{webpic.getTags() = }")
    print(f"{webpic.isParent() = }")
    print(f"{webpic.isChild() = }")
    print(f"{webpic.isEmpty() = }")
    print(f"{webpic.getParentChildStatus() = }")
    
    print("clearing webpic...")
    webpic.clear()
    print(f"{webpic.isEmpty() = }")


if __name__ == "__main__":
    
    print("Printing WebPic Object Info...")
    
    for idx, (parent, child) in enumerate(zip(parent_urls, child_urls)):
        print(f"\n\nidx = {idx}")
        
        try:
            # get WebPic objects from url
            p_obj = url2WebPic(parent)
            
            # print basic info of parent
            print("Parent Info")
            printInfo(p_obj)
            
            # get WebPic objects from url
            c_obj = url2WebPic(child)
            
            # print basic info for child
            print("Child Info")
            printInfo(c_obj)
            
        except Exception as err:
            print(err)
