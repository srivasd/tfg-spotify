
# export SPOTIPY_CLIENT_ID='1e0cf3d0cdd8419083524b6f045849d5'
# export SPOTIPY_CLIENT_SECRET='01ac539b293a4860bb0cc4ee8d07d5f3'
# export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'

import spotipy
import spotipy.util as util

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    sp = spotipy.Spotify(auth=token)
    results = sp.current_user_saved_tracks()
    for item in results['items']:
        track = item['track']
        print(track['name'] + ' - ' + track['artists'][0]['name'])
else:
    print("Can't get token for", username)
