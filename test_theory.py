from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='cpu')

q1 = "Hồ Chí Minh tên khai sinh là gì"

doc_db = "Hỏi: Thông tin về Hồ Chí Minh\nĐáp: Chủ tịch Hồ Chí Minh (1890–1969), tên khai sinh là Nguyễn Sinh Cung. Người là lãnh tụ vĩ đại của cách mạng Việt Nam."
doc_hqly = "Hỏi: Hãy mô tả ngắn gọn bối cảnh và ý nghĩa của Hồ Quý Ly lập nhà Hồ.\nĐáp: 1400: Hồ Quý Ly lập nhà Hồ."

print("Similarity to modified DB doc:", util.cos_sim(model.encode(q1), model.encode(doc_db)).item())
print("Similarity to HQly doc:", util.cos_sim(model.encode(q1), model.encode(doc_hqly)).item())
