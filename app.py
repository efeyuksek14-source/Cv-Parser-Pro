import streamlit as st
import re
import json
from PyPDF2 import PdfReader
import docx
from google import genai
from google.genai import types

# ----------------------------------------
# 🔑 APİ AYARI (Artık şifre güvenli kasadan okunuyor!)
# ----------------------------------------
try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = "Şifre Bulunamadı"

# 1. Dosyalardan Metin Okuma Fonksiyonları
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    try:
        doc = docx.Document(file)
        text_parts = []
        for para in doc.paragraphs:
            if para.text.strip():
                text_parts.append(para.text)
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    if cell.text.strip():
                        text_parts.append(cell.text)
        return "\n".join(text_parts)
    except Exception as e:
        return f"Word dosyası okunurken hata oluştu: {str(e)}"

# 2. Yapay Zeka ile Bilgi Ayıklama Fonksiyonu
def analyze_cv_with_ai(cv_text):
    try:
        if GEMINI_API_KEY == "Şifre Bulunamadı":
            return {"Hata": "Streamlit Settings -> Secrets kısmına GEMINI_API_KEY eklenmemiş!"}
            
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        Aşağıdaki CV metnini analiz et ve bilgileri tam olarak şu JSON formatında ayıkla.
        Hiçbir yorum yapma, sadece saf JSON döndür.
        
        CRITICAL INSTRUCTION FOR LISTS: 
        "Egitim" ve "Deneyim" alanlarını asla tek bir paragraf veya düz metin olarak yazma. 
        Her bir okulu ve her bir iş deneyimini bir liste (array) elemanı olarak ayır. 
        Her iş deneyimi maddesi şu düzende olsun: "Şirket Adı - Pozisyon (Başlangıç - Bitiş Tarihi) / Varsa yapılan işlerin kısa özeti"
        
        Format:
        {{
            "Ad Soyad": "",
            "Telefon": "",
            "E-posta": "",
            "Adres": "Adayın açık adresi, şehir veya ikametgah bilgisi",
            "Egitim": ["Okul 1 - Bölüm (Mezuniyet Yılı)", "Okul 2 - Bölüm (Yıl)"],
            "Deneyim": ["Şirket 1 - Pozisyon (Yıl-Yıl) - Görev özeti", "Şirket 2 - Pozisyon (Yıl-Yıl)"],
            "Yetenekler": "Adayın bildiği diller, programlar ve yetenekler (Virgülle ayrılmış şık bir metin)",
            "Vize Pasaport": "Eğer varsa vize ve pasaport durumları, yoksa Belirtilmemiş yaz",
            "Referanslar": "Eğer varsa referans kişileri ve bilgileri"
        }}
        
        CV Metni:
        {cv_text}
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        clean_text = response.text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.replace("
```json", "", 1)
        if clean_text.endswith("
