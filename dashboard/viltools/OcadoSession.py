import requests

class OcadoSession:
    def __init__(self, urlAccessToken, clientId, clientSecret, apiKey, proxy={}):
        self.clientId = clientId
        self.clientSecret = clientSecret
        self.apiKey = apiKey
        self.proxies = proxy
        self.data = {'client_id': self.clientId,
                     'client_secret': self.clientSecret,
                     'grant_type': 'client_credentials',
                     'scope': 'SERVICE_ACCOUNTS'}
        self.headers = {'x-api-key': self.apiKey,
                        'cache-control': 'no-cache',
                         'Content-Type' : 'application/x-www-form-urlencoded'}
        self.bearerToken = None
        self.urlAccessToken = urlAccessToken

    # Pour rafraichir le Berer Token en cas de besoin
    def refreshToken(self):
        res = requests.post(self.urlAccessToken, proxies=self.proxies, headers=self.headers, data=self.data)
        resJson = res.json()
        # TODO : Verifier existence du Refresh Token sinon sortir en erreur...
        self.bearerToken = resJson["access_token"]

    def get(self, url, reqId="IdParDefaut", **kwargs):
        if self.bearerToken == None:
            self.refreshToken()  # Cas du premier appel si Token non initialisé
        headers = {'x-api-key': self.apiKey,
                   'RequestId': reqId,
                   "Authorization": "Bearer " + self.bearerToken,
                   "Content-Type": "application/json"}
        res = requests.get(url, proxies=self.proxies, headers=headers, **kwargs)
        if res.status_code == 401:  # Cas ou le Token a expiré
            self.refreshToken()
            headers = {'x-api-key': self.apiKey,
                       'RequestId': reqId,
                       "Authorization": "Bearer " + self.bearerToken,
                       "Content-Type": "application/json"}
            res = requests.get(url, proxies=self.proxies, headers=headers, **kwargs)
        return res,headers

    def put(self, url, reqId="IdParDefaut", **kwargs):
        if self.bearerToken == None:
            self.refreshToken()  # Cas du premier appel si Token non initialisé
        headers = {'x-api-key': self.apiKey,
                   'RequestId': reqId,
                   "Authorization": "Bearer " + self.bearerToken,
                   "Content-Type": "application/json"}
        res = requests.put(url, proxies=self.proxies, headers=headers, **kwargs)
        if res.status_code == 401:  # Cas ou le Token a expiré
            self.refreshToken()
            headers = {'x-api-key': self.apiKey,
                       'RequestId': reqId,
                       "Authorization": "Bearer " + self.bearerToken,
                       "Content-Type": "application/json"}
            res = requests.put(url, proxies=self.proxies, headers=headers, **kwargs)
        return res,headers


    def post(self, url, reqId="IdParDefaut", **kwargs):
        if self.bearerToken == None:
            self.refreshToken()  # Cas du premier appel si Token non initialisé
        headers = {'x-api-key': self.apiKey,
                   'RequestId': reqId,
                   "Authorization": "Bearer " + self.bearerToken,
                   "Content-Type": "application/json"}
        res = requests.post(url, proxies=self.proxies, headers=headers, **kwargs)
        if res.status_code == 401:  # Cas ou le Token a expiré
            self.refreshToken()
            headers = {'x-api-key': self.apiKey,
                       'RequestId': reqId,
                       "Authorization": "Bearer " + self.bearerToken,
                       "Content-Type": "application/json"}
            res = requests.post(url, proxies=self.proxies, headers=headers, **kwargs)
        return res,headers


    def delete(self, url, reqId="IdParDefaut", **kwargs):
        if self.bearerToken == None:
            self.refreshToken()  # Cas du premier appel si Token non initialisé
        headers = {'x-api-key': self.apiKey,
                   'RequestId': reqId,
                   "Authorization": "Bearer " + self.bearerToken,
                   "Content-Type": "application/json"}
        res = requests.delete(url, proxies=self.proxies, headers=headers, **kwargs)
        if res.status_code == 401:  # Cas ou le Token a expiré
            self.refreshToken()
            headers = {'x-api-key': self.apiKey,
                       'RequestId': reqId,
                       "Authorization": "Bearer " + self.bearerToken,
                       "Content-Type": "application/json"}
            res = requests.delete(url, proxies=self.proxies, headers=headers, **kwargs)
        return res,headers
# Fin Class ocadoSession
