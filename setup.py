
from setuptools import setup


with open("./VERSION", "r") as file:
    VERSION = file.read()

with open("./README.md", "r") as file:
    readme = file.read()

with open("./LICENSE", "r") as file:
    license = file.read()

setup(
    name="WebPicAPI",
    version=VERSION,
    description="A simple API to fetch basic info and download pictures from popular picture/wallpaper websites and social media.",
    long_description=readme,
    long_description_content_type="text/markdown",
    author="Gavin1937",
    author_email="gyh1837771475gyh@gmail.com",
    url="https://github.com/Gavin1937/WebPicAPI",
    license="GPL-3.0",
    license_files=license,
    install_requires=["PixivPy", "tweepy", "requests", "requests-oauthlib", "beautifulsoup4", "lxml"],
    packages=["WebPicAPI", "WebPicAPI.Api", "WebPicAPI.ApiManager", "WebPicAPI.Util"]
)

