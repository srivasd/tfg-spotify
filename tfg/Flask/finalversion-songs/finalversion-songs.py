#!/usr/bin/env python
from json import dumps
from sys import maxsize

import spotipy
import sys
from flask import Flask, g, Response, request
from neo4j.v1 import GraphDatabase, basic_auth
from spotipy import Spotify
from spotipy.util import prompt_for_user_token

app = Flask(__name__, static_url_path='/static/')
driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "neo4j"))

scope = 'user-library-read'

username = 'srivasdelgado'

token = prompt_for_user_token(username, scope)
print(token)


def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


@app.route("/")
def get_index():
    db = get_db()

    song_proof = request.args.get('song', default = '', type = str)
    print("Cancion parametro: " + song_proof)

    if song_proof != '':
        if token:

            main_features = []
            actual_features = []
            songs_checked = []
            related_artists_checked = []
            related_artist_global = ""

            sp = spotipy.Spotify(auth=token)

            result = sp.search(song_proof, type='track')
            song_id = result['tracks']['items'][0]['id']

            song_info = sp.track(song_id)

            db.run("CREATE (s:Song {name: {name}, main: {main}})",
                   {"name": song_info['name'], "main": True})

            song_features = sp.audio_features(song_info['id'])

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
            main_artist = song_info['album']['artists'][0]['name']
            artistId = song_info['album']['artists'][0]['id']
            print(artistId)

            db.run("CREATE (ar:Artist {name: {name}, main: {main}})",
                        {"name": song_info['album']['artists'][0]['name'], "main": True})

            db.run("MATCH (s:Song),(ar:Artist) CREATE (s)-[r: ARTIST]->(ar) RETURN r")
            # Related Artist's
            sp = spotipy.Spotify(auth=token)
            related_artists = sp.artist_related_artists(artistId)

            for related_artist in related_artists['artists']:
                print(related_artist['id'])
                # Artist's related songs to the first one
                # Artist's albums

                sp = spotipy.Spotify(auth=token)

                offset = 0
                limit = 2
                artist_albums_ids = []
                while True:
                    artist_albums = sp.artist_albums(related_artist['id'], album_type='album', offset=offset, limit=limit)
                    offset += len(artist_albums['items'])

                    for album in artist_albums['items']:

                        artist_albums_ids.append(album['id'])
                        # Artist's songs
                        for artist_albums_id in artist_albums_ids:
                            sp = spotipy.Spotify(auth=token)

                            offset = 0
                            limit = 3
                            while True:
                                album_songs = sp.album_tracks(artist_albums_id, offset=offset, limit=limit)
                                offset += len(album_songs['items'])

                                cont = 1
                                for song in album_songs['items']:
                                    track_info = sp.audio_features(song['id'])

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
                                                related_artist_global = related_artist['name']
                                                cypher_artist = "CREATE (ar:Artist {name: {name}, main: {main}})"
                                                db.run(cypher_artist,
                                                            {"name": related_artist['name'], "main": False})

                                                db.run("CREATE (s:Song {name: {name}, artist: {artist}, main: {main}})",
                                                        {"name": song['name'], "artist": song['artists'][0]['name'], "main": False})
                                            related_song_global = song['name']
                                            db.run(
                                                "MATCH (ar:Artist),(s:Song) WHERE ar.name = \"" + related_artist_global + "\" AND s.name = \"" + related_song_global + "\" CREATE (ar)-[r:RELATED_SONG]->(s) RETURN r")
                                            related_artists_checked.append(related_artist)
                                    cont += 1

                                if len(album_songs['items']) < limit:
                                    break
                            break
                    if len(artist_albums['items']) < limit:
                        break

            db.run(
                'MATCH (ar:Artist),(ar2:Artist) WHERE ar.name = "' + main_artist + "\" AND NOT ar2.name = \"" + main_artist + "\"CREATE (ar)-[r: RELATED_ARTIST]->("
                                                                                                                               "ar2) RETURN r")

        # Repeat the process

        else:
            print("Can't get token for", username)

    return app.send_static_file('index.html')


@app.route("/graph")
def get_graph():
    db = get_db()
    nodes = []
    rels = []
    print('--------------------GRAPH INFORMATION--------------------')
    songs_main = db.run("MATCH (s:Song) WHERE s.main = True RETURN s")
    for song in songs_main:
        song_properties = song['s'].properties
        print(song_properties)
        nodes.append({"title": song_properties["name"], "label": "song"})
    # Target de la cancion escogida
    target = 0
    artists_main = db.run("MATCH (a:Artist) WHERE a.main = True RETURN a")
    for artist in artists_main:
        artist_properties = artist['a'].properties
        print(artist_properties)
        nodes.append({"title": artist_properties["name"], "label": "artist"})
    # Source de grupo de la canción escogida
    source = 1
    rels.append({"source": source, "target": target})
    # Target2 grupo de la cancion escogida y Source2 grupos relacionados
    target2 = 1
    source2 = 2
    related_artists = db.run("MATCH (a:Artist) WHERE a.main = False RETURN a")
    for related_artist in related_artists:
        related_artist_properties = related_artist['a'].properties
        nodes.append({"title": related_artist_properties["name"], "label": "artist"})
        rels.append({"source": source2, "target": target2})
        target3 = source2
        source3 = source2 + 1
        related_songs = db.run("MATCH (s:Song) WHERE s.artist = \""+related_artist_properties["name"]+"\" AND s.main "
                                                                                                      "= False RETURN"
                                                                                                      " s")
        for related_song in related_songs:
            related_song_properties = related_song['s'].properties
            nodes.append({"title": related_song_properties["name"], "label": "song"})
            rels.append({"source": source3, "target": target3})
            source3 += 1
        source2 = source3

    for n in nodes:
        print(n)
    for r in rels:
        print(r)
    print(Response(dumps({"nodes": nodes, "links": rels}),
                   mimetype="application/json"))
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


if __name__ == '__main__':
    app.run(port=8080)
