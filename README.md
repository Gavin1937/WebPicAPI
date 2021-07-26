
# Web Picture Python3 API

### This API is design for fetching basic info and download pictures from popular picture/wallpaper websites.


# Python Version: Python 3.8.10


# Dependencies

| Dependency Name                                                    | Usage                     | Version |
|--------------------------------------------------------------------|---------------------------|---------|
| [PixivPy](https://github.com/upbit/pixivpy)                        | class PixivAPI            | 3.6.0   |
| [tweepy](https://github.com/tweepy/tweepy)                         | class TwitterAPI          | 3.10.0  |
| [requests](https://github.com/psf/requests)                        | for both PixivPy & tweepy | 2.22.0  |
| [requests-oauthlib](https://github.com/requests/requests-oauthlib) | for both PixivPy & tweepy | 1.3.0   |

## Install all dependencies with:
```sh
pip3 install pixivpy tweepy requests requests-oauthlib
``` 

# Requried API tokens

| Name                                                                                                  | Tutorials                                                                                                                                                                                            |
|-------------------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| pixiv API: (code, access_token, refresh_token, and expires_in)                                        | [@ZipFile Pixiv OAuth Flow](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362) and [OAuth with Selenium/ChromeDriver](https://gist.github.com/upbit/6edda27cb1644e94183291109b8a5fde) |
| twitter API: (consumer_api_key, consumer_secret, bearer_token, access_token, and access_token_secret) | [Apply For Twitter API Account](https://developer.twitter.com/en/docs/twitter-api/getting-started/getting-access-to-the-twitter-api)                                                                 |

### If you are using [@ZipFile Pixiv OAuth Flow](https://gist.github.com/ZipFile/c9ebedb224406f4f11845ab700124362)'s method for pixiv API, you can use [pixiv_auth.py](./pixiv_auth.py) file under this repo. It's the same file with an additional function.


# Supported Websites:

* [pixiv](https://www.pixiv.net/)
* [twitter](https://twitter.com/)
* [danbooru](https://danbooru.donmai.us/)
* [yande.re](https://yande.re/)
* [konachan](https://konachan.com/)