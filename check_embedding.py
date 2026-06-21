from backend.app.utils.db_neo4j import neo4j_db

res = neo4j_db.query("MATCH (c:Chunk {id: 'chunk_admin_c4713043'}) RETURN c.text, size(c.embedding) as emb_size")
print(res)

res2 = neo4j_db.query("MATCH (c:Chunk {id: '21942'}) RETURN c.text, size(c.embedding) as emb_size")
print(res2)
