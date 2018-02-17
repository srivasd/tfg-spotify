import spotipy
import json

from spotipy.util import prompt_for_user_token

search_str = 'On Top Of The World'

scope = 'user-library-read'

username = 'srivasdelgado'

token = prompt_for_user_token(username, scope)
print(token)

sp = spotipy.Spotify(auth=token)

result = sp.search(search_str, type='track')
print(json.dumps(result, indent=1))

print(result['tracks']['items'][0]['id'])
