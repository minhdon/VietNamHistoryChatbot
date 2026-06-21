from backend.app.services.retriever import retrieve_context

print(retrieve_context("Hồ Chí Minh tên khai sinh là gì", top_k=5, threshold=0.1))
