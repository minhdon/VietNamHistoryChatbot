from backend.app.utils.db_neo4j import neo4j_db

query = """
MATCH (c:Chunk)
WITH c, replace(replace(toString(c.id), 'chunk_admin_', ''), 'chunk_', '') AS str_id
WHERE str_id =~ '^[0-9]+$'
RETURN max(toInteger(str_id)) AS max_id
"""
print(neo4j_db.query(query))
