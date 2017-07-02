import json

from neo4j.v1 import GraphDatabase, basic_auth
import spotipy
import spotipy.util as util
import sys

scope = 'user-library-read'

username = 'srivasdelgado'

token = util.prompt_for_user_token(username, scope)
print(token)

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
session = driver.session()


if token:
    # Night Visions
    album_id = '1vAEF8F0HoRFGiYOEeJXHW'
    sp = spotipy.Spotify(auth=token)
    count = sys.maxsize
    cont = 1
    offset = 0
    limit = 50
    while True:
        album_info = sp.album_tracks(album_id, offset=offset, limit=limit)
        album_name = sp.album(album_id)
        offset += len(album_info['items'])
        # print(json.dumps(album_name, indent=1))
        session.run("CREATE (a:Album {name: {name}})",
                    {"name": album_name['name']})
        for song in album_info['items']:
            print('Song', cont, ':', song['name'])
            session.run("CREATE (s:Song {name: {name}, track: {track}})",
                        {"name": song['name'], "track": cont})
            cont += 1
        session.run("MATCH (s:Song),(a:Album) CREATE (s)-[r: ALBUM]->(a) RETURN r")
        if len(album_info['items']) < limit:
            break
else:
    print("Can't get token for", username)

session.close()