#! /bin/python3

# ##################################################################
# 
# Testing and Demonstration file for WebPicAPI
# 
# Author: Gavin1937
# GitHub: https://github.com/Gavin1937/WebPicAPI
# 
# ##################################################################


from webpicapi import *

# URLs for testing
parent_urls = [
    # PIXIV
    "https://www.pixiv.net/users/163536",
    
    # TWITTER
    "https://twitter.com/WhiteHouse",
    
    # DANBOORU
    "https://danbooru.donmai.us/posts?tags=fate_%28series%29",
    
    # YANDERE
    "https://yande.re/pool/show/97999",
    
    # KONACHAN
    "https://konachan.com/post",
    
    # WEIBO
    "https://m.weibo.cn/u/1833651020",
    
    # EHENTAI
    "https://e-hentai.org/tag/parody:azur+lane"
]
child_urls = [
    # PIXIV
    "https://www.pixiv.net/artworks/92066353",
    
    # TWITTER
    "https://twitter.com/MySportsUpdate/status/1428422991269044227",
    
    # DANBOORU
    "https://danbooru.donmai.us/posts/4717214",
    
    # YANDERE
    "https://yande.re/post/show/835239",
    
    # KONACHAN
    "https://konachan.com/post/show/330626/azur_lane-japanese_clothes-shoukaku_-azur_lane-yos",

    # WEIBO
    "https://m.weibo.cn/detail/4669008060350870",
    
    # EHENTAI
    "https://e-hentai.org/s/75f5ee2ecb/1988870-1"
]


print("Printing WebPic Object Info...")

for idx, (parent, child) in enumerate(zip(parent_urls, child_urls)):
    print(f"\n\nidx = {idx}")
    
    try:
        # get WebPic objects for parent
        p_obj = url2WebPic(parent)
        
        # print basic info of parent
        print("Parent Info")
        printInfo(p_obj)
        
        # clear WebPic objects
        p_obj.clear()
        
        # get WebPic objects for child
        c_obj = url2WebPic(child)
        
        # print basic info for child
        print("Child Info")
        printInfo(c_obj)
        
        # clear WebPic objects
        c_obj.clear()
    except Exception as err:
        print(err)
