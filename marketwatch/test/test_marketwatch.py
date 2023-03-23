import pytest
from unittest.mock import patch, MagicMock
from marketwatch import Strategy, Profile, encode_client_info

@pytest.fixture
def strategy():
    return Strategy(
        client_id='my_client_id',
        client_secret='my_client_secret'
        )

@pytest.fixture
def access_token():
    return 'my_access_token'

@pytest.fixture
def user_info():
    return {
        'identities': [{'provider': 'my_provider'}],
        'name': 'my_display_name',
        'user_id': 'my_user_id',
        'family_name': 'my_family_name',
        'given_name': 'my_given_name',
        'email': 'my_email',
        'picture': 'my_picture',
        'locale': 'my_locale',
        'nickname': 'my_nickname',
        'gender': 'my_gender',
    }

@pytest.fixture
def raw_user_info():
    return 'my_raw_user_info'

@patch('requests.post')
def test_get_delegation_token(mock_post, strategy):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '{"id_token": "my_id_token"}'
    mock_post.return_value = mock_response
    id_token, result = strategy.get_delegation_token('my_id_token', 'my_scope')
    assert id_token == 'my_id_token'
    assert result == {'id_token': 'my_id_token'}

@patch('requests.get')
def test_user_profile(mock_get, strategy, access_token, user_info, raw_user_info):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = raw_user_info
    mock_get.return_value = mock_response
    profile = strategy.user_profile(access_token)
    assert profile.provider == user_info['identities'][0]['provider']
    assert profile.displayName == user_info['name']
    assert profile.id == user_info['user_id']
    assert profile.name['familyName'] == user_info['family_name']
    assert profile.name['givenName'] == user_info['given_name']
    assert profile.emails == [{'value': user_info['email']}]
    assert profile.picture == user_info['picture']
    assert profile.locale == user_info['locale']
    assert profile.nickname == user_info['nickname']
    assert profile.gender == user_info['gender']
    assert profile._json == user_info
    assert profile._raw == raw_user_info