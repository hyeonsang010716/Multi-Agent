import pdfplumber
pdf_path = "pdf_extraction/1.기업가치.pdf"
pdf = pdfplumber.open(pdf_path)
pages = pdf.pages
text = []
for page in pages:
    sub = page.extract_text()
    text.append(sub)
    
# 리스트에 저장된 텍스트를 하나의 문자열로 결합
full_text = "\n".join(text)

# 텍스트 파일로 저장
with open("extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

# PDF 파일 닫기
pdf.close()