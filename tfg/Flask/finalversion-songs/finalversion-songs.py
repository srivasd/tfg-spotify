#!/usr/bin/env python
from json import dumps

import spotipy
import sys
from flask import Flask, g, Response, request
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


@app.route("/")
def get_index():
    global level
    global initial
    global id

    db = get_db()

    song_proof = request.args.get('song', default = '', type = str)
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
            related_artist_global = ""
            song_id = ""
            artist_in_bbdd = ""

            sp = spotipy.Spotify(auth=token)

            if not initial:
                queryInitial = 'MATCH (s:Song) WHERE s.name = "' + song_proof + '" RETURN s'
                resultsInitial = db.run(queryInitial)
                for record in resultsInitial:
                    print(record["s"].properties['name'])
                    artist = record["s"].properties['artist']
                db.run('MATCH (a:Artist { name: "' + artist + '" }) SET a.level = ' + str(level) + ', a.main = TRUE RETURN a')
                db.run('MATCH (s:Song { name: "' + song_proof + '" }) SET s.level = ' + str(level) + ', s.main = TRUE RETURN s')

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
                        print("BBDD: " + record["s"].properties["artist"])
                        artist_in_bbdd = record["s"].properties["artist"]
                    if inputSong['name'] == song_proof and artist_in_bbdd == inputSong["album"]["artists"][0]["name"]:
                        song_id = inputSong['id']

                if song_id == "":
                    if artist_in_bbdd != "":
                        print("Buscamos en el artista")
                        result_artist = sp.search(artist_in_bbdd, type='artist')
                        result_artist_id = result_artist['artists']['items'][0]['id']
                        print(result_artist_id)
                        artist_albums2 = sp.artist_albums(result_artist_id)
                        for album in artist_albums2['items']:
                            print(album['id'])
                            print("Entra en el bucle 1")
                            count = sys.maxsize
                            offset = 0
                            limit = 50
                            while True:
                                print("Entras en el while")
                                album_info = sp.album_tracks(album['id'], offset=offset, limit=limit)
                                print("Pasas del album info")
                                offset += len(album_info['items'])
                                print("Pasas del offset")
                                # print(json.dumps(album_info, indent=1))
                                # print(album_info['items'])
                                for track in album_info['items']:
                                    print("Entra en el bucle 2")
                                    print(track['name'])
                                    print(track['id'])
                                    if track['name'] == song_proof:
                                        song_id = track['id']
                                        break
                                if len(album_info['items']) < limit:
                                    break

                if song_id == "":
                    song_id = result['tracks']['items'][0]['id']

            song_info = sp.track(song_id)
            queryMainSong = 'MATCH (s:Song) WHERE s.name = "'+song_proof+'" RETURN s'
            resultsMainSong = db.run(queryMainSong)
            duplicatedMainSong = ""

            for record in resultsMainSong:
                print(record["s"].properties['name'])
                duplicatedMainSong = record["s"].properties['name']

            if duplicatedMainSong != song_proof:
                db.run("CREATE (s:Song {name: {name}, level: {level}, artist: {artist}, main: {main}, id: {id}})",
                   {"name": song_info['name'], "level": level, "artist": song_info['album']['artists'][0]['name'], "main": True, "id": id})
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
            print(artistId)

            queryMainArtist = 'MATCH (a:Artist) WHERE a.name = "' + song_info['album']['artists'][0]['name'] + '" RETURN a'
            resultsMainArtist = db.run(queryMainArtist)
            duplicatedMainArtist = ""
            for record in resultsMainArtist:
                print(record["a"].properties['name'])
                duplicatedMainArtist = record["a"].properties['name']

            if duplicatedMainArtist != song_info['album']['artists'][0]['name']:
                db.run("CREATE (a:Artist {name: {name}, level: {level}, main: {main}, id: {id}})",
                        {"name": song_info['album']['artists'][0]['name'], "level": level, "main": True, "id": id})
                id = id + 1
            if duplicatedMainSong != song_proof:
                db.run('MATCH (s:Song),(a:Artist) WHERE s.artist ="' + song_info['album']['artists'][0]['name'] + '" AND a.name ="' + song_info['album']['artists'][0]['name'] + '" CREATE (a)-[r: ARTIST_SONG]->(s) RETURN r')
            # Related Artist's
            # sp = spotipy.Spotify(auth=token)
            related_artists = sp.artist_related_artists(artistId)

            for related_artist in related_artists['artists']:
                print(related_artist['id'])
                # Artist's related songs to the first one
                # Artist's albums

                # sp = spotipy.Spotify(auth=token)

                offset = 0
                limit = 2
                artist_albums_ids = []
                while True:
                    print("Aqui 1")
                    artist_albums = sp.artist_albums(related_artist['id'], album_type='album', offset=offset, limit=limit)
                    print("Aqui 2")
                    offset += len(artist_albums['items'])
                    print("Aqui 3")

                    for album in artist_albums['items']:
                        print("Aqui 4")
                        artist_albums_ids.append(album['id'])
                        # Artist's songs
                        print("Aqui 5")
                        for artist_albums_id in artist_albums_ids:
                            # sp = spotipy.Spotify(auth=token)
                            print("Aqui 6")
                            offset = 0
                            limit = 3
                            while True:
                                print("Aqui 7")
                                album_songs = sp.album_tracks(artist_albums_id, offset=offset, limit=limit)
                                print("Aqui 7b")
                                offset += len(album_songs['items'])
                                print("Aqui 7c")
                                cont = 1
                                print(album_songs['items'])
                                for song in album_songs['items']:
                                    print("Aqui 7d")
                                    track_info = sp.audio_features(song['id'])
                                    print("Aqui 8")
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
                                        print("Aqui 9")
                                        while i <= 7:
                                            if isinstance(actual_features[i], float):
                                                change_feature = abs(actual_features[i] - main_features[i]) + change_feature
                                            i = i + 1
                                        actual_features.clear()
                                        print("Aqui 10")
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

                                            # if related_artist not in related_artists_checked:
                                            related_artist_global = related_artist['name']

                                            queryRelatedArtist = 'MATCH (a:Artist) WHERE a.name = "' + \
                                                                 related_artist['name'] + '" RETURN a'
                                            resultsRelatedArtist = db.run(queryRelatedArtist)
                                            duplicatedRelatedArtist = ""
                                            for record in resultsRelatedArtist:
                                                print(record["a"].properties['name'])
                                                duplicatedRelatedArtist = record["a"].properties['name']

                                            if duplicatedRelatedArtist != related_artist['name']:
                                                cypher_artist = "CREATE (a:Artist {name: {name}, level: {level}, relatedartist: {relatedartist}, main: {main}, id: {id}})"
                                                db.run(cypher_artist,
                                                        {"name": related_artist['name'], "level": level, "relatedartist": main_artist, "main": False, "id": id})
                                                id = id + 1

                                                db.run('MATCH (ar:Artist),(ar2:Artist) WHERE ar.name = "' + main_artist + '" AND ar2.name = "' + related_artist['name'] + '" CREATE (ar)-[r: RELATED_ARTIST]->(ar2) RETURN r')

                                            queryRelatedSong = 'MATCH (s:Song) WHERE s.name = "' + song['name'] + '" RETURN s'
                                            resultsRelatedSong = db.run(queryRelatedSong)
                                            duplicatedRelatedSong = ""
                                            for record in resultsRelatedSong:
                                                print(record["s"].properties['name'])
                                                duplicatedRelatedSong = record["s"].properties['name']

                                            if duplicatedRelatedSong != song['name']:
                                                db.run("CREATE (s:Song {name: {name}, artist: {artist}, level: {level}, main: {main}, id: {id}})",
                                                        {"name": song['name'], "artist": song['artists'][0]['name'], "level": level, "main": False, "id": id})
                                                id = id + 1

                                                # Eliminamos las canciones sin grupo
                                                resultsSong = db.run(
                                                    'MATCH (s:Song) WHERE s.name = "' + song['name'] + '" RETURN s')
                                                print("Hace la primera llamada a la bbdd")
                                                pruebaCancion = ""
                                                for record in resultsSong:
                                                    print(record["s"].properties['artist'])
                                                    resultArtist = db.run('MATCH (a:Artist) WHERE a.name = "' + record["s"].properties['artist'] + '" RETURN a')
                                                    print("Hace la segunda llamada a la bbdd")
                                                    print("Llega 1")
                                                    for record2 in resultArtist:
                                                        print("Llega 2")
                                                        pruebaCancion = pruebaCancion + record2["a"].properties['name']
                                                        print("Llega 3")
                                                print("Llega 4")
                                                if pruebaCancion == "":
                                                    print("Llega 5")
                                                    db.run('MATCH (s:Song) WHERE s.name = "' + song['name'] + '" DELETE s')
                                                    print("Llega 6")
                                                    print("Hace la tercera llamada a la bbdd")


                                            related_song_global = song['name']
                                            if duplicatedRelatedSong != song['name']:
                                                db.run('MATCH (a { name: "' + related_artist['name'] + '" })-[r:ARTIST_SONG]->(s { artist: "' + related_artist['name'] + '"}) DELETE r')
                                                db.run('MATCH (s:Song),(a:Artist) WHERE s.artist ="' + related_artist['name'] +'" AND a.name ="' + related_artist['name'] +'" CREATE (a)-[r: ARTIST_SONG]->(s) RETURN r')
                                            related_artists_checked.append(related_artist)
                                    cont += 1

                                if len(album_songs['items']) < limit:
                                    break
                            break
                    if len(artist_albums['items']) < limit:
                        break

                # Eliminamos los artistas o grupos sin canciones

                print("Llega aqui!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                print(related_artist['name'])
                queryArtistNoSongs = 'MATCH (a:Artist) WHERE a.name = "' + str(related_artist['name']) + '" RETURN a'
                print(queryArtistNoSongs)
                resultsRelatedArtists = db.run(queryArtistNoSongs)
                print("aaaaaaaaaaaaaaaaaa")
                resultsNoSongs = []
                pruebaArtista = ""
                for record in resultsRelatedArtists:
                    print(record["a"].properties['name'])
                    pruebaArtista = pruebaArtista + record["a"].properties['name']
                if pruebaArtista != "":
                    print("Llamada de canciones")
                    resultsNoSongs = db.run('MATCH (s:Song) WHERE s.artist = "' + related_artist['name'] + '" RETURN s')

                # resultsNoSongs = db.run('MATCH (s:Song) WHERE s.artist = "' + related_artist['name'] + '" RETURN s')
                print("Aquí fijo que no llega")

                prueba = ""
                for record in resultsNoSongs:
                    print("prueba sin canciones----------------------------------")
                    print(record["s"].properties['name'])
                    prueba = prueba + record["s"].properties['name']
                if prueba == "":
                    print("Llamada de eliminacion del artista")
                    db.run('MATCH (a1:Artist) - [r] -> () WHERE a1.name = "' + related_artist['name'] + '" DELETE r')
                    db.run('MATCH (a1:Artist) - [r] -> (a2:Artist) WHERE a2.name = "' + related_artist['name'] + '" DELETE r')
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

    query_songs_main = 'MATCH (s:Song) WHERE s.main = True AND s.level = '+ str(level) +' RETURN s'
    songs_main = db.run(query_songs_main)
    for song in songs_main:
        song_properties = song['s'].properties
        aux = "aux"
        print(song_properties)
        # source = song_properties["id"]
        # if initial_graph:
        if level > 5:
            main_song_graph = {"id": song_properties["id"], "title": song_properties["name"], "label": "song" + str(5)}
            if initial_graph:
                nodes.append(main_song_graph)
        else:

            if initial_graph:
                main_song_graph = {"id": song_properties["id"], "title": song_properties["name"], "label": "song" + str(level)}
                print(main_song_graph)
                nodes.append(main_song_graph)
            else:
                for n in nodes:
                    if n["title"] == song_properties["name"]:
                        main_song_graph = n
                        break
        print(main_song_graph)
        source = nodes.index(main_song_graph)

    query_artists_main = 'MATCH (a:Artist) WHERE a.main = True AND a.level = '+ str(level) +' RETURN a'
    artists_main = db.run(query_artists_main)
    for artist in artists_main:
        artist_properties = artist['a'].properties
        print(artist_properties)
        if level > 5:
            print("Pasa 1")
            main_artist_graph = {"id": artist_properties["id"], "title": artist_properties["name"], "label": "artist" + str(5)}
            print("Pasa 2")
            if initial_graph:
                nodes.append(main_artist_graph)
            print("Pasa 3")
        else:
            print("Pasa 3")
            if initial_graph:
                main_artist_graph = {"id": artist_properties["id"], "title": artist_properties["name"], "label": "artist" + str(level)}
                nodes.append(main_artist_graph)
            else:
                print("Pasa 4")
                for n in nodes:
                    print("Pasa 5")
                    if n["title"] == artist_properties["name"]:
                        print("Pasa 6")
                        main_artist_graph = n
                        print("Pasa 7")
                        break
                    print("Pasa 8")
                print("Pasa 9")
        target = nodes.index(main_artist_graph)
        print("Pasa 10")
        if initial_graph:
            rels.append({"source": source, "target": target})

    query_related_artists = 'MATCH (a:Artist) WHERE a.main = False AND a.level = '+ str(level) +' RETURN a'
    print("Pasa 11")
    related_artists = db.run(query_related_artists)
    print("Pasa 12")
    source = target
    for related_artist in related_artists:
        print("Pasa 13")
        related_artist_properties = related_artist['a'].properties
        print("Pasa 14")
        # target = related_artist_properties["id"]
        if level > 5:
            print("Pasa 15")
            related_artist_graph = {"id": related_artist_properties["id"], "title": related_artist_properties["name"], "label": "artist" + str(5)}
            print("Pasa 16")
            nodes.append(related_artist_graph)
            print("Pasa 17")
        else:
            print("Pasa 18")
            related_artist_graph = {"id": related_artist_properties["id"], "title": related_artist_properties["name"], "label": "artist" + str(level)}
            print("Pasa 19")
            nodes.append(related_artist_graph)
        target = nodes.index(related_artist_graph)
        print("Pasa 20")
        rels.append({"source": source, "target": target})
        related_songs = db.run('MATCH (s:Song) WHERE s.level = ' + str(level) + ' AND s.artist = "' + related_artist_properties["name"] + '" AND s.main = False RETURN s')
        print("Pasa 21")
        source2 = target
        for related_song in related_songs:
            print("Pasa 22")
            related_song_properties = related_song['s'].properties
            # target = related_song_properties["id"]
            if level > 5:
                print("Pasa 23")
                related_song_graph = {"id": related_song_properties["id"], "title": related_song_properties["name"], "label": "song" + str(5)}
                nodes.append(related_song_graph)
            else:
                related_song_graph = {"id": related_song_properties["id"], "title": related_song_properties["name"], "label": "song" + str(level)}
                for n in nodes:
                    if n["title"] == related_song_properties["name"]:
                        related_song_graph = n
                        break
                print("Pasa 24")
                nodes.append(related_song_graph)
            target = nodes.index(related_song_graph)
            print("Pasa 25")
            rels.append({"source": source2, "target": target})

    # Nuevas canciones de un artista ya disponible en la bbdd
    previous_related_artists = db.run('MATCH (a:Artist) WHERE a.level < ' + str(level) + ' RETURN a')
    print("Pasa 26")
    for previous_related_artist in previous_related_artists:
        print("Pasa 27")
        previous_related_artist_properties = previous_related_artist["a"].properties
        print("Pasa 28")
        previous_related_artist_graph = {"id": previous_related_artist_properties["id"], "title": previous_related_artist_properties["name"], "label": "artist" + str(previous_related_artist_properties["level"])}
        print("Pasa 29")
        for n in nodes:
            if n["title"] == previous_related_artist_properties["name"]:
                previous_related_artist_graph = n
                break
        source = nodes.index(previous_related_artist_graph)
        print("Pasa 29 b")
        actual_related_songs = db.run('MATCH (s:Song) WHERE s.level = ' + str(level) + ' AND s.artist = "' + previous_related_artist_properties["name"] + '" RETURN s')
        print("Pasa 30")
        for actual_related_song in actual_related_songs:
            actual_related_song_properties = actual_related_song["s"].properties
            print("Pasa 31")
            if level > 5:
                print("Pasa 32")
                previous_related_song_graph = {"id": actual_related_song_properties["id"], "title": actual_related_song_properties["name"], "label": "song" + str(5)}
                print("Pasa 33")
                nodes.append(previous_related_song_graph)
                print("Pasa 34")
            else:
                print("Pasa 35")
                previous_related_song_graph = {"id": actual_related_song_properties["id"], "title": actual_related_song_properties["name"], "label": "song" + str(level)}
                for n in nodes:
                    if n["title"] == actual_related_song_properties["name"]:
                        previous_related_song_graph = n
                        break
                nodes.append(previous_related_song_graph)
            print("Pasa 36")
            target = nodes.index(previous_related_song_graph)
            print("Pasa 37")
            rels.append({"source": source, "target": target})

    for n in nodes:
        print(n)
    for r in rels:
        print(r)

    # print("Antes de la llamada: ", level)
    # level = level + 1
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
