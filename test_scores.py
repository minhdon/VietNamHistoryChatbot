from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='cpu')

q1 = "Hồ Chí Minh tên khai sinh là gì"
q2 = "Hồ Chí Minh mất ngày nào"
q3 = "Hồ Chí Minh sinh ra ở đâu"

doc_hqly = "Hỏi: Hãy mô tả ngắn gọn bối cảnh và ý nghĩa của Hồ Quý Ly lập nhà Hồ.\nĐáp: 1400: Hồ Quý Ly lập nhà Hồ."
doc_hcm = "Chủ tịch Hồ Chí Minh (1890–1969), tên khai sinh là Nguyễn Sinh Cung."
doc_hcm_q = "Hỏi: Hồ Chí Minh tên khai sinh là gì?\nĐáp: Nguyễn Sinh Cung"

emb_q1 = model.encode(q1)
emb_hqly = model.encode(doc_hqly)
emb_hcm = model.encode(doc_hcm)
emb_hcm_q = model.encode(doc_hcm_q)

print("Q1 vs HQly:", util.cos_sim(emb_q1, emb_hqly).item())
print("Q1 vs HCM_doc:", util.cos_sim(emb_q1, emb_hcm).item())
print("Q1 vs HCM_QA:", util.cos_sim(emb_q1, emb_hcm_q).item())
