#!/usr/bin/env python
import os
from json import dumps

import spotipy
from flask import Flask, g, Response, request, send_from_directory
from neo4j.v1 import GraphDatabase, basic_auth
from spotipy.util import prompt_for_user_token

import threading
import time
import requests

app = Flask(__name__, static_url_path='/static/')
driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "neo4j"))

scope = 'user-library-read'

username = 'srivasdelgado'

token = prompt_for_user_token(username, scope)
print(token)

level = 0
initial = True
initial_graph = True

target = 0
source = 0

id = 0

nodes = []
rels = []


def get_db():
    if not hasattr(g, 'neo4j_db'):
        g.neo4j_db = driver.session()
    return g.neo4j_db


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'neo4j_db'):
        g.neo4j_db.close()


def start_runner():
    def start_loop():
        not_started = True
        while not_started:
            print('In start loop')
            try:
                r = requests.get('http://127.0.0.1:8080/graph')
                if r.status_code == 200:
                    print('/graph 200 Status')
                    not_started = True
                    # not_started = False
                print(r.status_code)
            except:
                print('/graph status error')
            time.sleep(15)

    print('Started runner')
    thread = threading.Thread(target=start_loop)
    thread.start()
    app.background_thread = thread


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route("/details")
def get_details():
    global level
    db = get_db()

    song_clicked = db.run('MATCH (s:Song) WHERE s.level = ' + str(level) + ' AND s.main = TRUE RETURN s')

    song_name = ""
    song_level = ""
    song_artist = ""
    song_id = ""
    song_main = ""
    song_popularity = ""
    song_duration = ""
    song_albummame = ""
    song_releasedate = ""
    song_image = ""

    for record in song_clicked:
        song_name = record["s"].properties['name']
        song_level = str(record["s"].properties['level'])
        song_artist = record["s"].properties['artist']
        song_id = str(record["s"].properties['id'])
        song_main = str(record["s"].properties['main'])
        song_popularity = str(record["s"].properties['popularity'])
        song_duration = record["s"].properties['duration']
        song_albummame = record["s"].properties['albumname']
        song_releasedate = str(record["s"].properties['releasedate'])
        song_image = record["s"].properties['image']

    response_song = {"id": song_id, "name": song_name, "level": str(song_level), "artist": song_artist,
                     "main": song_main, "popularity": song_popularity, "duration": song_duration, "albumname": song_albummame, "releasedate": song_releasedate, "image": song_image}

    return Response(dumps({"song_clicked": response_song}),
                    mimetype="application/json")


