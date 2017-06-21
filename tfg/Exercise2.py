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
    albums = sp.artist_albums(artist_id=artist_id, album_type='album')
    # print(json.dumps(albums, indent=1))
    for album in albums['items']:
        print('\nAlbum name:', album['name'])
        album_id = album['id']
        sp = spotipy.Spotify(auth=token)
        count = sys.maxsize
        offset = 0
        limit = 50
        cont = 1
        while True:
            album_info = sp.album_tracks(album_id, offset=offset, limit=limit)
            offset += len(album_info['items'])
            for song in album_info['items']:
                print('Song', cont, ':', song['name'])
                track_info = sp.audio_features(song['id'])
                # print(json.dumps(track_info, indent=1))
                for feature in track_info:
                    print('\tDanceability:', feature['danceability'])
                    print('\tEnergy:', feature['energy'])
                    print('\tLiveness:', feature['liveness'])
                cont += 1
            # print(json.dumps(album_info, indent=1))
            if len(album_info['items']) < limit:
                break
else:
    print("Can't get token for", username)