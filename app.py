import streamlit as st
import datetime
import time

# 3. Arayüz Tasarımı (En Üste Alındı)
st.set_page_config(page_title="AI CV Parser Pro", page_icon="🤖", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f4f6f9; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
    .result-card { background-color: #ffffff; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); margin-bottom: 15px; }
    .bullet-item { background-color: #f8fafc; padding: 10px 15px; border-left: 4px solid #3b82f6; border-radius: 4px; margin-bottom: 8px; font-size: 14px; }
    </style>
""", unsafe_allow_html=True)

st.title("🤖 Yapay Zeka Destekli CV Analiz Merkezi [HAFİF TEST MODU]")
st.warning("⚡ MongoDB kaldırıldı! Sistem şu an tamamen tarayıcı hafızasında çalışıyor. Bağlantı hatası riski YOKTUR.")

# ----------------------------------------
# 🧠 SİMÜLE VERİTABANI (Tarayıcı Hafızası)
# ----------------------------------------
if 'mock_users_db' not in st.session_state:
    # Sisteme test için varsayılan bir kullanıcı ekliyoruz
    st.session_state.mock_users_db = {
        "efe@ceyiznet.com": {
            "password": "123",
            "paket_turu": "Profesyonel",
            "abonelik_durumu": "aktif",
            "abonelik_bitis": "2026-07-16",
            "kalan_hak": 500
        }
    }

if 'mock_cvs_db' not in st.session_state:
    st.session_state.mock_cvs_db = [] # Yüklenen CV'lerin tutulacağı liste

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""

# Test Analiz Fonksiyonu
def analyze_cv_mock(filename):
    time.sleep(0.8) # Yapay zeka yükleniyor efekti
    return {
        "Ad Soyad": f"Aday: {filename.split('.')[0].upper()}",
        "Telefon": "+90 532 999 88 77",
        "E-posta": "ornek_aday@ceyiznet.com",
        "Adres": "Maltepe, İstanbul",
        "Deneyim": [
            "CSS Ship Management - Stajyer (6 Ay)",
            "Ceyiznet - E-Ticaret Yöneticisi (1 Yıl)"
        ],
        "Yetenekler": "E-Ticaret, Python, Analiz, Pazarlama"
    }

# ----------------------------------------
# 🚪 YAN PANEL: SIFIR HATA ÜYELİK SİSTEMİ
# ----------------------------------------
with st.sidebar:
    if not st.session_state.logged_in:
        st.subheader("🔐 Kullanıcı Paneli")
        auth_mode = st.radio("İşlem Seçin", ["Giriş Yap", "Kayıt Ol"])
        
        email = st.text_input("E-posta Adresi (Test için)").strip()
        password = st.text_input("Şifre", type="password")
        
        if auth_mode == "Kayıt Ol":
            paket_secimi = st.selectbox("Satın Alınacak Paket", [
                "Başlangıç Paketi (10$ - 100 CV)", 
                "Profesyonel Paket (15$ - 500 CV)", 
                "Kurumsal Paket (25$ - Sınırsız CV)"
            ])
            
            if st.button("Hesap Oluştur (Anında & Bedava)"):
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
                        
                        # Sahte veritabanımıza ekliyoruz
                        st.session_state.mock_users_db[email] = {
                            "password": password,
                            "paket_turu": p_isim,
                            "abonelik_durumu": "aktif",
                            "abonelik_bitis": bitis_tarihi,
                            "kalan_hak": hak
                        }
                        st.success(f"🎉 {p_isim} paket hesabınız yaratıldı! Giriş Yap sekmesine geçip girebilirsiniz.")
                else:
                    st.warning("Lütfen alanları doldurun.")
                    
        elif auth_mode == "Giriş Yap":
            st.info("Hazır hesapla girmek için:\n\n**E-posta:** efe@ceyiznet.com\n\n**Şifre:** 123")
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
        st.write(f"**Durum:** {u_info['abonelik_durumu'].upper()}")
        st.write(f"**Bitiş Tarihi:** {u_info['abonelik_bitis']}")
        
        if u_info['paket_turu'] == "Sınırsız (Kurumsal)":
            st.write("**Kalan Analiz Hakkı:** Sınırsız ♾️")
        else:
            st.write(f"**Kalan Analiz Hakkı:** {u_info['kalan_hak']}")
            
        if st.button("Çıkış Yap"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            if 'ai_results' in st.session_state:
                del st.session_state.ai_results
            st.rerun()

# ----------------------------------------
# 🖥️ ANA İÇERİK ALANI
# ----------------------------------------
if not st.session_state.logged_in:
    st.info("ℹ️ Giriş yapmadan paneli göremezsiniz. Lütfen sol taraftan giriş yapın.")
else:
    col_left, col_right = st.columns([1, 1.5])

    with col_left:
        st.subheader("📁 Özgeçmiş Yükleme")
        uploaded_file = st.file_uploader("Herhangi bir dosya seçin", type=["pdf", "docx"])
        
        if uploaded_file is not None:
            st.success(f"🔄 {uploaded_file.name} hazır.")
            st.write("---")
            
            if st.button("🚀 Analiz Et", type="primary"):
                u_info = st.session_state.mock_users_db[st.session_state.user_email]
                
                if u_info["kalan_hak"] > 0:
                    with st.spinner("Analiz ediliyor..."):
                        ai_result = analyze_cv_mock(uploaded_file.name)
                        st.session_state.ai_results = ai_result
                        
                        # Geçmişe kaydetme simülasyonu
                        ai_result["owner_email"] = st.session_state.user_email
                        ai_result["kayit_tarihi"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.mock_cvs_db.append(ai_result)
                        
                        # Hafızadaki hesaptan hakkı 1 düşürüyoruz
                        if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                            st.session_state.mock_users_db[st.session_state.user_email]["kalan_hak"] -= 1
                            
                        st.success("💾 Analiz tamamlandı, hakkınız düşüldü!")
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
            
            st.markdown('<div class="result-card">', unsafe_allow_html=True)
            st.markdown(f"### 💼 İş Tecrübeleri")
            for is_madde in res.get('Deneyim', []):
                st.markdown(f'<div class="bullet-item">💼 {is_madde}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Sonuçlar burada görünecek.")

    # GEÇMİŞ PANELİ (SADECE O KULLANICIYA AİT)
    st.write("---")
    st.subheader("🗄️ Geçmiş CV Analizleriniz")

    # Genel listeden sadece aktif kullanıcınınkileri süzüyoruz
    kullanici_kayitlari = [c for c in st.session_state.mock_cvs_db if c["owner_email"] == st.session_state.user_email]
    
    if len(kullanici_kayitlari) > 0:
        for kayit in reversed(kullanici_kayitlari):
            with st.expander(f"📄 {kayit.get('Ad Soyad')} - {kayit.get('kayit_tarihi')}"):
                st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                st.write("**💼 Deneyimler:**")
                for d in kayit.get('Deneyim', []):
                    st.write(f"- {d}")
    else:
        st.info("Geçmiş analiziniz bulunmuyor.")