@app.route("/")
def get_index():
    global level
    global initial
    global id

    db = get_db()

    song_proof = request.args.get('song', default='', type=str)
    print("Cancion parametro: " + song_proof)

    artist_proof = request.args.get('artist', default='', type=str)
    print("Artista parametro: " + artist_proof)

    if song_proof != '':

        if token:
            level = level + 1
            main_features = []
            actual_features = []
            songs_checked = []
            related_artists_checked = []
            song_id = ""
            artist_in_bbdd = ""

            sp = spotipy.Spotify(auth=token)

            if not initial:
                queryInitial = 'MATCH (s:Song) WHERE s.name = "' + song_proof + '" RETURN s'
                resultsInitial = db.run(queryInitial)
                for record in resultsInitial:
                    artist = record["s"].properties['artist']
                db.run('MATCH (a:Artist { name: "' + artist + '" }) SET a.level = ' + str(
                    level) + ', a.main = TRUE RETURN a')
                db.run('MATCH (s:Song { name: "' + song_proof + '" }) SET s.level = ' + str(
                    level) + ', s.main = TRUE RETURN s')

            if song_proof != '' and artist_proof != '':
                result = sp.search(song_proof, type='track')
                for inputSong in result['tracks']['items']:
                    if inputSong['name'] == song_proof and artist_proof == inputSong["album"]["artists"][0]["name"]:
                        song_id = inputSong['id']

            elif song_proof != '':
                result = sp.search(song_proof, type='track')
                for inputSong in result['tracks']['items']:
                    print("Prueba de input song: " + inputSong['name'])
                    print("Artista de prueba de input song: " + inputSong["album"]["artists"][0]["name"])

                    queryInput = 'MATCH (s:Song) WHERE s.name = "' + song_proof + '" RETURN s'
                    resultsInput = db.run(queryInput)

                    for record in resultsInput:
                        artist_in_bbdd = record["s"].properties["artist"]
                    if inputSong['name'] == song_proof and artist_in_bbdd == inputSong["album"]["artists"][0]["name"]:
                        song_id = inputSong['id']

                if song_id == "":
                    if artist_in_bbdd != "":
                        result_artist = sp.search(artist_in_bbdd, type='artist')
                        result_artist_id = result_artist['artists']['items'][0]['id']
                        artist_albums2 = sp.artist_albums(result_artist_id)
                        for album in artist_albums2['items']:
                            offset = 0
                            limit = 50
                            while True:
                                album_info = sp.album_tracks(album['id'], offset=offset, limit=limit)
                                offset += len(album_info['items'])
                                for track in album_info['items']:
                                    if track['name'] == song_proof:
                                        song_id = track['id']
                                        break
                                if len(album_info['items']) < limit:
                                    break

                if song_id == "":
                    song_id = result['tracks']['items'][0]['id']

            song_info = sp.track(song_id)

            duration_s = song_info['duration_ms'] / 1000
            duration_min = duration_s / 60
            i = 0
            while i + 1 < duration_min:
                i = i + 1
            duration_s = duration_min - i
            duration_s = duration_s * 60
            song_duration = "Min: " + str(i) + " Seg: " + str(round(duration_s, 0))

            queryMainSong = 'MATCH (s:Song) WHERE s.name = "' + song_proof + '" RETURN s'
            resultsMainSong = db.run(queryMainSong)
            duplicatedMainSong = ""

            for record in resultsMainSong:
                duplicatedMainSong = record["s"].properties['name']

            if duplicatedMainSong != song_proof:
                db.run("CREATE (s:Song {name: {name}, level: {level}, artist: {artist}, main: {main}, id: {id}, popularity: {popularity}, duration: {duration}, albumname: {albumname}, releasedate: {releasedate}, image: {image}, uri: {uri}})",
                       {"name": song_info['name'], "level": level, "artist": song_info['album']['artists'][0]['name'],
                        "main": True, "id": id, "popularity": song_info['popularity'], "duration": song_duration, "albumname": song_info['album']['name'], "releasedate": song_info['album']['release_date'], "image": song_info['album']['images'][1]['url'], "uri": song_info['id']})
                id = id + 1

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
            print(main_artist)

            queryMainArtist = 'MATCH (a:Artist) WHERE a.name = "' + song_info['album']['artists'][0][
                'name'] + '" RETURN a'
            resultsMainArtist = db.run(queryMainArtist)
            duplicatedMainArtist = ""
            for record in resultsMainArtist:
                duplicatedMainArtist = record["a"].properties['name']

            if duplicatedMainArtist != song_info['album']['artists'][0]['name']:
                db.run("CREATE (a:Artist {name: {name}, level: {level}, main: {main}, id: {id}, uri: {uri}})",
                       {"name": song_info['album']['artists'][0]['name'], "level": level, "main": True, "id": id, "uri": song_info['album']['artists'][0]['id']})
                id = id + 1
            if duplicatedMainSong != song_proof:
                db.run('MATCH (s:Song),(a:Artist) WHERE s.artist ="' + song_info['album']['artists'][0][
                    'name'] + '" AND a.name ="' + song_info['album']['artists'][0][
                           'name'] + '" CREATE (a)-[r: ARTIST_SONG]->(s) RETURN r')
            # Related Artist's
            related_artists = sp.artist_related_artists(artistId)

            for related_artist in related_artists['artists']:
                print(related_artist['name'])
                # Artist's related songs to the first one
                # Artist's albums

                offset = 0
                limit = 2
                artist_albums_ids = []
                while True:
                    artist_albums = sp.artist_albums(related_artist['id'], album_type='album', offset=offset,
                                                     limit=limit)
                    offset += len(artist_albums['items'])

                    for album in artist_albums['items']:
                        artist_albums_ids.append(album['id'])
                        # Artist's songs
                        for artist_albums_id in artist_albums_ids:
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
                                                change_feature = abs(
                                                    actual_features[i] - main_features[i]) + change_feature
                                            i = i + 1
                                        actual_features.clear()
                                        if change_feature < 0.4 and song not in songs_checked:
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

                                            queryRelatedArtist = 'MATCH (a:Artist) WHERE a.name = "' + \
                                                                 related_artist['name'] + '" RETURN a'
                                            resultsRelatedArtist = db.run(queryRelatedArtist)
                                            duplicatedRelatedArtist = ""
                                            for record in resultsRelatedArtist:
                                                duplicatedRelatedArtist = record["a"].properties['name']

                                            if duplicatedRelatedArtist != related_artist['name']:
                                                cypher_artist = "CREATE (a:Artist {name: {name}, level: {level}, relatedartist: {relatedartist}, main: {main}, id: {id}, uri: {uri}})"
                                                db.run(cypher_artist,
                                                       {"name": related_artist['name'], "level": level,
                                                        "relatedartist": main_artist, "main": False, "id": id, "uri": related_artist['id']})
                                                id = id + 1

                                                db.run(
                                                    'MATCH (ar:Artist),(ar2:Artist) WHERE ar.name = "' + main_artist + '" AND ar2.name = "' +
                                                    related_artist[
                                                        'name'] + '" CREATE (ar)-[r: RELATED_ARTIST]->(ar2) RETURN r')

                                            queryRelatedSong = 'MATCH (s:Song) WHERE s.name = "' + song[
                                                'name'] + '" RETURN s'
                                            resultsRelatedSong = db.run(queryRelatedSong)
                                            duplicatedRelatedSong = ""
                                            for record in resultsRelatedSong:
                                                duplicatedRelatedSong = record["s"].properties['name']

                                            if duplicatedRelatedSong != song['name']:
                                                song_info = sp.track(song['id'])

                                                duration_s = song_info['duration_ms'] / 1000
                                                duration_min = duration_s / 60
                                                i = 0
                                                while i + 1 < duration_min:
                                                    i = i + 1
                                                duration_s = duration_min - i
                                                duration_s = duration_s * 60
                                                song_duration = "Min: " + str(i) + " Seg: " + str(round(duration_s, 0))

                                                db.run(
                                                    "CREATE (s:Song {name: {name}, artist: {artist}, level: {level}, main: {main}, id: {id}, popularity: {popularity}, duration: {duration}, albumname: {albumname}, releasedate: {releasedate}, image: {image}, uri: {uri}})",
                                                    {"name": song['name'], "artist": song['artists'][0]['name'],
                                                     "level": level, "main": False, "id": id, "popularity": song_info['popularity'], "duration": song_duration, "albumname": song_info['album']['name'], "releasedate": song_info['album']['release_date'], "image": song_info['album']['images'][1]['url'], "uri": song_info['id']})
                                                id = id + 1
                                                # Eliminamos las canciones sin grupo
                                                resultsSong = db.run(
                                                    'MATCH (s:Song) WHERE s.name = "' + song['name'] + '" RETURN s')
                                                pruebaCancion = ""
                                                for record in resultsSong:
                                                    resultArtist = db.run(
                                                        'MATCH (a:Artist) WHERE a.name = "' + record["s"].properties[
                                                            'artist'] + '" RETURN a')
                                                    for record2 in resultArtist:
                                                        pruebaCancion = pruebaCancion + record2["a"].properties['name']
                                                if pruebaCancion == "":
                                                    db.run(
                                                        'MATCH (s:Song) WHERE s.name = "' + song['name'] + '" DELETE s')

                                            if duplicatedRelatedSong != song['name']:
                                                db.run('MATCH (a { name: "' + related_artist[
                                                    'name'] + '" })-[r:ARTIST_SONG]->(s { artist: "' + related_artist[
                                                           'name'] + '"}) DELETE r')
                                                db.run('MATCH (s:Song),(a:Artist) WHERE s.artist ="' + related_artist[
                                                    'name'] + '" AND a.name ="' + related_artist[
                                                           'name'] + '" CREATE (a)-[r: ARTIST_SONG]->(s) RETURN r')
                                            related_artists_checked.append(related_artist)
                                    cont += 1

                                if len(album_songs['items']) < limit:
                                    break
                            break
                    if len(artist_albums['items']) < limit:
                        break

                # Eliminamos los artistas o grupos sin canciones

                queryArtistNoSongs = 'MATCH (a:Artist) WHERE a.name = "' + str(related_artist['name']) + '" RETURN a'
                resultsRelatedArtists = db.run(queryArtistNoSongs)
                resultsNoSongs = []
                pruebaArtista = ""
                for record in resultsRelatedArtists:
                    pruebaArtista = pruebaArtista + record["a"].properties['name']
                if pruebaArtista != "":
                    resultsNoSongs = db.run('MATCH (s:Song) WHERE s.artist = "' + related_artist['name'] + '" RETURN s')

                prueba = ""
                for record in resultsNoSongs:
                    prueba = prueba + record["s"].properties['name']
                if prueba == "":
                    db.run('MATCH (a1:Artist) - [r] -> () WHERE a1.name = "' + related_artist['name'] + '" DELETE r')
                    db.run('MATCH (a1:Artist) - [r] -> (a2:Artist) WHERE a2.name = "' + related_artist[
                        'name'] + '" DELETE r')
                    db.run('MATCH (a:Artist) WHERE a.name = "' + related_artist['name'] + '" DELETE a')

            initial = False
            # Repeat the process

        else:
            print("Can't get token for", username)

    return app.send_static_file('index.html')


