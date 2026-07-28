Python
import streamlit as res_st
import datetime
import time
import hashlib
import json
import base64
from pymongo import MongoClient
import google.generativeai as genai
from pypdf import PdfReader

# 1. Arayüz Tasarımı ve Sayfa Ayarları
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

# ----------------------------------------
# 🗄️ MONGODB VE GEMINI API BAĞLANTILARI
# ----------------------------------------
@res_st.cache_resource
def init_connection():
    # Hızlı ve stabil hafif bağlantı sürücüsü
    return MongoClient(res_st.secrets["mongo_uri"], serverSelectionTimeoutMS=5000)

try:
    client = init_connection()
    db = client["parserflow_db"]
    users_col = db["users"]
    cvs_col = db["cvs"]
except Exception as e:
    res_st.error(f"⚠️ Veritabanı bağlantısı kurulamadı: {e}")
    res_st.stop()

# Gemini API Yapılandırması
try:
    genai.configure(api_key=res_st.secrets["GEMINI_API_KEY"])
except Exception as e:
    res_st.error(f"⚠️ Gemini API Key hatası: {e}")

# --- GÜVENLİK İÇİN ŞİFRE HASHLEME FONKSİYONLARI ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    return make_hashes(password) == hashed_text

# --- PDF METİN OKUMA VE GEMINI ANALİZ MOTORU ---
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

def analyze_cv_real(file_text):
    # En hızlı yanıt veren kararlı model
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
        "Toplam Tecrübe": "Tahmini veya belirtilen toplam tecrübe süresi (Örn: 3 Yıl)",
        "Deneyim": ["Son iş tecrübeleri (En fazla 5 iş tecrübesi listele: Şirket - Pozisyon - Tarih Aralığı)"],
        "Eğitim": ["Okul/Üniversite - Bölüm - Mezuniyet Yılı"],
        "Diller": ["Bilinen yabancı diller ve seviyeleri"],
        "Sertifikalar": ["Sahip olunan sertifikalar, kurslar ve belgeler"],
        "Yetenekler": "Öne çıkan teknik yetenekler, yazılımlar ve beceriler"
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
            "Toplam Tecrübe": "Bulunamadı",
            "Deneyim": [raw_response[:100]],
            "Eğitim": ["Bulunamadı"],
            "Diller": ["Bulunamadı"],
            "Sertifikalar": ["Bulunamadı"],
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

# --- GEÇİCİ DURUM HAFIZALARI ---
if 'logged_in' not in res_st.session_state:
    res_st.session_state.logged_in = False
if 'user_email' not in res_st.session_state:
    res_st.session_state.user_email = ""
if 'current_analysis' not in res_st.session_state:
    res_st.session_state.current_analysis = None
if 'current_pdf_bytes' not in res_st.session_state:
    res_st.session_state.current_pdf_bytes = None
if 'current_pdf_name' not in res_st.session_state:
    res_st.session_state.current_pdf_name = None

