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
    artist_id = '53XhwfbYqKCa1cC15pYq2q'
    sp = spotipy.Spotify(auth=token)
    albums = sp.artist_albums(artist_id=artist_id, album_type='album')
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
                track_info = sp.audio_features(song['id'])
                for feature in track_info:
                    session.run(
                        "CREATE (a:Song {name: {name}, danceability: {danceability}, energy: {energy}, liveness: {liveness}",
                        {"name": song['name'], "danceability": feature['danceability'], "energy": feature['energy'], "liveness": feature['liveness']})
                cont += 1
            if len(album_info['items']) < limit:
                break
else:
    print("Can't get token for", username)

result = session.run("MATCH (a:Song)"
                     "RETURN a.name AS name, a.danceability AS danceability, a.energy AS energy, liveness AS liveness")

for record in result:
    print("%s %s %s %s" % (record["name"], record["danceability"], record["energy"], record["liveness"]))

session.close()