@app.route("/graph")
def get_graph():
    db = get_db()
    global level
    global target
    global source
    global initial_graph
    global nodes
    global rels

    print('--------------------GRAPH INFORMATION--------------------')

    aux = ""

    query_songs_main = 'MATCH (s:Song) WHERE s.main = True AND s.level = ' + str(level) + ' RETURN s'
    songs_main = db.run(query_songs_main)
    for song in songs_main:
        song_properties = song['s'].properties
        aux = "aux"
        if level > 5:
            main_song_graph = {"id": song_properties["id"], "title": song_properties["name"], "label": "song" + str(5), "uri": song_properties["uri"]}
            if initial_graph:
                nodes.append(main_song_graph)
        else:

            if initial_graph:
                main_song_graph = {"id": song_properties["id"], "title": song_properties["name"],
                                   "label": "song" + str(level), "uri": song_properties["uri"]}
                nodes.append(main_song_graph)
            else:
                for n in nodes:
                    if n["title"] == song_properties["name"]:
                        main_song_graph = n
                        break
        source = nodes.index(main_song_graph)

    query_artists_main = 'MATCH (a:Artist) WHERE a.main = True AND a.level = ' + str(level) + ' RETURN a'
    artists_main = db.run(query_artists_main)
    for artist in artists_main:
        artist_properties = artist['a'].properties
        if level > 5:
            main_artist_graph = {"id": artist_properties["id"], "title": artist_properties["name"],
                                 "label": "artist" + str(5), "uri": artist_properties["uri"]}
            if initial_graph:
                nodes.append(main_artist_graph)
        else:
            if initial_graph:
                main_artist_graph = {"id": artist_properties["id"], "title": artist_properties["name"],
                                     "label": "artist" + str(level), "uri": artist_properties["uri"]}
                nodes.append(main_artist_graph)
            else:
                for n in nodes:
                    if n["title"] == artist_properties["name"]:
                        main_artist_graph = n
                        break
        target = nodes.index(main_artist_graph)
        if initial_graph:
            rels.append({"source": source, "target": target})

    query_related_artists = 'MATCH (a:Artist) WHERE a.main = False AND a.level = ' + str(level) + ' RETURN a'
    related_artists = db.run(query_related_artists)
    source = target
    for related_artist in related_artists:
        related_artist_properties = related_artist['a'].properties
        if level > 5:
            related_artist_graph = {"id": related_artist_properties["id"], "title": related_artist_properties["name"],
                                    "label": "artist" + str(5), "uri": related_artist_properties["uri"]}
            if related_artist_graph not in nodes:
                nodes.append(related_artist_graph)
        else:
            related_artist_graph = {"id": related_artist_properties["id"], "title": related_artist_properties["name"],
                                    "label": "artist" + str(level), "uri": related_artist_properties["uri"]}
            if related_artist_graph not in nodes:
                nodes.append(related_artist_graph)
        target = nodes.index(related_artist_graph)
        artist_relatedartist_rel = {"source": source, "target": target}
        if artist_relatedartist_rel not in rels:
            rels.append({"source": source, "target": target})
        related_songs = db.run(
            'MATCH (s:Song) WHERE s.level = ' + str(level) + ' AND s.artist = "' + related_artist_properties[
                "name"] + '" AND s.main = False RETURN s')
        source2 = target
        for related_song in related_songs:
            related_song_properties = related_song['s'].properties
            if level > 5:
                related_song_graph = {"id": related_song_properties["id"], "title": related_song_properties["name"],
                                      "label": "song" + str(5), "uri": related_song_properties["uri"]}
                if related_song_graph not in nodes:
                    nodes.append(related_song_graph)
            else:
                related_song_graph = {"id": related_song_properties["id"], "title": related_song_properties["name"],
                                      "label": "song" + str(level), "uri": related_song_properties["uri"]}
                for n in nodes:
                    if n["title"] == related_song_properties["name"]:
                        related_song_graph = n
                        break
                if related_song_graph not in nodes:
                    nodes.append(related_song_graph)
            target = nodes.index(related_song_graph)
            relatedartist_relatedsong_rel = {"source": source2, "target": target}
            if relatedartist_relatedsong_rel not in rels:
                rels.append({"source": source2, "target": target})

    # Nuevas canciones de un artista ya disponible en la bbdd
    previous_related_artists = db.run('MATCH (a:Artist) WHERE a.level < ' + str(level) + ' RETURN a')
    for previous_related_artist in previous_related_artists:
        previous_related_artist_properties = previous_related_artist["a"].properties
        previous_related_artist_graph = {"id": previous_related_artist_properties["id"],
                                         "title": previous_related_artist_properties["name"],
                                         "label": "artist" + str(previous_related_artist_properties["level"]), "uri": previous_related_artist_properties["uri"]}
        for n in nodes:
            if n["title"] == previous_related_artist_properties["name"]:
                previous_related_artist_graph = n
                break
        source = nodes.index(previous_related_artist_graph)
        actual_related_songs = db.run(
            'MATCH (s:Song) WHERE s.level = ' + str(level) + ' AND s.artist = "' + previous_related_artist_properties[
                "name"] + '" RETURN s')
        for actual_related_song in actual_related_songs:
            actual_related_song_properties = actual_related_song["s"].properties
            if level > 5:
                previous_related_song_graph = {"id": actual_related_song_properties["id"],
                                               "title": actual_related_song_properties["name"],
                                               "label": "song" + str(5), "uri": actual_related_song_properties["uri"]}
                if previous_related_song_graph not in nodes:
                    nodes.append(previous_related_song_graph)
            else:
                previous_related_song_graph = {"id": actual_related_song_properties["id"],
                                               "title": actual_related_song_properties["name"],
                                               "label": "song" + str(level), "uri": actual_related_song_properties["uri"]}
                for n in nodes:
                    if n["title"] == actual_related_song_properties["name"]:
                        previous_related_song_graph = n
                        break
                if previous_related_song_graph not in nodes:
                    nodes.append(previous_related_song_graph)
            target = nodes.index(previous_related_song_graph)
            other_level_songs_rel = {"source": source, "target": target}
            if other_level_songs_rel not in rels:
                rels.append({"source": source, "target": target})

    for n in nodes:
        print(n)
    for r in rels:
        print(r)

    print("Nivel de la llamada: ", level)

    if aux != "":
        initial_graph = False

    print(Response(dumps({"nodes": nodes, "links": rels}),
                   mimetype="application/json"))
    return Response(dumps({"nodes": nodes, "links": rels}),
                    mimetype="application/json")


if __name__ == '__main__':
    # start_runner()
    app.run(port=8080)
