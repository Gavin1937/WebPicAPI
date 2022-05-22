
# apitoken.json file template
apitoken_template = """
{
    \"pixiv_token\": {
        \"code\": "",
        \"access_token\": "",
        \"refresh_token\": "",
        \"expires_in\": 0
    },
    \"twitter_token\": {
        \"consumer_api_key\": \"\",
        \"consumer_secret\": \"\",
        \"bearer_token\": \"\",
        \"access_token\": \"\",
        \"access_token_secret\": \"\"
    }
}
"""

def isValidUrl(url: str) -> bool:
    if url is not None and len(url) > 0:
        return True
    else: return False

