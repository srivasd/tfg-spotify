import spotipy
import spotipy.util as util
import json

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    search_str = 'Imagine Dragons'
    sp = spotipy.Spotify(auth=token)
    result = sp.search(search_str, type='artist')
    print(json.dumps(result, indent=1))
else:
    print("Can't get token for", username)