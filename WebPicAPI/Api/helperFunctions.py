
from .types import WebPicType, DomainStr2WebPicType


def findFirstNonNum(s: str, start_idx: int = 0) -> int:
    """Find the first non numeric character of input string from start_idx, return index"""
    while start_idx < len(s):
        if not s[start_idx].isnumeric():
            return start_idx
        start_idx += 1
    return start_idx

def space2lowline(s: str) -> str:
    """Convert all spaces \' \' in input string to lowline \'_\' and return as a new string"""
    # l = str(s).split(' ')
    # output = ""
    # for i in l:
    #     output += i + '_'
    # return output[:-1]
    return s.replace(' ', '_')

def rmListDuplication(l: list) -> list:
    # output = []
    # for item in l:
    #     if item not in output:
    #         output.append(item)
    # return output
    return list(set(l))

def isEmptyWebPic(webpic: any) -> bool:
    return (
        len(webpic.getFileUrl()) == 0 and
        len(webpic.getFileName()) == 0 and
        webpic.getSrcUrl() == 0 and
        webpic.hasArtist() == False and
        len(webpic.getTags()) == 0
    )


def url2WebPic(url: str) -> any:
    """Get WebPic object from any supported url"""
    webpic_type = DomainStr2WebPicType(url)
    if webpic_type == WebPicType.PIXIV:
        from .PixivPic import PixivPic
        return PixivPic(url)
    elif webpic_type == WebPicType.TWITTER:
        from .TwitterPic import TwitterPic
        return TwitterPic(url)
    elif webpic_type == WebPicType.DANBOORU:
        from .DanbooruPic import DanbooruPic
        return DanbooruPic(url)
    elif webpic_type == WebPicType.YANDERE:
        from .YanderePic import YanderePic
        return YanderePic(url)
    elif webpic_type == WebPicType.KONACHAN:
        from .KonachanPic import KonachanPic
        return KonachanPic(url)
    elif webpic_type == WebPicType.WEIBO:
        from .WeiboPic import WeiboPic
        return WeiboPic(url)
    elif webpic_type == WebPicType.EHENTAI:
        from .EHentaiPic import EHentaiPic
        return EHentaiPic(url)
    else: # Unknown
        return None

def printInfo(webpic: any) -> None:
    """Printing all info of a supported WebPic"""
    try:
        if (webpic is None or
            DomainStr2WebPicType(webpic.getUrl()) == WebPicType.UNKNOWN or
            isEmptyWebPic(webpic)
            ):
            return
    except: # ignore if caught exceptions
        return
    
    print(f"{webpic.getUrl() = }")
    print(f"{webpic.getWebPicType() = }")
    print(f"{webpic.getParentChildStatus() = }")
    print(f"{webpic.getFileUrl() = }")
    print(f"{webpic.getFileName() = }")
    print(f"{webpic.getSrcUrl() = }")
    print(f"{webpic.hasArtist() = }")
    if webpic.hasArtist():
        print(f"{webpic.getArtistInfo().getArtistNames() = }")
        print(f"{webpic.getArtistInfo().getUrl_pixiv() = }")
        print(f"{webpic.getArtistInfo().getUrl_twitter() = }")
    print(f"{webpic.getTags() = }")

