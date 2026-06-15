from backend.app.services.retriever import retrieve_context
import json

res = retrieve_context("tại sao ko có context nào được trả về", threshold=0.0)
print(json.dumps(res, ensure_ascii=False, indent=2))
