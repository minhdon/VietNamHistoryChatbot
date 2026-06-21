from backend.app.utils.db_neo4j import neo4j_db
from backend.app.services.retriever import model
from sentence_transformers import util

# 1. Query from DB (MPS generated)
res = neo4j_db.query("MATCH (c:Chunk {id: 'chunk_admin_c4713043'}) RETURN c.embedding")
emb_db = res[0]["c.embedding"]

# 2. Query text
text = "Hồ Chí Minh tên khai sinh là gì"
emb_q = model.encode(text).tolist()

print("Similarity to query:", util.cos_sim(emb_db, emb_q).item())

# 3. What if we re-embed the chunk text with CPU?
res_text = neo4j_db.query("MATCH (c:Chunk {id: 'chunk_admin_c4713043'}) RETURN c.text")
text_db = res_text[0]["c.text"]
emb_cpu = model.encode(text_db).tolist()
print("Similarity between CPU and MPS embeddings of the SAME text:", util.cos_sim(emb_db, emb_cpu).item())

print("Similarity to query IF using CPU for both:", util.cos_sim(emb_cpu, emb_q).item())
