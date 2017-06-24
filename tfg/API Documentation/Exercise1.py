import spotipy
import spotipy.util as util

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Imagine Dragons
    artist_id = '53XhwfbYqKCa1cC15pYq2q'
    sp = spotipy.Spotify(auth=token)
    artist_info = sp.artist_related_artists(artist_id)
    for g in artist_info['artists']:
        print('\nGroup Name(Level 1):', g['name'])
        artist_id2 = g['id']
        artist_info2 = sp.artist_related_artists(artist_id2)
        for h in artist_info2['artists']:
            print('\n\tGroup Name(Level 2):', h['name'])
            artist_id3 = h['id']
            artist_info3 = sp.artist_related_artists(artist_id3)
            for i in artist_info3['artists']:
                print('\n\t\tGroup Name(Level 3):', i['name'])
else:
    print("Can't get token for", username)