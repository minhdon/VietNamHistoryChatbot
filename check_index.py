from app.services.retriever import driver

with driver.session() as session:
    res = session.run("SHOW INDEXES YIELD name, type, labelsOrTypes, properties")
    for r in res:
        print(f"Name: {r['name']}, Type: {r['type']}, Labels: {r['labelsOrTypes']}, Props: {r['properties']}")
