
# pip install requests
import requests
import base64
import datetime
from urllib.parse import urlencode

# AUTHENTICATION
vClientID = 'a5431a7076994a458137c09d5bec3b1b'
vClientSecret = 'a59462b26c074561afe5f43f178186ab'

# SPOTIFY AUTHENTICATION CLASS
class SpotifyAPI(object):
    vAccessToken = None
    vAccessTokenExpires = datetime.datetime.now()
    vClientID = None
    vClientSecret = None
    vTokenURL = 'https://accounts.spotify.com/api/token'

    def __init__(self, vClientID, vClientSecret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vClientID = vClientID
        self.vClientSecret = vClientSecret

    def GetClientCredentials(self):
        """
        Returns a base64 encoded string
        """
        vClientID = self.vClientID
        vClientSecret = self.vClientSecret

        if(vClientID == None or vClientSecret == None):
            raise Exception("Please set a valid Client ID or Client Secret")

        vClientCredentials = f"{vClientID}:{vClientSecret}"
        vClientCredentialsB64 = base64.b64encode(vClientCredentials.encode())
        return vClientCredentialsB64.decode()

    def GetTokenHeader(self):
        vClientCredentials = self.GetClientCredentials()
        return  {
                    "Authorization": f"Basic {vClientCredentials}"
                }

    def GetTokenData(self):
        return  {
                    "grant_type": "client_credentials"
                }

    def PerformAuthorization(self):
        vTokenURL = self.vTokenURL
        vTokenData = self.GetTokenData()
        vTokenHeader = self.GetTokenHeader()

        vRequests = requests.post(vTokenURL, data = vTokenData, headers = vTokenHeader)

        if vRequests.status_code not in (200, 299):
            raise Exception("Could not authenticate client")

        vNow = datetime.datetime.now()
        vAccessToken = vRequests.json()['access_token']
        vTokenExpiresIn = vRequests.json()['expires_in']
        self.vAccessToken = vAccessToken
        self.vAccessTokenExpires = vNow + datetime.timedelta(seconds=vTokenExpiresIn)
        self.vAccessTokenDidExpire = vNow + datetime.timedelta(seconds=vTokenExpiresIn) < vNow
        return True

    def GetAccessToken(self):
        vAuthorizationDone = self.PerformAuthorization()
        if not vAuthorizationDone:
            raise Exception("Authentication failed")
        vToken = self.vAccessToken
        vExpires = self.vAccessTokenExpires
        vNow = datetime.datetime.now()
        if vExpires < vNow:
            self.PerformAuthorization()
            return self.GetAccessToken()
        elif vToken == None:
            self.PerformAuthorization()
            return self.GetAccessToken()
        return vToken

    def getResourceHeader(self):
        vAccessToken = self.GetAccessToken()
        return {"Authorization": f"Bearer {vAccessToken}"}

    def GetResource(self, vLookupID, vResourceType = 'albums', vVersion = 'v1'):
        vLookupURL = f'https://api.spotify.com/{vVersion}/{vResourceType}/{vLookupID}'
        print(vLookupURL)
        vHeaders = self.getResourceHeader()
        vRequestData = requests.get(vLookupURL, headers=vHeaders)
        if vRequestData.status_code not in range(200, 299):
            return {}
        return vRequestData.json()

    def GetAlbum(self, _id):
        return self.GetResource(_id, vResourceType = 'albums')

    def GetArtist(self, _id):
        return self.GetResource(_id, vResourceType = 'artists')


    def BaseSearch(self, vQueryParams):
        vHeaders = self.getResourceHeader()
        vURL = 'https://api.spotify.com/v1/search'
        vLookupURL = f"{vURL}?{vQueryParams}"
        print(vLookupURL)
        vRequestData = requests.get(vLookupURL, headers=vHeaders)
        if vRequestData.status_code not in range(200, 299):
            return {}
        return vRequestData.json()

    def Search(self, vQuery = None, vSearchType = 'artist', vOperator = None, vOperatorQuery = None):
        if vQuery is None:
            raise Exception('Please enter a query')
        if isinstance(vQuery, dict):
            vQuery = " ".join([f"{k}:{v}" for k,v in vQuery.items()])
        if vOperator != None and vOperatorQuery != None:
            if vOperator.lower() == "or" or vOperator.lower() == "not":
                vOperator = vOperator.upper()
                if isinstance(vOperatorQuery, str):
                    vQuery = f"{vQuery} {vOperator} {vOperatorQuery}"
        vQueryParams = urlencode({"q": vQuery, "type": vSearchType.lower()})
        return self.BaseSearch(vQueryParams)

# ACCESS API

vSpotifyClient = SpotifyAPI(vClientID, vClientSecret)

print(vSpotifyClient.Search({"track": "Everyday", "artist": "Buddy Holly"}, vSearchType="track"))

print(vSpotifyClient.Search(vQuery="Everyday", vOperator="NOT", vOperatorQuery="Ariana Grande", vSearchType="track"))

print(vSpotifyClient.GetArtist('3wYyutjgII8LJVVOLrGI0D'))







