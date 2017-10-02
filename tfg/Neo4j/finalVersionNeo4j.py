import spotipy
import spotipy.util as util
import json
import sys
from neo4j.v1 import GraphDatabase, basic_auth

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
session = driver.session()

if token:
    # Song (On top of the world)
    main_features = []
    actual_features = []
    songs_checked = []
    related_artists_checked = []
    song_id = '4eLSCSELtKxZwXnFbNLXT5'
    sp = spotipy.Spotify(auth=token)
    offset = 0
    limit = 2
    song_info = sp.track(song_id)
    # print(json.dumps(song_info, indent=1))
    session.run("CREATE (s:Song {name: {name}})",
                {"name": song_info['name']})
    song_features = sp.audio_features(song_info['id'])
    # print(json.dumps(track_info, indent=1))
    print(song_info['name'])
    for feature in song_features:
        print('\tDanceability:', feature['danceability'])
        main_features.append(feature['danceability'])
        print('\tEnergy:', feature['energy'])
        main_features.append(feature['energy'])
        print('\tLiveness:', feature['liveness'])
        main_features.append(feature['liveness'])
        print('\tMode:', feature['mode'])
        main_features.append(feature['mode'])
        print('\tSpeechiness:', feature['speechiness'])
        main_features.append(feature['speechiness'])
        print('\tAcousticness:', feature['acousticness'])
        main_features.append(feature['acousticness'])
        print('\tInstrumentalness:', feature['instrumentalness'])
        main_features.append(feature['instrumentalness'])
        print('\tValence:', feature['valence'])
        main_features.append(feature['valence'])
    # Song's artist
    # artistName = song_info['album']['artists'][0]['name']
    artistId = song_info['album']['artists'][0]['id']
    print(artistId)

    session.run("CREATE (ar:Artist {name: {name}})",
                {"name": song_info['album']['artists'][0]['name']})

    session.run("MATCH (s:Song),(ar:Artist) CREATE (s)-[r: ARTIST]->(ar) RETURN r")
    # Related Artist's
    sp = spotipy.Spotify(auth=token)
    related_artists = sp.artist_related_artists(artistId)
    # print(json.dumps(related_artists, indent=1))
    for related_artist in related_artists['artists']:
        print(related_artist['id'])
        # Artist's related songs to the first one
        # Artist's albums

        sp = spotipy.Spotify(auth=token)
        count = sys.maxsize
        offset = 0
        limit = 2
        artist_albums_ids = []
        while True:
            artist_albums = sp.artist_albums(related_artist['id'], album_type='album', offset=offset, limit=limit)
            offset += len(artist_albums['items'])
            # print(json.dumps(artist_albums, indent=1))
            # for album in artist_albums['items']:
            for album in artist_albums['items']:
                # print(album['id'])
                artist_albums_ids.append(album['id'])
                # Artist's songs
                for artist_albums_id in artist_albums_ids:
                    sp = spotipy.Spotify(auth=token)
                    count = sys.maxsize
                    offset = 0
                    limit = 3
                    while True:
                        album_songs = sp.album_tracks(artist_albums_id, offset=offset, limit=limit)
                        offset += len(album_songs['items'])
                        # print(json.dumps(album_info, indent=1))
                        cont = 1
                        for song in album_songs['items']:
                            track_info = sp.audio_features(song['id'])
                            # print(json.dumps(track_info, indent=1))
                            for feature in track_info:
                                change_feature = 0
                                actual_features.append(feature['danceability'])
                                actual_features.append(feature['energy'])
                                actual_features.append(feature['liveness'])
                                actual_features.append(feature['mode'])
                                actual_features.append(feature['speechiness'])
                                actual_features.append(feature['acousticness'])
                                actual_features.append(feature['instrumentalness'])
                                actual_features.append(feature['valence'])
                                i = 0
                                while i <= 7:
                                    if isinstance(actual_features[i], float):
                                        change_feature = abs(actual_features[i] - main_features[i]) + change_feature
                                    i = i + 1
                                actual_features.clear()
                                if change_feature < 0.5 and song not in songs_checked:
                                    print('Song', cont, ':', song['name'])

                                    print('\tDanceability:', feature['danceability'])
                                    print('\tEnergy:', feature['energy'])
                                    print('\tLiveness:', feature['liveness'])
                                    print('\tMode:', feature['mode'])
                                    print('\tSpeechiness:', feature['speechiness'])
                                    print('\tAcousticness:', feature['acousticness'])
                                    print('\tInstrumentalness:', feature['instrumentalness'])
                                    print('\tValence:', feature['valence'])
                                    songs_checked.append(song)

                                    if related_artist not in related_artists_checked:
                                        cypher_artist = "CREATE (ra:RelatedArtist {name: {name}})"
                                        session.run(cypher_artist,
                                                    {"name": related_artist['name']})

                                    session.run("CREATE (rs:RelatedSong {name: {name}})",
                                                {"name": song['name']})
                                    # session.run("MATCH (rar:RelatedArtist),(rs:RelatedSong) CREATE (rar)-[r: "
                                    #             "RELATED_SONG]->(rs) RETURN r")
                                    related_artists_checked.append(related_artist)
                            cont += 1
                        # print(json.dumps(album_info, indent=1))
                        if len(album_songs['items']) < limit:
                            break
                    break
            if len(artist_albums['items']) < limit:
                break

    session.run("MATCH (ar:Artist),(rar:RelatedArtist) CREATE (ar)-[r: RELATED_ARTIST]->("
                "rar) RETURN r")


# Repeat the process


else:
    print("Can't get token for", username)

session.close()