# ----------------------------------------
# 🚪 GELİŞMİŞ B2B GİRİŞ YAP / KAYIT OL EKRANI
# ----------------------------------------
if not res_st.session_state.logged_in:
    col_auth_left, col_auth_right = res_st.columns([1.2, 1])
    
    with col_auth_left:
        res_st.subheader("🔐 ParserFlow Kurumsal Portal")
        auth_mode = res_st.radio("İşlem Seçiniz:", ["Giriş Yap", "Kayıt Ol (Yeni Hesap)"], horizontal=True)
        
        if auth_mode == "Kayıt Ol (Yeni Hesap)":
            res_st.markdown("##### 📝 Hesap Tipi & Kullanıcı Bilgileri")
            
            hesap_turu = res_st.selectbox("Hesap Türü Seçin:", ["Bireysel Kullanıcı", "Kurumsal / Şirket"])
            
            c1, c2 = res_st.columns(2)
            with c1:
                ad_soyad = res_st.text_input("Ad Soyad *").strip()
                email = res_st.text_input("Kurumsal E-posta Adresi *", key="reg_email").strip().lower()
            with c2:
                telefon = res_st.text_input("Telefon Numarası").strip()
                password = res_st.text_input("Şifre Belirleyin *", type="password", key="reg_pass")

            sirket_unvani = ""
            vergi_no = ""
            vergi_dairesi = ""
            sektor = ""

            if hesap_turu == "Kurumsal / Şirket":
                res_st.markdown("##### 🏢 Şirket & Fatura Bilgileri")
                sc1, sc2 = res_st.columns(2)
                with sc1:
                    sirket_unvani = res_st.text_input("Şirket Unvanı *").strip()
                    vergi_dairesi = res_st.text_input("Vergi Dairesi").strip()
                with sc2:
                    vergi_no = res_st.text_input("Vergi Numarası / VKN").strip()
                    sektor = res_st.selectbox("Sektör", ["Lojistik / Denizcilik", "Bilişim / Teknoloji", "E-Ticaret / Mağazacılık", "İnsan Kaynakları", "Üretim / Sanayi", "Diğer"])

            res_st.markdown("##### 💳 Abonelik Paketi Seçimi")
            paket_secimi = res_st.selectbox("Başlangıç Paketi", [
                "Başlangıç Paketi (10$ / Ay - 100 CV)", 
                "Profesyonel Paket (15$ / Ay - 500 CV)", 
                "Kurumsal Paket (25$ / Ay - Sınırsız CV)"
            ])
            
            if res_st.button("🚀 Hesabımı Oluştur ve Başla", type="primary"):
                if email and password and ad_soyad and (hesap_turu == "Bireysel Kullanıcı" or sirket_unvani):
                    try:
                        existing_user = users_col.find_one({"email": email})
                        if existing_user:
                            res_st.error("⚠️ Bu e-posta adresi zaten sisteme kayıtlı!")
                        else:
                            hak = 100 if "10$" in paket_secimi else (500 if "15$" in paket_secimi else 9999)
                            p_isim = "Başlangıç" if "10$" in paket_secimi else ("Profesyonel" if "15$" in paket_secimi else "Sınırsız (Kurumsal)")
                            bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                            
                            new_user_data = {
                                "email": email,
                                "password": make_hashes(password),
                                "ad_soyad": ad_soyad,
                                "telefon": telefon,
                                "hesap_turu": hesap_turu,
                                "sirket_unvani": sirket_unvani,
                                "vergi_no": vergi_no,
                                "vergi_dairesi": vergi_dairesi,
                                "sektor": sektor,
                                "paket_turu": p_isim, 
                                "abonelik_durumu": "aktif", 
                                "abonelik_bitis": bitis_tarihi, 
                                "kalan_hak": hak,
                                "toplam_hak": hak,
                                "kategoriler": ["Genel"],
                                "kayit_tarihi": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }
                            users_col.insert_one(new_user_data)
                            res_st.success("🎉 Kayıt başarıyla tamamlandı! 'Giriş Yap' sekmesinden sisteme girebilirsiniz.")
                    except Exception as reg_err:
                        res_st.error(f"❌ Veritabanı kayıt hatası: {reg_err}")
                else:
                    res_st.warning("⚠️ Lütfen zorunlu alanları (*) doldurunuz.")
                    
        elif auth_mode == "Giriş Yap":
            email = res_st.text_input("E-posta Adresi", key="login_email").strip().lower()
            password = res_st.text_input("Şifre", type="password", key="login_pass")
            
            if res_st.button("Sisteme Giriş Yap", type="primary"):
                if not email or not password:
                    res_st.warning("⚠️ E-posta ve şifre boş bırakılamaz.")
                else:
                    try:
                        user_record = users_col.find_one({"email": email})
                        if not user_record:
                            res_st.error(f"❌ '{email}' e-postasına ait bir kayıt bulunamadı! Lütfen önce Kayıt Olun.")
                        elif not check_hashes(password, user_record["password"]):
                            res_st.error("❌ Şifre hatalı! Lütfen tekrar kontrol edin.")
                        else:
                            res_st.session_state.logged_in = True
                            res_st.session_state.user_email = email
                            res_st.rerun()
                    except Exception as log_err:
                        res_st.error(f"❌ Veritabanı bağlantı hatası: {log_err}")
                    
    with col_auth_right:
        res_st.markdown("""
            ### 💼 ParserFlow SaaS Platformu
            
            * **Özelleştirilmiş İK Portalı:** Bireysel veya Kurumsal hesap seçeneği.
            * **Şirket ve Fatura Entegrasyonu:** Şirketiniz için vergi bilgileriyle resmi profil.
            * **Gemini Yapay Zeka:** Tam yapay zeka entegrasyonu ile dakikalar değil saniyeler içinde CV tarama.
            * **Kesintisiz MongoDB Bulut:** Verileriniz güvende, tüm ekibiniz için erişilebilir.
        """)

