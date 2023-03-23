import json
import base64
import requests
from requests.exceptions import RequestException
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session

class Profile:
    def __init__(self, data, raw):
        self.provider = data['identities'][0]['provider']
        self.displayName = data['name']
        self.id = data['user_id']

        self.name = {
            'familyName': data['family_name'],
            'givenName': data['given_name']
        }

        if 'emails' in data:
            self.emails = [{'value': email} for email in data['emails']]
        elif 'email' in data:
            self.emails = [{'value': data['email']}]

        for k in ['picture', 'locale', 'nickname', 'gender', 'identities']:
            if k in data:
                setattr(self, k, data[k])

        self._json = data
        self._raw = raw

class Strategy(OAuth2Session):
    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, **kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorization_url = 'https://sso.accounts.dowjones.com/authorize'
        self.token_url = 'https://sso.accounts.dowjones.com/oauth/token'
        self.user_info_url = 'https://sso.accounts.dowjones.com/userinfo'
        self.api_url = 'https://sso.accounts.dowjones.com/api'
        self.delegation_url = 'https://sso.accounts.dowjones.com/delegation'

        super(Strategy, self).__init__(client=BackendApplicationClient(client_id=self.client_id), **kwargs)
        self.headers.update({'DowJones-Passport-Client': encode_client_info({'name': 'passport-dowjones', 'version': '1.0.0'})})

    def authorization_params(self, state=None, **kwargs):
        return {'connection': kwargs.get('connection'), 'audience': kwargs.get('audience')}

    def _get_access_token(self):  # sourcery skip: raise-specific-error
        try:
            return self.fetch_token(
                token_url=self.token_url,
                client_id=self.client_id,
                client_secret=self.client_secret,
                grant_type='client_credentials',
                auth=None,
            )
        except RequestException as e:
            raise Exception(f'Failed to fetch access token: {str(e)}') from e

    def get_delegation_token(self, id_token, scopes, **kwargs):
        # sourcery skip: raise-specific-error
        if isinstance(id_token, list):
            id_token = ' '.join(id_token)

        scope = (
            f'openid {scopes}'
            if isinstance(scopes, str)
            else 'openid ' + ' '.join(scopes)
        )
        data = {'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer', 'client_id': self.client_id, 'api_type': 'app', 'id_token': id_token, 'scope': scope}
        headers = {'DowJones-Passport-Client': encode_client_info({'name': 'passport-dowjones', 'version': '1.0.0'})}

        try:
            resp = requests.post(self.delegation_url, data=data, headers=headers)
            resp.raise_for_status()
            result = json.loads(resp.text)
            return result.get('id_token'), result
        except RequestException as e:
            raise Exception(f'Failed to fetch delegation token: {str(e)}') from e

    def user_profile(self, access_token):
        headers = {'Authorization': f'Bearer {access_token}'}
        resp = requests.get(self.user_info_url, headers=headers)
        resp.raise_for_status()
        json_data = json.loads(resp.text)
        return Profile(json_data, resp.text)

def encode_client_info(obj):
    str_ = json.dumps(obj)
    return base64.b64encode(str_.encode('utf-8')).decode('utf-8').replace('+', '-').replace('/', '_').rstrip('=')