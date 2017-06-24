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
