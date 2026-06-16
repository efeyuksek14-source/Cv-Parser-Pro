import streamlit as st
import datetime
import time

# 3. Arayüz Tasarımı
st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .bullet-item { background-color: #f8fafc; padding: 10px 15px; border-left: 4px solid #3b82f6; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
    .category-box { background-color: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #475569; display: inline-block; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Yapay Zeka Destekli Gelişmiş CV Yönetim Merkezi")

# ----------------------------------------
# 🧠 SİMÜLE VERİTABANI (Tarayıcı Hafızası)
# ----------------------------------------
if 'mock_users_db' not in st.session_state:
    st.session_state.mock_users_db = {
        "efe@ceyiznet.com": {
            "password": "123",
            "paket_turu": "Profesyonel",
            "abonelik_durumu": "aktif",
            "abonelik_bitis": "2026-07-16",
            "kalan_hak": 500,
            "kategoriler": ["Genel", "Yazılım", "Stajyerler"] # Kullanıcıya özel varsayılan kategoriler
        }
    }

if 'mock_cvs_db' not in st.session_state:
    # Testleri hızlandırmak için içeride hazır 1-2 sahte CV bırakıyoruz
    st.session_state.mock_cvs_db = [
        {
            "id": 1,
            "Ad Soyad": "Aday: AHMET YILMAZ",
            "Telefon": "+90 532 111 22 33",
            "E-posta": "ahmet@example.com",
            "Adres": "Kadıköy, İstanbul",
            "Deneyim": ["CSS Ship Management - Teknik Departman Stajyeri"],
            "Yetenekler": "Python, Excel",
            "owner_email": "efe@ceyiznet.com",
            "kategori": "Stajyerler",
            "kayit_tarihi": "2026-06-16 10:00:00"
        },
        {
            "id": 2,
            "Ad Soyad": "Aday: ELİF KAYA",
            "Telefon": "+90 544 333 44 55",
            "E-posta": "elif@example.com",
            "Adres": "Beşiktaş, İstanbul",
            "Deneyim": ["Ceyiznet - E-Ticaret Sorumlusu"],
            "Yetenekler": "Shopify, Trendyol Entegrasyon",
            "owner_email": "efe@ceyiznet.com",
            "kategori": "Genel",
            "kayit_tarihi": "2026-06-16 10:30:00"
        }
    ]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Test Analiz Fonksiyonu
def analyze_cv_mock(filename):
    time.sleep(0.5)
    return {
        "Ad Soyad": f"Aday: {filename.split('.')[0].upper()}",
        "Telefon": "+90 532 999 88 77",
        "E-posta": "ornek_aday@ceyiznet.com",
        "Adres": "Maltepe, İstanbul",
        "Deneyim": [
            "Örnek Şirket - Pozisyon Bilgisi (2 Yıl)"
        ],
        "Yetenekler": "E-Ticaret, Python, Analiz"
    }

# ----------------------------------------
# 🚪 YAN PANEL SİSTEMİ
# ----------------------------------------
with st.sidebar:
    if not st.session_state.logged_in:
        st.subheader("🔐 Kullanıcı Paneli")
        auth_mode = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"])
        
        email = st.text_input("E-posta Adresi").strip()
        password = st.text_input("Şifre", type="password")
        
        if auth_mode == "Kayıt Ol":
            paket_secimi = st.selectbox("Satın Alınacak Paket", [
                "Başlangıç Paketi (10$ - 100 CV)", 
                "Profesyonel Paket (15$ - 500 CV)", 
                "Kurumsal Paket (25$ - Sınırsız CV)"
            ])
            
            if st.button("Hesap Oluştur"):
                if email and password:
                    if email in st.session_state.mock_users_db:
                        st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        if "10$" in paket_secimi:
                            hak = 100
                            p_isim = "Başlangıç"
                        elif "15$" in paket_secimi:
                            hak = 500
                            p_isim = "Profesyonel"
                        else:
                            hak = 9999
                            p_isim = "Sınırsız (Kurumsal)"
                            
                        bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                        
                        st.session_state.mock_users_db[email] = {
                            "password": password,
                            "paket_turu": p_isim,
                            "abonelik_durumu": "aktif",
                            "abonelik_bitis": bitis_tarihi,
                            "kalan_hak": hak,
                            "kategoriler": ["Genel"] # Yeni kullanıcıya varsayılan kategori
                        }
                        st.success("🎉 Hesabınız oluşturuldu! Giriş yapabilirsiniz.")
                else:
                    st.warning("Lütfen alanları doldurun.")
                    
        elif auth_mode == "Giriş Yap":
            st.info("Hazır hesap:\n\nefe@ceyiznet.com / 123")
            if st.button("Giriş Yap"):
                if email in st.session_state.mock_users_db and st.session_state.mock_users_db[email]["password"] == password:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Hatalı e-posta veya şifre!")
    else:
        st.subheader("👤 Hesap Bilgileri")
        st.write(f"**Kullanıcı:** {st.session_state.user_email}")
        
        u_info = st.session_state.mock_users_db[st.session_state.user_email]
        st.write(f"**Paket:** {u_info['paket_turu']}")
        
        if u_info['paket_turu'] == "Sınırsız (Kurumsal)":
            st.write("**Kalan Hak:** Sınırsız ♾️")
        else:
            st.write(f"**Kalan Hak:** {u_info['kalan_hak']}")
            
        st.write("---")
        # 🗺️ ÇOKLU SAYFA MENÜSÜ (İstediğin Ekstra Sayfa Geçişi)
        st.subheader("🗺️ Menü")
        sayfa = st.radio("Gitmek İstediğiniz Sayfa:", ["🏠 Ana Sayfa (CV Analiz)", "📁 CVler (Yönetim & Kategori)"])
        
        st.write("---")
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.rerun()

# ----------------------------------------
# 🖥️ ANA İÇERİK ALANI
# ----------------------------------------
if not st.session_state.logged_in:
    st.info("ℹ️ Lütfen sol panelden giriş yapın.")
else:
    u_info = st.session_state.mock_users_db[st.session_state.user_email]

    # 🏠 1. SAYFA: ANA SAYFA (CV ANALİZ)
    if sayfa == "🏠 Ana Sayfa (CV Analiz)":
        col_left, col_right = st.columns([1, 1.5])

        with col_left:
            st.subheader("📁 Özgeçmiş Yükleme")
            uploaded_file = st.file_uploader("Bir dosya seçin", type=["pdf", "docx"])
            
            # Analiz etmeden önce hangi kategoriye kaydedileceğini seçtiriyoruz
            secilen_kat = st.selectbox("Bu CV Hangi Kategoriye Kaydedilsin?", u_info["kategoriler"])
            
            if uploaded_file is not None:
                st.success(f"🔄 {uploaded_file.name} hazır.")
                
                if st.button("🚀 Analiz Et", type="primary"):
                    if u_info["kalan_hak"] > 0:
                        with st.spinner("Analiz ediliyor..."):
                            ai_result = analyze_cv_mock(uploaded_file.name)
                            st.session_state.ai_results = ai_result
                            
                            # Veritabanı simülasyonuna ekleme
                            ai_result["id"] = len(st.session_state.mock_cvs_db) + 1
                            ai_result["owner_email"] = st.session_state.user_email
                            ai_result["kategori"] = secilen_kat # Seçtiği kategoriyi ekliyoruz
                            ai_result["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.mock_cvs_db.append(ai_result)
                            
                            if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                                st.session_state.mock_users_db[st.session_state.user_email]["kalan_hak"] -= 1
                                
                            st.success(f"💾 CV başarıyla '{secilen_kat}' kategorisine kaydedildi!")
                            st.rerun()
                    else:
                        st.error("❌ Limitiniz bitti!")

        with col_right:
            st.subheader("📊 Anlık Sonuç")
            if 'ai_results' in st.session_state:
                res = st.session_state.ai_results
                st.balloons()
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f"### 👤 Kişisel Bilgiler")
                st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                st.write(f"**📍 Adres:** {res.get('Adres')}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Sonuçlar burada görünecek.")

    # 📁 2. SAYFA: CV'LER (GEÇMİŞ VE KATEGORİ YÖNETİMİ)
    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        st.subheader("📁 Özelleştirilmiş CV Deposu")
        
        # 🟢 YENİ KATEGORİ OLUŞTURMA ALANI
        col_kat1, col_kat2 = st.columns([2, 1])
        with col_kat1:
            yeni_kategori = st.text_input("➕ Yeni Kategori İsmi Girin (Örn: Muhasebe, İstanbul İK vb.)").strip()
        with col_kat2:
            st.write("##") # Boşluk ayarı
            if st.button("Kategori Oluştur"):
                if yeni_kategori:
                    if yeni_kategori in u_info["kategoriler"]:
                        st.warning("Bu isimde bir kategori zaten var!")
                    else:
                        st.session_state.mock_users_db[st.session_state.user_email]["kategoriler"].append(yeni_kategori)
                        st.success(f"📂 '{yeni_kategori}' kategorisi başarıyla oluşturuldu!")
                        st.rerun()
                        
        st.write("---")
        
        # 🔍 KATEGORİYE GÖRE FİLTRELEME FİLTRESİ
        filtre_kategori = st.selectbox("📂 Listelemek İstediğiniz Kategoriyi Seçin:", ["Hepsi"] + u_info["kategoriler"])
        
        # Giriş yapmış kullanıcının CV'lerini çekiyoruz
        kullanici_kayitlari = [c for c in st.session_state.mock_cvs_db if c["owner_email"] == st.session_state.user_email]
        
        # Eğer filtre seçildiyse ona göre daraltıyoruz
        if filtre_kategori != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["kategori"] == filtre_kategori]
            
        st.write(f"### 📄 Aday Listesi ({len(kullanici_kayitlari)} Aday Listeleniyor)")
        
        if len(kullanici_kayitlari) > 0:
            for kayit in reversed(kullanici_kayitlari):
                with st.expander(f"📄 {kayit.get('Ad Soyad')} - Yüklenme: {kayit.get('kayit_tarihi')}"):
                    # Ekranda hangi kategoride olduğunu rozet (badge) olarak gösteriyoruz
                    st.markdown(f'<div class="category-box">📂 Kategori: {kayit.get("kategori")}</div>', unsafe_allow_html=True)
                    
                    st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    
                    # 🟡 CV'NİN KATEGORİSİNİ SONRADAN DEĞİŞTİRME ÖZELLİĞİ
                    yeni_kat_atama = st.selectbox(
                        "Kategoriyi Değiştir:", 
                        u_info["kategoriler"], 
                        index=u_info["kategoriler"].index(kayit.get("kategori")),
                        key=f"change_kat_{kayit['id']}"
                    )
                    
                    if yeni_kat_atama != kayit.get("kategori"):
                        # Hafızadaki kaydı bulup güncelliyoruz
                        for idx, cv_item in enumerate(st.session_state.mock_cvs_db):
                            if cv_item["id"] == kayit["id"]:
                                st.session_state.mock_cvs_db[idx]["kategori"] = yeni_kat_atama
                                st.success("Kategori başarıyla güncellendi!")
                                st.rerun()
        else:
            st.info("Bu kategoride henüz yüklenmiş bir aday CV'si bulunmuyor.")
