from backend.app.utils.db_neo4j import neo4j_db

res = neo4j_db.query("SHOW INDEXES YIELD * WHERE type = 'VECTOR'")
for r in res:
    print(r)
