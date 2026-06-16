# backend/app/routers/ocr.py
from fastapi import APIRouter, UploadFile, File, HTTPException
import pytesseract
from PIL import Image
import pypdf
import io

router = APIRouter(
    prefix="/api/ocr",
    tags=["OCR"]
)

@router.post("/extract")
async def extract_text_from_file(file: UploadFile = File(...)):
    filename = file.filename.lower()
    extracted_text = ""

    try:
        # Đọc file thành dữ liệu bytes đi vào bộ nhớ RAM (không cần lưu xuống ổ cứng)
        file_bytes = await file.read()

        # 📸 TRƯỜNG HỢP 1: FILE LÀ ẢNH (PNG, JPG, JPEG, WEBP)
        if filename.endswith(('.png', '.jpg', '.jpeg', '.webp')):
            image = Image.open(io.BytesIO(file_bytes))
            # Chạy Tesseract OCR cấu hình nhận diện cả tiếng Việt (vie) và tiếng Anh (eng)
            extracted_text = pytesseract.image_to_string(image, lang='vie+eng')

        # 📄 TRƯỜNG HỢP 2: FILE LÀ PDF
        elif filename.endswith('.pdf'):
            pdf_file = io.BytesIO(file_bytes)
            reader = pypdf.PdfReader(pdf_file)
            
            # Duyệt qua từng trang của file PDF để gom chữ lại
            page_texts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    page_texts.append(text)
            
            extracted_text = "\n".join(page_texts)

        else:
            raise HTTPException(status_code=400, detail="Hệ thống chỉ hỗ trợ file PDF hoặc file Ảnh (PNG, JPG, JPEG).")

        # Làm sạch chuỗi text thu được (bỏ khoảng trắng thừa)
        extracted_text = extracted_text.strip()
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="Không thể bóc tách được chữ từ file này (Ảnh quá mờ hoặc PDF trống).")

        return {"status": "success", "extracted_text": extracted_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý OCR: {str(e)}")