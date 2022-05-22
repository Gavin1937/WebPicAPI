
from enum import IntEnum


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
        return "ehentai"
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
    elif webpic_type_str == "ehentai":
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
        # we mainly support "m.weibo.cn"
        return "m.weibo.cn"
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
    elif "www.weibo.com" in domain_str or "weibo.com" in domain_str or "m.weibo.cn" in domain_str:
        return WebPicType.WEIBO
    elif "e-hentai.org" in domain_str:
        return WebPicType.EHENTAI
    else: # Unknown
        return WebPicType.UNKNOWN

def WebPicTypeMatch(src_type: WebPicType, dest_type: WebPicType) -> bool:
    """Check wether src_type is same as dest_type"""
    # handle String dest_type
    loc_dest_type = WebPicType.UNKNOWN
    if type(dest_type) == str:
        loc_dest_type = Str2WebPicType(dest_type)
    else: # dest_type is WebPicType
        loc_dest_type = dest_type
    return bool(src_type == loc_dest_type)

