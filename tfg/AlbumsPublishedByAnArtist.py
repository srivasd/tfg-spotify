import spotipy
import spotipy.util as util
import json
import sys

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    artist_id = '53XhwfbYqKCa1cC15pYq2q'
    sp = spotipy.Spotify(auth=token)
    count = sys.maxsize
    offset = 0
    limit = 1
    while True:
        artist_info = sp.artist_albums(artist_id, album_type='album', offset=offset, limit=limit)
        offset += len(artist_info['items'])
        print(json.dumps(artist_info, indent=1))
        if len(artist_info['items']) < limit:
            break
else:
    print("Can't get token for", username)