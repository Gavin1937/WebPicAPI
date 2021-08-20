
# Web Picture Python3 API

### This API is design for fetching basic info and download pictures from popular picture/wallpaper websites.


# Python Version: Python 3.8.10


# Dependencies

| Dependency Name                                                  | Usage                     |
|------------------------------------------------------------------|---------------------------|
| [PixivPy](https://pypi.org/project/PixivPy/)                     | class PixivAPI            |
| [tweepy](https://pypi.org/project/tweepy/)                       | class TwitterAPI          |
| [requests](https://pypi.org/project/requests/)                   | for both PixivPy & tweepy |
| [requests-oauthlib](https://pypi.org/project/requests-oauthlib/) | for both PixivPy & tweepy |
| [BeautifulSoup](https://pypi.org/project/beautifulsoup4/)        | for parsing HTML          |
| [lxml](https://pypi.org/project/lxml/)                           | for parsing HTML          |

## Install all dependencies with:
```sh
pip install -r requirements.txt
``` 

# Requried API tokens

| Name                                                                                                  | Tutorials                                                                                                                                                                                            |
|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pixiv API: (code, access_token, refresh_token, and expires_in)                                        | [@ZipFile Pixiv OAuth Flow](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362) and [OAuth with Selenium/ChromeDriver](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde) |
| twitter API: (consumer_api_key, consumer_secret, bearer_token, access_token, and access_token_secret) | [Apply For Twitter API Account](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)                                                                 |

### If you are using [@ZipFile Pixiv OAuth Flow](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)'s method for pixiv API, you can use [pixiv_auth.py](./pixiv_auth.py) file in this repo. It's the same file with an additional function.


# Supported Websites:

* [pixiv](https://www.pixiv.net/)
* [twitter](https://twitter.com/)
* [danbooru](https://danbooru.donmai.us/)
* [yande.re](https://yande.re/)
* [konachan](https://konachan.com/)
* [weibo](https://www.weibo.com/)
* [e-hentai](https://e-hentai.org/)


# Get Started

Every Supported Websites is corresponding to a class, they are:

* PixivPic(url: str)
* TwitterPic(url: str)
* DanbooruPic(url: str)
* YanderePic(url: str)
* KonachanPic(url: str)
* WeiboPic(url: str)
* EHentaiPic(url: str)

All of these classes are derived from super class WebPic

As you see, these classes take a url: str as parameter. They will raise a ValueError if inputted url is not belong to their domain.

You can also call url2WebPic(url: str) if you don't know which class is the url belong to, it will return the correct class object or None if inputted url is unsupported.

In every classes above, we provided following interfaces:


## class WebPic:
### Super class of all other *Pic classes

* **clear() -> None**
  * clear all data in a WebPic object. **You should manually call this function for each WebPic object, they won't destruct autometically.**
* **getUrl() -> str**
  * get inputted url of current object
* **getWebPicType() -> WebPicType**
  * get [class WebPicType](#class-webpictypeintenum) of current object

## WebPic derived classes:
### Getters
* **getFileUrl() -> list**
  * get file url(s) of current object **only if it is a child & contains image(s)**
* **getFileName() -> list**
  * get file name(s) from file url **only if it is a child & contains image(s)**
* **getSrcUrl() -> str**
  * get source url of the image if found one. 
  * **pixiv, twitter, and twitter are consider as \"source websites\"**
  * **we assumed e-hentai urls have no source**
* **hasArtist() -> bool**
  * whether current object has artist(s) specified
* **getArtistInfo() -> ArtistInfo**
  * return [class ArtistInfo](#class-artistinfo)
* **getTags() -> list**
  * get tags of current image(s)
### Booleans
* **isParent() -> bool**
  * whether current object is parent
* **isChild() -> bool**
  * whether current object is child
#### It is hard to specify who is parent and who is child for different websites. So, we assume all the webpages that only contains downloadable images as child, and all other webpages from the same domain that contains thoese children are parent.

### Other Functions
* **clear() -> None**
  * clear all data in a WebPic object. **You should manually call this function for each WebPic object, they won't destruct autometically.**
* **getParentChildStatus() -> ParentChild**
  * get [class ParentChild](#class-parentchildintenum) status of current object
* **downloadPic(dest_filepath = None) -> None**
  * download image(s) in current object **only if current object is a child**
* **getChildrenUrls(max_num: int = 30) -> list**
  * get children urls from current object **only if current object is a parent**
  * parameter: max_num sets the limit of how many children will be capture
  * for **e-hentai urls**
    * if current object is an **e-hentai Gallery**, this function will return Pictures under that Gallery
    * if current object is an **e-hentai Search Page or Main Page**, this function will return Galleries in the page 

## class ArtistInfo:
### Stores basic info for artist

* clear(self) -> None
### Getters
* **getArtistNames(self) -> list:**
  * return founded artist name(s)
* **getUrl_pixiv(self) -> list**
  * get artist pixiv url
* **getUrl_twitter(self) -> list**
  * get artist twitter url
### Although weibo count as a \"source website\", it is rare to see weibo url in other websites, so we did not plan to store it in class ArtistInfo

## class ParentChild(IntEnum)
### derived from class IntEnum, stores the status of a WebPic object
### Status
* UNKNOWN = 0
* PARENT = 1
* CHILD = 2

## class WebPicType(IntEnum)
### derived from class IntEnum, stores the url type of a WebPic object

### WebPicType Bit Table
| Type     | decimal Number | Binary Number |
|----------|----------------|---------------|
| PIXIV    | 1              | 0b 00000001   |
| TWITTER  | 2              | 0b 00000010   |
| DANBOORU | 4              | 0b 00000100   |
| YANDERE  | 8              | 0b 00001000   |
| KONACHAN | 16             | 0b 00010000   |
| WEIBO    | 32             | 0b 00100000   |
| EHENTAI  | 64             | 0b 01000000   |
| UNKNOWN  | 128            | 0b 10000000   |

* We use store this WebPicType info in 8-bits, so it is possible to use bit wise operators to assign multiple WebPicTypes to a row in database

## Public Functions

### functions relate to API
* **isEmptyWebPic(webpic: any) -> bool**
  * whether input WebPic object is empty
  * return False if input parameter is a not WebPic object
* **WebPicType2Str(webpic_type: WebPicType) -> str**
  * convert WebPicType to string, output can be:

| WebPicType | Output     |
|------------|------------|
| PIXIV      | "pixiv"    |
| TWITTER    | "twitter"  |
| DANBOORU   | "danbooru" |
| YANDERE    | "yandere"  |
| KONACHAN   | "konachan" |
| WEIBO      | "weibo"    |
| EHENTAI    | "ehentai"  |
| UNKNOWN    | None       |

* **Str2WebPicType(webpic_type_str: str) -> WebPicType**
  * convert strings to WebPicType
  * input string can be any thing in the table above
  * if input string cannot be identified, function return WebPicType.UNKNOWN
* **WebPicType2DomainStr(webpic_type: WebPicType) -> str**
  * convert WebPicType to url's domain as string
  * we use "m.weibo.cn" as the domain for WEIBO because "www.weibo.com" cannot display weibo status in a single page, weibo status only come with "m.weibo.cn"

| WebPicType | Output               |
|------------|----------------------|
| PIXIV      | "www.pixiv.net"      |
| TWITTER    | "www.twitter.com"    |
| DANBOORU   | "danbooru.donmai.us" |
| YANDERE    | "yande.re"           |
| KONACHAN   | "konachan.com"       |
| WEIBO      | "m.weibo.cn"         |
| EHENTAI    | "e-hentai.org"       |
| UNKNOWN    | None                 |

* **DomainStr2WebPicType(domain_str: str) -> WebPicType**
  * convert domain string listed above to WebPicType
  * This function can also recinize the WebPicType from full url
* **WebPicTypeMatch(src_type: WebPicType, dest_type: WebPicType) -> bool**
  * wether src_type is same as dest_type
* **url2WebPic(url: str) -> any**
  * get WebPic object from any supported url
* **printInfo(webpic: any) -> None**
  * printing all info of a supported WebPic

### helper functions (Not neccessary to user)
* **findFirstNonNum(s: str, start_idx: int = 0) -> int**
  * find first character that is not a number from a string
* **space2lowline(s: str) -> str**
  * convert all space character (' ') in the string to lowline charator ('_')
* **rmListDuplication(l: list) -> list**
  * remove duplication from inputted list


## Code Examples
Checkout [Test.py](./Test.py) for examples and demonstrations

