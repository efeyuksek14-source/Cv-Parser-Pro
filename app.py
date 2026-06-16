import streamlit as st
import datetime
import time

# 3. Arayüz Tasarımı
st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .category-box { background-color: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #475569; display: inline-block; margin-bottom: 10px; margin-right: 5px;}
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
            "kategoriler": ["Genel", "Yazılım", "Stajyerler"]
        }
    }

if 'mock_cvs_db' not in st.session_state:
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
            "durum": "Olumlu",
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
            "durum": "Nötr",
            "kayit_tarihi": "2026-06-16 10:30:00"
        }
    ]

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

def analyze_cv_mock(filename):
    time.sleep(0.4)
    return {
        "Ad Soyad": f"Aday: {filename.split('.')[0].upper()}",
        "Telefon": "+90 532 999 88 77",
        "E-posta": "ornek_aday@ceyiznet.com",
        "Adres": "Maltepe, İstanbul",
        "Deneyim": ["Örnek Şirket - Pozisyon Bilgisi (2 Yıl)"],
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
            paket_secimi = st.selectbox("Satın Alınacak Paket", ["Başlangıç Paketi (10$)", "Profesyonel Paket (15$)", "Kurumsal Paket (25$)"])
            if st.button("Hesap Oluştur"):
                if email and password:
                    if email in st.session_state.mock_users_db:
                        st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        hak = 100 if "10$" in paket_secimi else (500 if "15$" in paket_secimi else 9999)
                        p_isim = "Başlangıç" if "10$" in paket_secimi else ("Profesyonel" if "15$" in paket_secimi else "Sınırsız (Kurumsal)")
                        bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                        st.session_state.mock_users_db[email] = {
                            "password": password, "paket_turu": p_isim, "abonelik_durumu": "aktif", "abonelik_bitis": bitis_tarihi, "kalan_hak": hak, "kategoriler": ["Genel"]
                        }
                        st.success("🎉 Kayıt başarılı! Giriş yapabilirsiniz.")
        elif auth_mode == "Giriş Yap":
            st.info("Hazır hesap: efe@ceyiznet.com / 123")
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
        st.write(f"**Kalan Hak:** Sınırsız ♾️" if u_info['paket_turu'] == "Sınırsız (Kurumsal)" else f"**Kalan Hak:** {u_info['kalan_hak']}")
        st.write("---")
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
            secilen_kat = st.selectbox("Bu CV Hangi Kategoriye Kaydedilsin?", u_info["kategoriler"])
            
            if uploaded_file is not None:
                st.success(f"🔄 {uploaded_file.name} hazır.")
                if st.button("🚀 Analiz Et", type="primary"):
                    if u_info["kalan_hak"] > 0:
                        with st.spinner("Analiz ediliyor..."):
                            ai_result = analyze_cv_mock(uploaded_file.name)
                            st.session_state.ai_results = ai_result
                            
                            ai_result["id"] = len(st.session_state.mock_cvs_db) + 1
                            ai_result["owner_email"] = st.session_state.user_email
                            ai_result["kategori"] = secilen_kat
                            ai_result["durum"] = "Yeni"
                            ai_result["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            st.session_state.mock_cvs_db.append(ai_result)
                            
                            if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                                st.session_state.mock_users_db[st.session_state.user_email]["kalan_hak"] -= 1
                            st.rerun()
                    else:
                        st.error("❌ Limitiniz bitti!")

        with col_right:
            st.subheader("📊 Anlık Sonuç")
            if 'ai_results' in st.session_state:
                res = st.session_state.ai_results
                # Balonlar tamamen silindi
                st.markdown('<div class="result-card">', unsafe_allow_html=True)
                st.markdown(f"### 👤 Kişisel Bilgiler")
                st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Sonuçlar burada görünecek.")

    # 📁 2. SAYFA: CV'LER (SADE SATIR VE SONUNDA RENKLİ DAİRE)
    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        st.subheader("📁 Özelleştirilmiş CV Deposu")
        
        col_kat1, col_kat2 = st.columns([2, 1])
        with col_kat1:
            yeni_kategori = st.text_input("➕ Yeni Kategori İsmi Girin").strip()
        with col_kat2:
            st.write("##")
            if st.button("Kategori Oluştur"):
                if yeni_kategori and yeni_kategori not in u_info["kategoriler"]:
                    st.session_state.mock_users_db[st.session_state.user_email]["kategoriler"].append(yeni_kategori)
                    st.success(f"📂 '{yeni_kategori}' kategorisi oluşturuldu!")
                    st.rerun()
                        
        st.write("---")
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtre_kategori = st.selectbox("📂 Kategori Filtresi:", ["Hepsi"] + u_info["kategoriler"])
        with col_f2:
            filtre_durum = st.selectbox("🎨 Durum Filtresi:", ["Hepsi", "Yeni", "Olumlu", "Nötr", "Olumsuz"])
        
        kullanici_kayitlari = [c for c in st.session_state.mock_cvs_db if c["owner_email"] == st.session_state.user_email]
        if filtre_kategori != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["kategori"] == filtre_kategori]
        if filtre_durum != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["durum"] == filtre_durum]
            
        st.write(f"### 📄 Aday Havuzu ({len(kullanici_kayitlari)} Aday)")
        
        if len(kullanici_kayitlari) > 0:
            for kayit in reversed(kullanici_kayitlari):
                # Duruma göre satırın sonuna eklenecek daire emojisini belirliyoruz
                emoji_map = {"Yeni": "🔵", "Olumlu": "🟢", "Nötr": "🟡", "Olumsuz": "🔴"}
                current_emoji = emoji_map.get(kayit.get("durum", "Yeni"), "🔵")
                
                # Ekran görüntüsü 2026-06-16 110126.png'deki gibi düz expander başlığı ve sonuna renkli daire
                baslik = f"📄 {kayit.get('Ad Soyad')} | Durum: {kayit.get('durum')} | Tarih: {kayit.get('kayit_tarihi')} {current_emoji}"
                
                with st.expander(baslik):
                    st.markdown(f'<div class="category-box">📂 Kategori: {kayit.get("kategori")}</div>', unsafe_allow_html=True)
                    st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    st.write("---")
                    
                    # Buton alanları
                    st.write("**🚥 Durumu Değiştir:**")
                    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
                    with col_b1:
                        if st.button("🟢 Olumlu", key=f"btn_ol__{kayit['id']}"):
                            for idx, cv in enumerate(st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: st.session_state.mock_cvs_db[idx]["durum"] = "Olumlu"
                            st.rerun()
                    with col_b2:
                        if st.button("🟡 Nötr", key=f"btn_no_{kayit['id']}"):
                            for idx, cv in enumerate(st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: st.session_state.mock_cvs_db[idx]["durum"] = "Nötr"
                            st.rerun()
                    with col_b3:
                        if st.button("🔴 Olumsuz", key=f"btn_sz_{kayit['id']}"):
                            for idx, cv in enumerate(st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: st.session_state.mock_cvs_db[idx]["durum"] = "Olumsuz"
                            st.rerun()
                    with col_b4:
                        if st.button("🔵 Yeni", key=f"btn_yn_{kayit['id']}"):
                            for idx, cv in enumerate(st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: st.session_state.mock_cvs_db[idx]["durum"] = "Yeni"
                            st.rerun()

                    st.write("---")
                    yeni_kat_atama = st.selectbox(
                        "Kategori Değiştir:", u_info["kategoriler"], index=u_info["kategoriler"].index(kayit.get("kategori")), key=f"change_kat_{kayit['id']}"
                    )
                    if yeni_kat_atama != kayit.get("kategori"):
                        for idx, cv_item in enumerate(st.session_state.mock_cvs_db):
                            if cv_item["id"] == kayit["id"]: st.session_state.mock_cvs_db[idx]["kategori"] = yeni_kat_atama
                        st.rerun()
        else:
            st.info("Aday bulunamadı.")
