import streamlit as res_st
import datetime
import time
import hashlib
import json
from pymongo import MongoClient
import google.generativeai as genai
from pypdf import PdfReader

# Sayfa Ayarları
res_st.set_page_config(page_title="ParserFlow - Akıllı ATS", page_icon="🚀", layout="wide")

res_st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .category-box { background-color: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #475569; display: inline-block; margin-bottom: 10px; margin-right: 5px;}
    .email-box { background-color: #f8fafc; padding: 15px; border: 1px dashed #cbd5e1; border-radius: 8px; font-family: monospace; white-space: pre-wrap; font-size: 13px; color: #334155; margin-top: 10px;}
    </style>
""", unsafe_allow_html=True)

res_st.title("🚀 ParserFlow - Yapay Zeka Destekli Gelişmiş CV Yönetim Merkezi")

# MongoDB Bağlantısı
@res_st.cache_resource
def init_connection():
    return MongoClient(res_st.secrets["mongo_uri"])

try:
    client = init_connection()
    db = client["parserflow_db"]
    users_col = db["users"]
    cvs_col = db["cvs"]
except Exception as e:
    res_st.error("⚠️ Veritabanı bağlantısı kurulamadı. Secrets ayarlarını kontrol edin.")
    res_st.stop()

# Gemini API Yapılandırması
try:
    genai.configure(api_key=res_st.secrets["GEMINI_API_KEY"])
except Exception as e:
    res_st.error("⚠️ Gemini API Key bulunamadı.")

def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def analyze_cv_real(file_text):
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"""
    Sen uzman bir İnsan Kaynakları yapay zeka asistanısın. Aşağıda metni verilen CV'yi incele ve bilgileri MÜKEMMEL BİR JSON FORMATINDA çıkar.
    Sadece geçerli bir JSON objesi döndür, başka hiçbir açıklama veya markdown bloğu (```json gibi) ekleme.

    İstenen JSON Formatı:
    {{
        "Ad Soyad": "Adayın Adı Soyadı",
        "Telefon": "Telefon numarası veya Bulunamadı",
        "E-posta": "E-posta adresi veya Bulunamadı",
        "Adres": "Şehir/Adres bilgisi veya Bulunamadı",
        "Deneyim": ["Şirket 1 - Pozisyon (Yıl)", "Şirket 2 - Pozisyon"],
        "Yetenekler": "Öne çıkan yetenekler ve teknolojiler"
    }}

    CV Metni:
    {file_text}
    """
    response = model.generate_content(prompt)
    raw_response = response.text.strip().replace("```json", "").replace("```", "")
    try:
        data = json.loads(raw_response)
    except:
        data = {
            "Ad Soyad": "Analiz Edilemedi",
            "Telefon": "Bulunamadı",
            "E-posta": "Bulunamadı",
            "Adres": "Bulunamadı",
            "Deneyim": [raw_response[:100]],
            "Yetenekler": "Genel"
        }
    return data

def generate_email_template(aday_isim, durum):
    if durum == "Olumlu":
        return f"Konu: İş Başvurusu Sonucu - Mülakat Daveti\n\nSayın {aday_isim},\n\nŞirketimize yapmış olduğunuz özgeçmiş başvurusu ekiplerimiz tarafından detaylıca incelenmiş ve tecrübeleriniz pozisyonumuz için oldukça olumlu bulunmuştur.\n\nSizinle daha yakından tanışmak ve pozisyon detaylarını görüşmek üzere en kısa sürede bir online mülakat planlamak istiyoruz.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    elif durum == "Olumsuz":
        return f"Konu: İş Başvurusu Sonucu Bilgilendirmesi\n\nSayın {aday_isim},\n\nŞirketimize göstermiş olduğunuz ilgi için teşekkür ederiz. Başvurunuz incelenmiş ancak farklı bir aday ile devam etme kararı alınmıştır.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    elif durum == "Nötr":
        return f"Konu: İş Başvurusu Durumu - Değerlendirme Süreci\n\nSayın {aday_isim},\n\nŞirketimize yapmış olduğunuz iş başvurusu havuzumuza başarıyla kaydedilmiştir. Değerlendirmelerimiz devam etmektedir.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    else:
        return f"Konu: Başvurunuz Hakkında\n\nSayın {aday_isim},\n\nİş başvurunuz sistemimize ulaştı.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"

if 'logged_in' not in res_st.session_state:
    res_st.session_state.logged_in = False
if 'user_email' not in res_st.session_state:
    res_st.session_state.user_email = ""
if 'current_analysis' not in res_st.session_state:
    res_st.session_state.current_analysis = None

# GİRİŞ / KAYIT EKRANI
if not res_st.session_state.logged_in:
    col_auth_left, col_auth_right = res_st.columns([1, 1.2])
    
    with col_auth_left:
        res_st.subheader("🔐 ParserFlow Erişim Paneli")
        auth_mode = res_st.radio("Yapmak İstediğiniz İşlem:", ["Giriş Yap", "Kayıt Ol (Ücretsiz Dene)"])
        
        email = res_st.text_input("E-posta Adresi").strip()
        password = res_st.text_input("Şifre", type="password")
        
        if auth_mode == "Kayıt Ol (Ücretsiz Dene)":
            paket_secimi = res_st.selectbox("Satın Alınacak Giriş Paketi", [
                "Başlangıç Paketi (10$ - 100 CV)", 
                "Profesyonel Paket (15$ - 500 CV)", 
                "Kurumsal Paket (25$ - Sınırsız CV)"
            ])
            if res_st.button("Hesabımı Oluştur"):
                if email and password:
                    existing_user = users_col.find_one({"email": email})
                    if existing_user:
                        res_st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        hak = 100 if "10$" in paket_secimi else (500 if "15$" in paket_secimi else 9999)
                        p_isim = "Başlangıç" if "10$" in paket_secimi else ("Profesyonel" if "15$" in paket_secimi else "Sınırsız (Kurumsal)")
                        bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                        
                        new_user_data = {
                            "email": email,
                            "password": make_hashes(password), 
                            "paket_turu": p_isim, 
                            "abonelik_durumu": "aktif", 
                            "abonelik_bitis": bitis_tarihi, 
                            "kalan_hak": hak,
                            "toplam_hak": hak,
                            "kategoriler": ["Genel"]
                        }
                        users_col.insert_one(new_user_data)
                        res_st.success("🎉 Kayıt başarılı! MongoDB veritabanına eklendiniz. 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")
                else:
                    res_st.warning("Lütfen boş alanları doldurun.")
                    
        elif auth_mode == "Giriş Yap":
            if res_st.button("Sisteme Giriş Yap", type="primary"):
                user_record = users_col.find_one({"email": email})
                if user_record and check_hashes(password, user_record["password"]):
                    res_st.session_state.logged_in = True
                    res_st.session_state.user_email = email
                    res_st.rerun()
                else:
                    res_st.error("Hatalı e-posta veya şifre!")
                    
    with col_auth_right:
        res_st.markdown("""
            ### Neden ParserFlow?
            * **Gerçek Yapay Zeka:** Google Gemini altyapısı ile CV'leri saniyeler içinde analiz edin.
            * **Kalıcı Bulut Depolama:** MongoDB entegrasyonu sayesinde verileriniz her cihazdan erişilebilir.
        """)

# ANA SİSTEM
else:
    u_info = users_col.find_one({"email": res_st.session_state.user_email})
    
    with res_st.sidebar:
        res_st.subheader("👤 Hesap Bilgileri")
        res_st.write(f"**Kullanıcı:** {res_st.session_state.user_email}")
        res_st.write(f"**Abonelik:** `{u_info['paket_turu']}`")
        
        if u_info['paket_turu'] == "Sınırsız (Kurumsal)":
            res_st.write("**Kalan Hak:** Sınırsız ♾️")
        else:
            kullanilan = u_info['toplam_hak'] - u_info['kalan_hak']
            res_st.write(f"📊 **Kota Kullanımı:** {kullanilan} / {u_info['toplam_hak']} CV")
            res_st.progress(kullanilan / u_info['toplam_hak'])
        
        res_st.write("---")
        sayfa = res_st.radio("Gitmek İstediğiniz Sayfa:", ["🏠 Ana Sayfa (CV Analiz)", "📁 CVler (Yönetim & Kategori)"])
        res_st.write("---")
        if res_st.button("🚪 Güvenli Çıkış"):
            res_st.session_state.logged_in = False
            res_st.session_state.user_email = ""
            res_st.session_state.current_analysis = None
            res_st.rerun()

    if sayfa == "🏠 Ana Sayfa (CV Analiz)":
        col_left, col_right = res_st.columns([1, 1.5])

        with col_left:
            res_st.subheader("📁 Özgeçmiş Yükleme")
            uploaded_file = res_st.file_uploader("Bir PDF dosyası seçin", type=["pdf"])
            
            if uploaded_file is not None:
                res_st.success(f"🔄 {uploaded_file.name} analize hazır.")
                if res_st.button("🚀 Yapay Zeka İle Analiz Et", type="primary"):
                    if u_info["paket_turu"] == "Sınırsız (Kurumsal)" or u_info["kalan_hak"] > 0:
                        with res_st.spinner("🤖 Google Gemini CV'yi analiz ediyor..."):
                            cv_text = extract_text_from_pdf(uploaded_file)
                            res_st.session_state.current_analysis = analyze_cv_real(cv_text)
                            res_st.rerun()
                    else:
                        res_st.error("❌ Limitiniz bitti!")

            if res_st.session_state.current_analysis is not None:
                res_st.write("---")
                res_st.subheader("📥 Havuza Kaydetme Paneli")
                
                ana_secilen_kat = res_st.selectbox("Hangi Kategoriye Kaydedilsin?", u_info["kategoriler"], key="ana_kat_sec")
                ana_secilen_durum = res_st.radio("🚥 Aday Değerlendirme Durumu Seçin:", ["🔵 Yeni", "🟢 Olumlu", "🟡 Nötr", "🔴 Olumsuz"], horizontal=True)
                durum_clean = ana_secilen_durum.split(" ")[1] 
                
                if res_st.button("💾 Havuza Güvenle Kaydet", type="secondary"):
                    final_cv = res_st.session_state.current_analysis.copy()
                    final_cv["owner_email"] = res_st.session_state.user_email
                    final_cv["kategori"] = ana_secilen_kat
                    final_cv["durum"] = durum_clean
                    final_cv["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    cvs_col.insert_one(final_cv)
                    
                    if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                        users_col.update_one({"email": res_st.session_state.user_email}, {"$inc": {"kalan_hak": -1}})
                    
                    res_st.success(f"💾 {final_cv.get('Ad Soyad', 'Aday')} kaydedildi!")
                    res_st.session_state.current_analysis = None
                    time.sleep(1)
                    res_st.rerun()

        with col_right:
            res_st.subheader("📊 Anlık İnceleme Ekranı")
            if res_st.session_state.current_analysis is not None:
                res = res_st.session_state.current_analysis
                res_st.markdown('<div class="result-card">', unsafe_allow_html=True)
                res_st.markdown("### 👤 Ayıklanan Bilgiler")
                res_st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                res_st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                res_st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                res_st.write(f"**📍 Adres:** {res.get('Adres')}")
                res_st.write(f"**🛠️ Yetenekler:** {res.get('Yetenekler')}")
                res_st.write("**💼 Deneyimler:**")
                if isinstance(res.get('Deneyim'), list):
                    for d in res.get('Deneyim'):
                        res_st.write(f"- {d}")
                else:
                    res_st.write(res.get('Deneyim'))
                res_st.markdown('</div>', unsafe_allow_html=True)
            else:
                res_st.info("Yapay zeka analiz sonuçları burada görünecek.")

    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        res_st.subheader("📁 Özelleştirilmiş Bulut CV Deposu")
        
        col_kat1, col_kat2 = res_st.columns([2, 1])
        with col_kat1:
            yeni_kategori = res_st.text_input("➕ Yeni Kategori İsmi Girin").strip()
        with col_kat2:
            res_st.write("##")
            if res_st.button("Kategori Oluştur"):
                if yeni_kategori and yeni_kategori not in u_info["kategoriler"]:
                    users_col.update_one({"email": res_st.session_state.user_email}, {"$push": {"kategoriler": yeni_kategori}})
                    res_st.success(f"📂 '{yeni_kategori}' kategorisi oluşturuldu!")
                    res_st.rerun()
                        
        res_st.write("---")
        
        col_f1, col_f2 = res_st.columns(2)
        with col_f1:
            filtre_kategori = res_st.selectbox("📂 Kategori Filtresi:", ["Hepsi"] + u_info["kategoriler"])
        with col_f2:
            filtre_durum = res_st.selectbox("🎨 Durum Filtresi:", ["Hepsi", "Yeni", "Olumlu", "Nötr", "Olumsuz"])
        
        query = {"owner_email": res_st.session_state.user_email}
        if filtre_kategori != "Hepsi":
            query["kategori"] = filtre_kategori
        if filtre_durum != "Hepsi":
            query["durum"] = filtre_durum
            
        kullanici_kayitlari = list(cvs_col.find(query).sort("kayit_tarihi", -1))
        
        res_st.write(f"### 📄 Aday Havuzu ({len(kullanici_kayitlari)} Aday)")
        
        if len(kullanici_kayitlari) > 0:
            for kayit in kullanici_kayitlari:
                emoji_map = {"Yeni": "🔵", "Olumlu": "🟢", "Nötr": "🟡", "Olumsuz": "🔴"}
                current_emoji = emoji_map.get(kayit.get("durum", "Yeni"), "🔵")
                baslik = f"📄 {kayit.get('Ad Soyad')} | Durum: {kayit.get('durum')} | Tarih: {kayit.get('kayit_tarihi')} {current_emoji}"
                
                with res_st.expander(baslik):
                    res_st.markdown(f'<div class="category-box">📂 Kategori: {kayit.get("kategori")}</div>', unsafe_allow_html=True)
                    res_st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    res_st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    res_st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    res_st.write(f"**🛠️ Yetenekler:** {kayit.get('Yetenekler')}")
                    
                    res_st.write("---")
                    res_st.write("**🚥 Durumu Değiştir:**")
                    col_b1, col_b2, col_b3, col_b4 = res_st.columns(4)
                    
                    with col_b1:
                        if res_st.button("🟢 Olumlu", key=f"btn_ol__{kayit['_id']}"):
                            cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"durum": "Olumlu"}})
                            res_st.rerun()
                    with col_b2:
                        if res_st.button("🟡 Nötr", key=f"btn_no_{kayit['_id']}"):
                            cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"durum": "Nötr"}})
                            res_st.rerun()
                    with col_b3:
                        if res_st.button("🔴 Olumsuz", key=f"btn_sz_{kayit['_id']}"):
                            cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"durum": "Olumsuz"}})
                            res_st.rerun()
                    with col_b4:
                        if res_st.button("🔵 Yeni", key=f"btn_yn_{kayit['_id']}"):
                            cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"durum": "Yeni"}})
                            res_st.rerun()

                    res_st.write("---")
                    state_key = f"email_generated_{kayit['_id']}"
                    if state_key not in res_st.session_state:
                        res_st.session_state[state_key] = False
                        
                    if res_st.button(f"✨ Bu Aday İçin E-posta Taslağı Üret", key=f"generate_btn_{kayit['_id']}"):
                        res_st.session_state[state_key] = True
                    
                    if res_st.session_state[state_key]:
                        sablon_metin = generate_email_template(kayit.get('Ad Soyad'), kayit.get('durum'))
                        res_st.markdown(f'<div class="email-box">{sablon_metin}</div>', unsafe_allow_html=True)
                        if res_st.button("❌ Taslağı Kapat", key=f"close_email_{kayit['_id']}"):
                            res_st.session_state[state_key] = False
                            res_st.rerun()

                    res_st.write("---")
                    yeni_kat_atama = res_st.selectbox("Kategori Değiştir:", u_info["kategoriler"], index=u_info["kategoriler"].index(kayit.get("kategori")), key=f"change_kat_{kayit['_id']}")
                    if yeni_kat_atama != kayit.get("kategori"):
                        cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"kategori": yeni_kat_atama}})
                        res_st.rerun()
        else:
            res_st.info("Aday bulunamadı.")
