
from distutils.core import setup
from WebPicAPI.Version import VERSION

with open("./README.md", "r") as file:
    readme = file.read()

setup(
    name="WebPicAPI",
    version=VERSION,
    description="A simple API to fetch basic info and download pictures from popular picture/wallpaper websites and social media.",
    long_description=readme,
    author="Gavin1937",
    author_email="gyh1837771475gyh@gmail.com",
    url="https://github.com/Gavin1937/WebPicAPI",
    packages=["WebPicAPI", "WebPicAPI.Api", "WebPicAPI.ApiManager", "WebPicAPI.Util"]
)