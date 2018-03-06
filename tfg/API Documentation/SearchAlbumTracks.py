import spotipy
import spotipy.util as util
import json
import sys

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Night Visions
    album_id = '1vAEF8F0HoRFGiYOEeJXHW'
    sp = spotipy.Spotify(auth=token)
    count = sys.maxsize
    offset = 0
    limit = 50
    while True:
        album_info = sp.album_tracks(album_id, offset=offset, limit=limit)
        offset += len(album_info['items'][0])
        # print(json.dumps(album_info, indent=1))
        print(album_info["items"][0]["name"])
        if len(album_info['items']) < limit:
            break
else:
    print("Can't get token for", username)