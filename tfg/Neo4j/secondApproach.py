from neo4j.v1 import GraphDatabase, basic_auth

driver = GraphDatabase.driver("bolt://localhost:7687", auth=basic_auth("neo4j", "neo4j"))
session = driver.session()

session.run("CREATE (a:Person {name: {name}, title: {title}})",
            {"name": "Arthur", "title": "King"})

session.run("CREATE (a:Person {name: {name}, title: {title}})",
            {"name": "Sophie", "title": "Queen"})

result = session.run("MATCH (a:Person)"
                     "RETURN a.name AS name, a.title AS title")

for record in result:
    print("%s %s" % (record["title"], record["name"]))

session.close()
