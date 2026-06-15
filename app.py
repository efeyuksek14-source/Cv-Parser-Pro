import streamlit as st
import json
from PyPDF2 import PdfReader
import docx
from google import genai
from pymongo import MongoClient
import datetime

# ----------------------------------------
# 🔑 ŞİFRELER VE BAĞLANTILAR (Secrets)
# ----------------------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
MONGO_URI = st.secrets.get("MONGO_URI", "")

# MongoDB Bağlantısı
@st.cache_resource
def init_mongodb():
    if MONGO_URI:
        try:
            client = MongoClient(MONGO_URI)
            db = client["cv_db"]
            return db["cv_collection"]
        except Exception as e:
            st.error(f"Veritabanı bağlantı hatası: {str(e)}")
            return None
    return None

db_collection = init_mongodb()

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
        if not GEMINI_API_KEY:
            return {"Hata": "Streamlit Secrets alanına GEMINI_API_KEY eklenmemiş!"}
            
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        prompt = f"""
        Aşağıdaki CV metnini analiz et ve bilgileri tam olarak şu JSON formatında ayıkla.
        Hiçbir yorum yapma, sadece saf JSON döndür.
        
        Format:
        {{
            "Ad Soyad": "",
            "Telefon": "",
            "E-posta": "",
            "Adres": "Adayın açık adresi, şehir veya ikametgah bilgisi",
            "Egitim": ["Okul 1 - Bölüm (Mezuniyet Yılı)"],
            "Deneyim": ["Şirket 1 - Pozisyon (Yıl-Yıl) - Görev özeti"],
            "Yetenekler": "Adayın bildiği diller, programlar (Virgülle ayrılmış metin)",
            "Vize Pasaport": "Vize ve pasaport durumları, yoksa Belirtilmemiş yaz",
            "Referanslar": "Referans kişileri ve bilgileri"
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
            clean_text = clean_text.replace("```json", "", 1)
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
            
        return json.loads(clean_text.strip())
    except Exception as e:
        return {"Hata": f"Yapay zeka analiz edemedi: {str(e)}"}

# 3. Streamlit Arayüz Tasarımı
st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .bullet-item { background-color: #f8fafc; padding: 10px 15px; border-left: 4px solid #3b82f6; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Yapay Zeka Destekli CV Analiz Merkezi")
st.write("Yüklediğiniz özgeçmişleri analiz eder, sonuçları veritabanında saklar.")
st.write("---")

col_left, col_right = st.columns([1, 1.5])

with col_left:
    st.subheader("📁 Özgeçmiş Yükleme")
    uploaded_file = st.file_uploader("PDF veya Word formatında bir dosya seçin", type=["pdf", "docx"])
    
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            raw_text = read_pdf(uploaded_file)
        else:
            raw_text = read_docx(uploaded_file)
            
        st.success("🔄 Dosya başarıyla sisteme yüklendi.")
        
        st.write("---")
        if st.button("🚀 Yapay Zeka İle Analiz Et", type="primary"):
            with st.spinner("Yapay zeka CV'yi inceliyor..."):
                ai_result = analyze_cv_with_ai(raw_text)
                st.session_state.ai_results = ai_result
                
                # VERİTABANINA KAYDETME İŞLEMİ
                if db_collection is not None and "Hata" not in ai_result:
                    ai_result["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    db_collection.insert_one(ai_result)
                    st.success("💾 Analiz sonucu başarıyla kaydedildi!")

with col_right:
    st.subheader("📊 Anlık Sonuç")
    if 'ai_results' in st.session_state:
        res = st.session_state.ai_results
        if "Hata" in res:
            st.error(res["Hata"])
        else:
            st.balloons()
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 👤 Kişisel Bilgiler")
            st.write(f"**Adı Soyadı:** {res.get('Ad Soyad', 'Belirtilmemiş')}")
            st.write(f"**📞 Telefon:** {res.get('Telefon', 'Belirtilmemiş')}")
            st.write(f"**📧 E-posta:** {res.get('E-posta', 'Belirtilmemiş')}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 💼 İş Tecrübeleri")
            for is_madde in res.get('Deneyim', []):
                st.markdown(f'<div class="bullet-item">💼 {is_madde}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Yüklediğiniz CV'nin anlık sonucu burada görünecektir.")

# --- TEMİZLENMİŞ VERİTABANI GEÇMİŞİ BÖLÜMÜ ---
st.write("---")
st.subheader("🗄️ Geçmiş CV Analizleri")

if db_collection is not None:
    try:
        kayitlar = list(db_collection.find().sort("_id", -1))
        
        if len(kayitlar) > 0:
            for kayit in kayitlar:
                with st.expander(f"📄 {kayit.get('Ad Soyad', 'İsimsiz Aday')} - {kayit.get('kayit_tarihi', '')}"):
                    st.write(f"**📞 Telefon:** {kayit.get('Telefon', '-')}")
                    st.write(f"**📧 E-posta:** {kayit.get('E-posta', '-')}")
                    st.write(f"**💡 Yetenekler:** {kayit.get('Yetenekler', '-')}")
                    st.write("**💼 Deneyimler:**")
                    for d in kayit.get('Deneyim', []):
                        st.write(f"- {d}")
        else:
            st.info("Henüz geçmiş bir analiz bulunmuyor. İlk analizi yaptığınızda burada listelenecektir.")
    except Exception as e:
        st.error(f"Veriler listelenirken hata oluştu: {str(e)}")
else:
    st.warning("Veritabanı bağlantısı kurulamadı. Lütfen Secrets ayarlarını kontrol edin.")
