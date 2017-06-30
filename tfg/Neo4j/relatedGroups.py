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
    # Imagine Dragons
    artist_id = '53XhwfbYqKCa1cC15pYq2q'
    sp = spotipy.Spotify(auth=token)
    artist_info = sp.artist_related_artists(artist_id)
    for g in artist_info['artists']:
        # print('\nGroup Name(Level 1):', g['name'])
        session.run("CREATE (a:Artist {name: {name}, level: {level}})",
                    {"name": g['name'], "level": 1})
        artist_id2 = g['id']
        artist_info2 = sp.artist_related_artists(artist_id2)
        for h in artist_info2['artists']:
            # print('\n\tGroup Name(Level 2):', h['name'])
            session.run("CREATE (a:Artist {name: {name}, level: {level}})",
                        {"name": h['name'], "level": 2})
            artist_id3 = h['id']
            artist_info3 = sp.artist_related_artists(artist_id3)
            for i in artist_info3['artists']:
                # print('\n\t\tGroup Name(Level 3):', i['name'])
                session.run("CREATE (a:Artist {name: {name}, level: {level}})",
                            {"name": i['name'], "level": 3})
else:
    print("Can't get token for", username)

result = session.run("MATCH (a:Artist)"
                     "RETURN a.name AS name, a.level AS level")

for record in result:
    print("%s %s " % (record["name"], record["level"]))

session.close()