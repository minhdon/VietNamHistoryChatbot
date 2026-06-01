import pandas as pd
from sqlalchemy import create_engine
from tqdm import tqdm

# 1. Cấu hình kết nối Docker Postgres (Port 5435)
DATABASE_URL = "postgresql://minh_admin:123456789@localhost:5435/history_rag"
engine = create_engine(DATABASE_URL)

# 2. Đọc toàn bộ file Parquet vào RAM (Parquet rất nhẹ nên 1M dòng load phát một)
print("🔄 Đang đọc file Parquet vào bộ nhớ...")
df = pd.read_parquet("../data/dataset_chats.parquet")

TABLE_NAME = "historical_chats"  # Đã sửa lỗi chính tả 'hitorical'
batch_size = 5000  # Số dòng mỗi lần đẩy vào DB
total_rows = len(df)

print(f"📦 Tổng số dòng cần nạp: {total_rows:,}")

# 3. Tiến hành chia batch và nạp vào DB
with tqdm(total=total_rows, desc="Đang nạp dữ liệu") as pbar:
    for i in range(0, total_rows, batch_size):
        # Cắt một cụm dữ liệu từ df
        chunk = df.iloc[i : i + batch_size]
        
        # Lần đầu tiên (i == 0) thì ghi đè (replace) để làm sạch bảng cũ nếu có. 
        # Các lần sau thì chèn thêm vào (append)
        if i == 0:
            chunk.to_sql(TABLE_NAME, engine, if_exists='replace', index=False)
        else:
            chunk.to_sql(TABLE_NAME, engine, if_exists='append', index=False)
            
        # Cập nhật thanh tiến trình
        pbar.update(len(chunk))

print(f"\n🎉 Hoàn thành! Toàn bộ dữ liệu đã được lưu trữ an toàn trong bảng '{TABLE_NAME}'!")