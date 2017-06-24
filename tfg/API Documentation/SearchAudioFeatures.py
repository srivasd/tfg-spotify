import spotipy
import spotipy.util as util
import json

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # On top of the world
    track_id = '4eLSCSELtKxZwXnFbNLXT5'
    sp = spotipy.Spotify(auth=token)
    track_info = sp.audio_features(track_id)
    print(json.dumps(track_info, indent=1))
else:
    print("Can't get token for", username)
