import spotipy
import spotipy.util as util
import json

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Maldita Nerea
    artist_id = '3heR1it0slFXjaa7E62zpw'
    sp = spotipy.Spotify(auth=token)
    artist_info = sp.artist_related_artists(artist_id)
    print(json.dumps(artist_info, indent=1))
else:
    print("Can't get token for", username)