# ----------------------------------------
# 🖥️ ANA SİSTEM (GİRİŞ YAPILDIYSA)
# ----------------------------------------
else:
    u_info = users_col.find_one({"email": res_st.session_state.user_email})
    
    with res_st.sidebar:
        res_st.subheader("👤 Profil Bilgileri")
        res_st.write(f"**Kullanıcı:** {u_info.get('ad_soyad', res_st.session_state.user_email) if u_info else res_st.session_state.user_email}")
        if u_info and u_info.get('sirket_unvani'):
            res_st.write(f"🏢 **Şirket:** {u_info.get('sirket_unvani')}")
        if u_info:
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
            res_st.session_state.current_pdf_bytes = None
            res_st.session_state.current_pdf_name = None
            res_st.rerun()

    if sayfa == "🏠 Ana Sayfa (CV Analiz)":
        col_left, col_right = res_st.columns([1, 1.5])

        with col_left:
            res_st.subheader("📁 Özgeçmiş Yükleme")
            uploaded_file = res_st.file_uploader("Bir PDF dosyası seçin", type=["pdf"])
            
            if uploaded_file is not None:
                res_st.success(f"🔄 {uploaded_file.name} analize hazır.")
                if res_st.button("🚀 Yapay Zeka İle Analiz Et", type="primary"):
                    if u_info and (u_info["paket_turu"] == "Sınırsız (Kurumsal)" or u_info["kalan_hak"] > 0):
                        with res_st.spinner("🤖 Google Gemini CV'yi analiz ediyor..."):
                            pdf_bytes = uploaded_file.getvalue()
                            cv_text = extract_text_from_pdf(uploaded_file)
                            
                            res_st.session_state.current_analysis = analyze_cv_real(cv_text)
                            res_st.session_state.current_pdf_bytes = pdf_bytes
                            res_st.session_state.current_pdf_name = uploaded_file.name
                            res_st.rerun()
                    else:
                        res_st.error("❌ Limitiniz bitti!")

            if res_st.session_state.current_analysis is not None:
                res_st.write("---")
                res_st.subheader("📥 Havuza Kaydetme Paneli")
                
                kategori_listesi = u_info["kategoriler"] if u_info else ["Genel"]
                ana_secilen_kat = res_st.selectbox("Hangi Kategoriye Kaydedilsin?", kategori_listesi, key="ana_kat_sec")
                ana_secilen_durum = res_st.radio("🚥 Aday Değerlendirme Durumu Seçin:", ["🔵 Yeni", "🟢 Olumlu", "🟡 Nötr", "🔴 Olumsuz"], horizontal=True)
                durum_clean = ana_secilen_durum.split(" ")[1] 
                
                if res_st.button("💾 Havuza Güvenle Kaydet", type="secondary"):
                    final_cv = res_st.session_state.current_analysis.copy()
                    final_cv["owner_email"] = res_st.session_state.user_email
                    final_cv["kategori"] = ana_secilen_kat
                    final_cv["durum"] = durum_clean
                    final_cv["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    if res_st.session_state.current_pdf_bytes:
                        final_cv["pdf_base64"] = base64.b64encode(res_st.session_state.current_pdf_bytes).decode('utf-8')
                        final_cv["pdf_filename"] = res_st.session_state.current_pdf_name

                    cvs_col.insert_one(final_cv)
                    
                    if u_info and u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                        users_col.update_one({"email": res_st.session_state.user_email}, {"$inc": {"kalan_hak": -1}})
                    
                    res_st.success(f"💾 {final_cv.get('Ad Soyad', 'Aday')} veritabanına kaydedildi!")
                    res_st.session_state.current_analysis = None
                    res_st.session_state.current_pdf_bytes = None
                    res_st.session_state.current_pdf_name = None
                    time.sleep(1)
                    res_st.rerun()

        with col_right:
            res_st.subheader("📊 Anlık İnceleme Ekranı")
            if res_st.session_state.current_analysis is not None:
                res = res_st.session_state.current_analysis
                res_st.markdown('<div class="result-card">', unsafe_allow_html=True)
                res_st.markdown("### 👤 Ayıklanan Detaylı Profil")
                res_st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                res_st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                res_st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                res_st.write(f"**📍 Adres:** {res.get('Adres')}")
                res_st.write(f"**⏳ Toplam Tecrübe:** {res.get('Toplam Tecrübe', 'Belirtilmedi')}")
                
                res_st.write("---")
                res_st.write("**💼 Son İş Deneyimleri (Max 5):**")
                if isinstance(res.get('Deneyim'), list):
                    for d in res.get('Deneyim'):
                        res_st.write(f"- {d}")
                else:
                    res_st.write(res.get('Deneyim'))
                    
                res_st.write("---")
                res_st.write("**🎓 Eğitim Geçmişi:**")
                if isinstance(res.get('Eğitim'), list):
                    for e in res.get('Eğitim'):
                        res_st.write(f"- {e}")
                else:
                    res_st.write(res.get('Eğitim'))

                res_st.write("---")
                res_st.write("**🌐 Yabancı Diller:**")
                if isinstance(res.get('Diller'), list):
                    for dil in res.get('Diller'):
                        res_st.write(f"- {dil}")
                else:
                    res_st.write(res.get('Diller'))

                res_st.write("---")
                res_st.write("**📜 Sertifikalar & Kurslar:**")
                if isinstance(res.get('Sertifikalar'), list):
                    for s in res.get('Sertifikalar'):
                        res_st.write(f"- {s}")
                else:
                    res_st.write(res.get('Sertifikalar'))

                res_st.write("---")
                res_st.write(f"**🛠️ Beceriler & Teknolojiler:** {res.get('Yetenekler')}")
                res_st.markdown('</div>', unsafe_allow_html=True)
            else:
                res_st.info("Yapay zeka analiz sonuçları detaylı olarak burada görünecek.")

    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        res_st.subheader("📁 Özelleştirilmiş Bulut CV Deposu")
        
        kategori_listesi = u_info["kategoriler"] if u_info else ["Genel"]
        col_kat1, col_kat2 = res_st.columns([2, 1])
        with col_kat1:
            yeni_kategori = res_st.text_input("➕ Yeni Kategori İsmi Girin").strip()
        with col_kat2:
            res_st.write("##")
            if res_st.button("Kategori Oluştur"):
                if yeni_kategori and yeni_kategori not in kategori_listesi:
                    users_col.update_one({"email": res_st.session_state.user_email}, {"$push": {"kategoriler": yeni_kategori}})
                    res_st.success(f"📂 '{yeni_kategori}' kategorisi oluşturuldu!")
                    res_st.rerun()
                        
        res_st.write("---")
        
        col_f1, col_f2 = res_st.columns(2)
        with col_f1:
            filtre_kategori = res_st.selectbox("📂 Kategori Filtresi:", ["Hepsi"] + kategori_listesi)
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
                    
                    if "pdf_base64" in kayit:
                        pdf_data = base64.b64decode(kayit["pdf_base64"])
                        dosya_adi = kayit.get("pdf_filename", f"{kayit.get('Ad Soyad')}_CV.pdf")
                        res_st.download_button(
                            label=f"📥 Orijinal CV PDF'ini İndir ({dosya_adi})",
                            data=pdf_data,
                            file_name=dosya_adi,
                            mime="application/pdf",
                            key=f"dl_pdf_{kayit['_id']}"
                        )
                        res_st.write("---")

                    res_st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    res_st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    res_st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    res_st.write(f"**⏳ Toplam Tecrübe:** {kayit.get('Toplam Tecrübe', 'Belirtilmedi')}")
                    
                    res_st.write("---")
                    res_st.write("**💼 Deneyimler:**")
                    if isinstance(kayit.get('Deneyim'), list):
                        for d in kayit.get('Deneyim'):
                            res_st.write(f"- {d}")
                    else:
                        res_st.write(kayit.get('Deneyim'))

                    res_st.write("**🎓 Eğitim:**")
                    if isinstance(kayit.get('Eğitim'), list):
                        for e in kayit.get('Eğitim'):
                            res_st.write(f"- {e}")
                    else:
                        res_st.write(kayit.get('Eğitim'))

                    res_st.write("**🌐 Yabancı Diller:**")
                    if isinstance(kayit.get('Diller'), list):
                        for dil in kayit.get('Diller'):
                            res_st.write(f"- {dil}")
                    else:
                        res_st.write(kayit.get('Diller'))

                    res_st.write("**📜 Sertifikalar:**")
                    if isinstance(kayit.get('Sertifikalar'), list):
                        for s in kayit.get('Sertifikalar'):
                            res_st.write(f"- {s}")
                    else:
                        res_st.write(kayit.get('Sertifikalar'))

                    res_st.write(f"**🛠️ Beceriler:** {kayit.get('Yetenekler')}")
                    
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
                    yeni_kat_atama = res_st.selectbox("Kategori Değiştir:", kategori_listesi, index=kategori_listesi.index(kayit.get("kategori")) if kayit.get("kategori") in kategori_listesi else 0, key=f"change_kat_{kayit['_id']}")
                    if yeni_kat_atama != kayit.get("kategori"):
                        cvs_col.update_one({"_id": kayit["_id"]}, {"$set": {"kategori": yeni_kat_atama}})
                        res_st.rerun()
        else:
            res_st.info("Aday bulunamadı.")
