import streamlit as res_st
import datetime
import time

# 3. Arayüz Tasarımı
res_st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

res_st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; border: 1px solid #e2e8f0; margin-bottom: 15px; }
    .category-box { background-color: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px; font-weight: bold; color: #475569; display: inline-block; margin-bottom: 10px; margin-right: 5px;}
    </style>
""", unsafe_allow_html=True)

res_st.title("🤖 Yapay Zeka Destekli Gelişmiş CV Yönetim Merkezi")

# ----------------------------------------
# 🧠 SİMÜLE VERİTABANI (Tarayıcı Hafızası)
# ----------------------------------------
if 'mock_users_db' not in res_st.session_state:
    res_st.session_state.mock_users_db = {
        "efe@ceyiznet.com": {
            "password": "123",
            "paket_turu": "Profesyonel",
            "abonelik_durumu": "aktif",
            "abonelik_bitis": "2026-07-16",
            "kalan_hak": 500,
            "kategoriler": ["Genel", "Yazılım", "Stajyerler"]
        }
    }

if 'mock_cvs_db' not in res_st.session_state:
    res_st.session_state.mock_cvs_db = [
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

if 'logged_in' not in res_st.session_state:
    res_st.session_state.logged_in = False
if 'user_email' not in res_st.session_state:
    res_st.session_state.user_email = ""
if 'current_analysis' not in res_st.session_state:
    res_st.session_state.current_analysis = None

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
with res_st.sidebar:
    if not res_st.session_state.logged_in:
        res_st.subheader("🔐 Kullanıcı Paneli")
        auth_mode = res_st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"])
        email = res_st.text_input("E-posta Adresi").strip()
        password = res_st.text_input("Şifre", type="password")
        
        if auth_mode == "Kayıt Ol":
            paket_secimi = res_st.selectbox("Satın Alınacak Paket", ["Başlangıç Paketi (10$)", "Profesyonel Paket (15$)", "Kurumsal Paket (25$)"])
            if res_st.button("Hesap Oluştur"):
                if email and password:
                    if email in res_st.session_state.mock_users_db:
                        res_st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        hak = 100 if "10$" in paket_secimi else (500 if "15$" in paket_secimi else 9999)
                        p_isim = "Başlangıç" if "10$" in paket_secimi else ("Profesyonel" if "15$" in paket_secimi else "Sınırsız (Kurumsal)")
                        bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                        res_st.session_state.mock_users_db[email] = {
                            "password": password, "paket_turu": p_isim, "abonelik_durumu": "aktif", "abonelik_bitis": bitis_tarihi, "kalan_hak": hak, "kategoriler": ["Genel"]
                        }
                        res_st.success("🎉 Kayıt başarılı! Giriş yapabilirsiniz.")
        elif auth_mode == "Giriş Yap":
            res_st.info("Hazır hesap: efe@ceyiznet.com / 123")
            if res_st.button("Giriş Yap"):
                if email in res_st.session_state.mock_users_db and res_st.session_state.mock_users_db[email]["password"] == password:
                    res_st.session_state.logged_in = True
                    res_st.session_state.user_email = email
                    res_st.rerun()
                else:
                    res_st.error("Hatalı e-posta veya şifre!")
    else:
        st_user = res_st.session_state.user_email
        u_info = res_st.session_state.mock_users_db[st_user]
        
        res_st.subheader("👤 Hesap Bilgileri")
        res_st.write(f"**Kullanıcı:** {st_user}")
        res_st.write(f"**Paket:** {u_info['paket_turu']}")
        res_st.write(f"**Kalan Hak:** Sınırsız ♾️" if u_info['paket_turu'] == "Sınırsız (Kurumsal)" else f"**Kalan Hak:** {u_info['kalan_hak']}")
        res_st.write("---")
        res_st.subheader("🗺️ Menü")
        sayfa = res_st.radio("Gitmek İstediğiniz Sayfa:", ["🏠 Ana Sayfa (CV Analiz)", "📁 CVler (Yönetim & Kategori)"])
        res_st.write("---")
        if res_st.button("Çıkış Yap"):
            res_st.session_state.logged_in = False
            res_st.session_state.user_email = ""
            res_st.session_state.current_analysis = None
            res_st.rerun()

# ----------------------------------------
# 🖥️ ANA İÇERİK ALANI
# ----------------------------------------
if not res_st.session_state.logged_in:
    res_st.info("ℹ️ Lütfen sol panelden giriş yapın.")
else:
    u_info = res_st.session_state.mock_users_db[res_st.session_state.user_email]

    # 🏠 1. SAYFA: ANA SAYFA (CV ANALİZ)
    if sayfa == "🏠 Ana Sayfa (CV Analiz)":
        col_left, col_right = res_st.columns([1, 1.5])

        with col_left:
            res_st.subheader("📁 Özgeçmiş Yükleme")
            uploaded_file = res_st.file_uploader("Bir dosya seçin", type=["pdf", "docx"])
            
            if uploaded_file is not None:
                res_st.success(f"🔄 {uploaded_file.name} hazır.")
                if res_st.button("🚀 Analiz Et", type="primary"):
                    if u_info["kalan_hak"] > 0:
                        with res_st.spinner("Analiz ediliyor..."):
                            res_st.session_state.current_analysis = analyze_cv_mock(uploaded_file.name)
                            res_st.rerun()
                    else:
                        res_st.error("❌ Limitiniz bitti!")

            if res_st.session_state.current_analysis is not None:
                res_st.write("---")
                res_st.subheader("📥 Havuza Kaydetme Paneli")
                
                ana_secilen_kat = res_st.selectbox("Hangi Kategoriye Kaydedilsin?", u_info["kategoriler"], key="ana_kat_sec")
                
                ana_secilen_durum = res_st.radio(
                    "🚥 Aday Değerlendirme Durumu:",
                    ["🔵 Yeni / Belirsiz", "🟢 Olumlu", "🟡 Nötr", "🔴 Olumsuz"],
                    horizontal=True
                )
                
                durum_clean = ana_secilen_durum.split(" ")[1] 
                
                if res_st.button("💾 Havuza Güvenle Kaydet", type="secondary"):
                    final_cv = res_st.session_state.current_analysis.copy()
                    final_cv["id"] = len(res_st.session_state.mock_cvs_db) + 1
                    final_cv["owner_email"] = res_st.session_state.user_email
                    final_cv["kategori"] = ana_secilen_kat
                    final_cv["durum"] = durum_clean
                    final_cv["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    res_st.session_state.mock_cvs_db.append(final_cv)
                    
                    if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                        res_st.session_state.mock_users_db[res_st.session_state.user_email]["kalan_hak"] -= 1
                    
                    res_st.success(f"💾 CV başarıyla '{ana_secilen_kat}' kategorisine kaydedildi!")
                    res_st.session_state.current_analysis = None
                    time.sleep(1)
                    res_st.rerun()

        with col_right:
            res_st.subheader("📊 Anlık İnceleme Ekranı")
            if res_st.session_state.current_analysis is not None:
                res = res_st.session_state.current_analysis
                res_st.markdown('<div class="result-card">', unsafe_allow_html=True)
                res_st.markdown(f"### 👤 Ayıklanan Bilgiler")
                res_st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                res_st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                res_st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                res_st.write(f"**📍 Adres:** {res.get('Adres')}")
                res_st.markdown('</div>', unsafe_allow_html=True)
            else:
                res_st.info("Sol taraftan bir dosya yükleyip 'Analiz Et' butonuna bastığınızda detaylar burada görünecek.")

    # 📁 2. SAYFA: CV'LER (SADE SATIR VE SONUNDA RENKLİ DAİRE)
    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        res_st.subheader("📁 Özelleştirilmiş CV Deposu")
        
        col_kat1, col_kat2 = res_st.columns([2, 1])
        with col_kat1:
            yeni_kategori = res_st.text_input("➕ Yeni Kategori İsmi Girin").strip()
        with col_kat2:
            res_st.write("##")
            if res_st.button("Kategori Oluştur"):
                if yeni_kategori and yeni_kategori not in u_info["kategoriler"]:
                    res_st.session_state.mock_users_db[res_st.session_state.user_email]["kategoriler"].append(yeni_kategori)
                    res_st.success(f"📂 '{yeni_kategori}' kategorisi oluşturuldu!")
                    res_st.rerun()
                        
        res_st.write("---")
        
        col_f1, col_f2 = res_st.columns(2)
        with col_f1:
            filtre_kategori = res_st.selectbox("📂 Kategori Filtresi:", ["Hepsi"] + u_info["kategoriler"])
        with col_f2:
            filtre_durum = res_st.selectbox("🎨 Durum Filtresi:", ["Hepsi", "Yeni", "Olumlu", "Nötr", "Olumsuz"])
        
        kullanici_kayitlari = [c for c in res_st.session_state.mock_cvs_db if c["owner_email"] == res_st.session_state.user_email]
        if filtre_kategori != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["kategori"] == filtre_kategori]
        if filtre_durum != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["durum"] == filtre_durum]
            
        res_st.write(f"### 📄 Aday Havuzu ({len(kullanici_kayitlari)} Aday)")
        
        if len(kullanici_kayitlari) > 0:
            for kayit in reversed(kullanici_kayitlari):
                emoji_map = {"Yeni": "🔵", "Olumlu": "🟢", "Nötr": "🟡", "Olumsuz": "🔴"}
                current_emoji = emoji_map.get(kayit.get("durum", "Yeni"), "🔵")
                
                baslik = f"📄 {kayit.get('Ad Soyad')} | Durum: {kayit.get('durum')} | Tarih: {kayit.get('kayit_tarihi')} {current_emoji}"
                
                with res_st.expander(baslik):
                    res_st.markdown(f'<div class="category-box">📂 Kategori: {kayit.get("kategori")}</div>', unsafe_allow_html=True)
                    res_st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    res_st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    res_st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    res_st.write("---")
                    
                    res_st.write("**🚥 Durumu Buradan da Güncelleyebilirsiniz:**")
                    col_b1, col_b2, col_b3, col_b4 = res_st.columns(4)
                    with col_b1:
                        if res_st.button("🟢 Olumlu", key=f"btn_ol__{kayit['id']}"):
                            for idx, cv in enumerate(res_st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: res_st.session_state.mock_cvs_db[idx]["durum"] = "Olumlu"
                            res_st.rerun()
                    with col_b2:
                        if res_st.button("🟡 Nötr", key=f"btn_no_{kayit['id']}"):
                            for idx, cv in enumerate(res_st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: res_st.session_state.mock_cvs_db[idx]["durum"] = "Nötr"
                            res_st.rerun()
                    with col_b3:
                        if res_st.button("🔴 Olumsuz", key=f"btn_sz_{kayit['id']}"):
                            for idx, cv in enumerate(res_st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: res_st.session_state.mock_cvs_db[idx]["durum"] = "Olumsuz"
                            res_st.rerun()
                    with col_b4:
                        if res_st.button("🔵 Yeni", key=f"btn_yn_{kayit['id']}"):
                            for idx, cv in enumerate(res_st.session_state.mock_cvs_db):
                                if cv["id"] == kayit["id"]: res_st.session_state.mock_cvs_db[idx]["durum"] = "Yeni"
                            res_st.rerun()

                    res_st.write("---")
                    yeni_kat_atama = res_st.selectbox(
                        "Kategori Değiştir:", u_info["kategoriler"], index=u_info["kategoriler"].index(kayit.get("kategori")), key=f"change_kat_{kayit['id']}"
                    )
                    if yeni_kat_atama != kayit.get("kategori"):
                        for idx, cv_item in enumerate(res_st.session_state.mock_cvs_db):
                            if cv_item["id"] == kayit["id"]: res_st.session_state.mock_cvs_db[idx]["kategori"] = yeni_kat_atama
                        res_st.rerun()
        else:
            res_st.info("Aday bulunamadı.")
