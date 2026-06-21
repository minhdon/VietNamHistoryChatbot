from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('keepitreal/vietnamese-sbert', device='cpu')

q1 = "Hồ Chí Minh tên khai sinh là gì"
doc_db = "Chủ tịch Hồ Chí Minh (1890–1969), tên khai sinh là Nguyễn Sinh Cung. Người là lãnh tụ vĩ đại của cách mạng Việt Nam, nhà sáng lập Đảng Cộng sản Việt Nam và Chủ tịch nước đầu tiên. Cả cuộc đời Người đã cống hiến cho sự nghiệp giải phóng dân tộc và thống nhất đất nước.Tiểu sử của Người được tóm tắt qua các cột mốc chính:Thời niên thiếu (1890–1910): Sinh ngày 19/5/1890 tại làng Kim Liên, huyện Nam Đàn, tỉnh Nghệ An."

print("Similarity:", util.cos_sim(model.encode(q1), model.encode(doc_db)).item())
