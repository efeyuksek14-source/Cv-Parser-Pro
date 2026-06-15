import streamlit as st
import re
import json
from PyPDF2 import PdfReader
import docx
from google import genai
from google.genai import types

# ----------------------------------------
# 🔑 APİ AYARI
# ----------------------------------------
GEMINI_API_KEY = "AQ.Ab8RN6KFWgC_WIooKDLai8-_JY1biFgcSu0BI7zApyehuFjKBg"

# 1. Dosyalardan Metin Okuma Fonksiyonları
def read_pdf(file):
    pdf_reader = PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text

def read_docx(file):
    doc = docx.Document(file)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"
    return text

# 2. Yapay Zeka ile Bilgi Ayıklama Fonksiyonu (Maddeleme Zorunlu Kılınmış Sürüm)
def analyze_cv_with_ai(cv_text):
    try:
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
            clean_text = clean_text.replace("```json", "", 1)
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
            
        return json.loads(clean_text.strip())
    except Exception as e:
        return {"Hata": f"Yapay zeka analiz edemedi: {str(e)}"}

# 3. Streamlit Arayüz Tasarımı
st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

# Kurumsal Şık Stil Ayarları
st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .bullet-item { background-color: #f8fafc; padding: 10px 15px; border-left: 4px solid #3b82f6; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Yapay Zeka Destekli CV Analiz Merkezi")
st.write("Yüklediğiniz özgeçmişleri saniyeler içinde analiz eder, kritik bilgileri yapılandırılmış olarak sunar.")
st.write("---")

# Sayfa Düzeni
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
            with st.spinner("Yapay zeka CV'yi satır satır inceliyor..."):
                st.session_state.ai_results = analyze_cv_with_ai(raw_text)

with col_right:
    st.subheader("📊 Yapılandırılmış Sonuçlar")
    
    if 'ai_results' in st.session_state:
        res = st.session_state.ai_results
        
        if "Hata" in res:
            st.error(res["Hata"])
        else:
            st.balloons()
            
            # 1. Kişisel Bilgiler
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 👤 Kişisel & İletişim Bilgileri")
            st.markdown(f"**Adı Soyadı:** {res.get('Ad Soyad', 'Belirtilmemiş')}")
            st.markdown(f"**📞 Telefon:** {res.get('Telefon', 'Belirtilmemiş')}")
            st.markdown(f"**📧 E-posta:** {res.get('E-posta', 'Belirtilmemiş')}")
            st.markdown(f"**🏠 Adres:** {res.get('Adres', 'Belirtilmemiş')}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 2. Vize Durumu
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 🛂 Vize & Pasaport Durumu")
            st.write(res.get('Vize Pasaport', 'Belirtilmemiş'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 3. Eğitim Geçmişi (Madde Madde)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 🎓 Eğitim Geçmişi")
            egitim_listesi = res.get('Egitim', [])
            if isinstance(egitim_listesi, list) and len(egitim_listesi) > 0:
                for okul in egitim_listesi:
                    st.markdown(f'<div class="bullet-item">🔹 {okul}</div>', unsafe_allow_html=True)
            else:
                st.write(str(egitim_listesi) if egitim_listesi else "Belirtilmemiş")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 4. İş Tecrübeleri (İSTEDİĞİN MADDE MADDE TASARIM)
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 💼 İş Tecrübeleri")
            deneyim_listesi = res.get('Deneyim', [])
            if isinstance(deneyim_listesi, list) and len(deneyim_listesi) > 0:
                for iş in deneyim_listesi:
                    st.markdown(f'<div class="bullet-item">💼 {iş}</div>', unsafe_allow_html=True)
            else:
                st.write(str(deneyim_listesi) if deneyim_listesi else "Belirtilmemiş")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 5. Yetenekler
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 💡 Yetenekler & Beceriler")
            st.write(res.get('Yetenekler', 'Belirtilmemiş'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            # 6. Referanslar
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 🤝 Referanslar")
            st.write(res.get('Referanslar', 'Belirtilmemiş'))
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("Sol taraftan bir CV yükleyip analiz butonuna bastığınızda, yapay zekanın ayıkladığı temiz veriler burada listelenecektir.")