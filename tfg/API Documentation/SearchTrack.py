import spotipy
import spotipy.util as util
import json
import sys

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Something just like this
    track_id = '6RUKPb4LETWmmr3iAEQktW'
    sp = spotipy.Spotify(auth=token)
    track_info = sp.track(track_id)
    print(json.dumps(track_info, indent=1))
else:
    print("Can't get token for", username)
