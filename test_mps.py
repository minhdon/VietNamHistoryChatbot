from sentence_transformers import SentenceTransformer

model_mps = SentenceTransformer('keepitreal/vietnamese-sbert', device='mps')
vec_mps = model_mps.encode("Hồ Chí Minh mất ngày mấy")

model_cpu = SentenceTransformer('keepitreal/vietnamese-sbert', device='cpu')
vec_cpu = model_cpu.encode("Hồ Chí Minh mất ngày mấy")

print("MPS vector sum:", sum(vec_mps))
print("CPU vector sum:", sum(vec_cpu))
print("Difference:", sum(abs(vec_mps - vec_cpu)))
