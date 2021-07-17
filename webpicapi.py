

# public functions

# get get url source as string
def getUrlSource(url) -> str:
    from urllib3 import PoolManager
    resp = PoolManager().request("GET", url)
    str_data = resp.data.decode('utf-8')
    return str_data
