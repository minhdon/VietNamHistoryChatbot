import sys
from backend.app.utils.db_neo4j import neo4j_db

res = neo4j_db.query("CALL apoc.help('apoc')")
if res is None:
    print("APOC IS NOT INSTALLED OR QUERY FAILED")
else:
    print("APOC IS INSTALLED")
