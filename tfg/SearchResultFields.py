import spotipy
import spotipy.util as util
import json

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)


if token:
    # Imagine Dragons
    artist_id = '53XhwfbYqKCa1cC15pYq2q'
    sp = spotipy.Spotify(auth=token)
    artist_info = sp.artist(artist_id)
    print('Genres:')
    for g in artist_info['genres']:
        print(g)
    print('\nName:', artist_info['name'])
    print('Popularity:', artist_info['popularity'])
    print('URI:', artist_info['uri'])
    print('Followers:', artist_info['followers']['total'])
    if 'images' in artist_info:
        print('Image:', artist_info['images'][0]['url'])
    print('ID:', artist_info['id'])
else:
    print("Can't get token for", username)