from backend.app.utils.db_neo4j import neo4j_db

query = """
MATCH (c:Chunk)
WHERE toString(c.id) =~ '^[0-9]+$'
RETURN c.id
"""
print(neo4j_db.query(query))
