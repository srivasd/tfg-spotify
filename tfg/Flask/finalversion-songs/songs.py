#!/usr/bin/env python
from json import dumps
from sys import maxsize

from flask import Flask, g, Response
from neo4j.v1 import GraphDatabase, basic_auth
from spotipy import Spotify
from spotipy.util import prompt_for_user_token

app = Flask(__name__, static_url_path='/static/')
# driver = GraphDatabase.driver('bolt://localhost')
driver = GraphDatabase.driver('bolt://localhost', auth=basic_auth("neo4j", "neo4j"))


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
    scope = 'user-library-read'

    username = 'srivasdelgado'

    token = prompt_for_user_token(username, scope)
    print(token)
    db = get_db()

    if token:
        # Night Visions
        album_id = '1vAEF8F0HoRFGiYOEeJXHW'
        sp = Spotify(auth=token)
        count = maxsize
        cont = 1
        offset = 0
        limit = 50
        while True:
            album_info = sp.album_tracks(album_id, offset=offset, limit=limit)
            album_name = sp.album(album_id)
            offset += len(album_info['items'])
            db.run("CREATE (a:Album {name: {name}})",
                   {"name": album_name['name']})
            for song in album_info['items']:
                print('Song', cont, ':', song['name'])
                db.run("CREATE (s:Song {name: {name}, track: {track}})",
                       {"name": song['name'], "track": cont})
                cont += 1
            db.run("MATCH (s:Song),(a:Album) CREATE (s)-[r: ALBUM]->(a) RETURN r")
            if len(album_info['items']) < limit:
                break
    else:
        print("Can't get token for", username)

    return app.send_static_file('index.html')


def serialize_song(song):
    return {
        'id': song['id'],
        'name': song['name'],
        'track': song['track'],
    }


def serialize_album(album):
    return {
        'name': album['name'],
    }


@app.route("/graph")
def get_graph():
    db = get_db()
    nodes = []
    rels = []
    i = 0
    print('--------------------GRAPH INFORMATION--------------------')
    albums = db.run("MATCH (a:Album) RETURN a")
    for album in albums:
        album_properties = album['a'].properties
        nodes.append({"title": album_properties["name"], "label": "album"})
        target = i
        i += 1
        print("Album: ", album_properties['name'])
        results = db.run("MATCH (s:Song) RETURN s")
        for song in results:
            song_properties = song['s'].properties
            print("Song: ", song_properties['name'], " - ", "Track: ", song_properties['track'])
            song_node = {"title": song_properties["name"], "label": "song"}
            try:
                source = nodes.index(song_node)
            except ValueError:
                nodes.append(song_node)
                source = i
                i += 1
            rels.append({"source": source, "target": target})
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
