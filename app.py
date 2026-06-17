import streamlit as res_st
import datetime
import time
import hashlib

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

# --- GÜVENLİK İÇİN ŞİFRE HASHLEME FONKSİYONLARI ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# ----------------------------------------
# 🧠 SİMÜLE VERİTABANI (Tarayıcı Hafızası)
# ----------------------------------------
if 'mock_users_db' not in res_st.session_state:
    res_st.session_state.mock_users_db = {
        "efe@ceyiznet.com": {
            "password": make_hashes("123"),
            "paket_turu": "Profesyonel",
            "abonelik_durumu": "aktif",
            "abonelik_bitis": "2026-07-16",
            "kalan_hak": 500,
            "toplam_hak": 500,
            "kategoriler": ["Genel", "Yazılım", "Stajyerler"]
        }
    }

if 'mock_cvs_db' not in res_st.session_state:
    # Testleri hızlandırmak için içeride hazır 2 sahte CV bırakıyoruz
    res_st.session_state.mock_cvs_db = [
        {
            "id": 1,
            "Ad Soyad": "AHMET YILMAZ",
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
            "Ad Soyad": "ELİF KAYA",
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
        "Ad Soyad": f"{filename.split('.')[0].replace('_', ' ').replace('-', ' ').upper()}",
        "Telefon": "+90 532 999 88 77",
        "E-posta": "ornek_aday@ceyiznet.com",
        "Adres": "Maltepe, İstanbul",
        "Deneyim": ["Örnek Şirket - Pozisyon Bilgisi (2 Yıl)"],
        "Yetenekler": "E-Ticaret, Python, Analiz"
    }

# 📜 İSTEK ÜZERİNE ÇALIŞACAK E-POSTA ŞABLON MOTORU
def generate_email_template(aday_isim, durum):
    if durum == "Olumlu":
        return f"Konu: İş Başvurusu Sonucu - Mülakat Daveti\n\nSayın {aday_isim},\n\nŞirketimize yapmış olduğunuz özgeçmiş başvurusu ekiplerimiz tarafından detaylıca incelenmiş ve tecrübeleriniz pozisyonumuz için oldukça olumlu bulunmuştur.\n\nSizinle daha yakından tanışmak ve pozisyon detaylarını görüşmek üzere en kısa sürede bir online mülakat planlamak istiyoruz. Uygun olduğunuz gün ve saat aralıklarını bu e-postayı yanıtlayarak bizimle paylaşebilir misiniz?\n\nSürecimize gösterdiğiniz ilgi için teşekkür eder, iyi günler dileriz.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    elif durum == "Olumsuz":
        return f"Konu: İş Başvurusu Sonucu Bilgilendirmesi\n\nSayın {aday_isim},\n\nŞirketimize göstermiş olduğunuz ilgi ve yapmış olduğunuz iş başvurusu için çok teşekkür ederiz.\n\nÖzgeçmişiniz detaylıca incelenmiş ancak bu pozisyon için aranan spesifik kriterler doğrultusunda şu aşamada sürecimize farklı bir aday ile devam etme kararı alınmıştır. Kariyer yolculuğunuzda başarılar dileriz.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    elif durum == "Nötr":
        return f"Konu: İş Başvurusu Durumu - Değerlendirme Süreci\n\nSayın {aday_isim},\n\nŞirketimize yapmış olduğunuz iş başvurusu İnsan Kaynakları havuzumuza başarıyla kaydedilmiştir. İlgili pozisyona ait değerlendirmelerimiz devam etmekte olup, sürecin tamamlanmasının ardından tarafınıza geri dönüş sağlanacaktır.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"
    else:
        return f"Konu: Başvurunuz Hakkında\n\nSayın {aday_isim},\n\nİş başvurunuz sistemimize ulaştı. Güncel durumunuz 'Yeni' olarak işaretlenmiştir, değerlendirme süreci başlayacaktır.\n\nSaygılarımızla,\nİnsan Kaynakları Departmanı"

# ----------------------------------------
# 🚪 GİRİŞ YAP / KAYIT OL EKRANI
# ----------------------------------------
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
                    if email in res_st.session_state.mock_users_db:
                        res_st.error("Bu e-posta adresi zaten kayıtlı!")
                    else:
                        hak = 100 if "10$" in paket_secimi else (500 if "15$" in paket_secimi else 9999)
                        p_isim = "Başlangıç" if "10$" in paket_secimi else ("Profesyonel" if "15$" in paket_secimi else "Sınırsız (Kurumsal)")
                        bitis_tarihi = (datetime.datetime.now() + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
                        
                        res_st.session_state.mock_users_db[email] = {
                            "password": make_hashes(password), 
                            "paket_turu": p_isim, 
                            "abonelik_durumu": "aktif", 
                            "abonelik_bitis": bitis_tarihi, 
                            "kalan_hak": hak,
                            "toplam_hak": hak,
                            "kategoriler": ["Genel"]
                        }
                        res_st.success("🎉 Kayıt başarılı! 'Giriş Yap' seçeneğine tıklayarak paneline erişebilirsin.")
                else:
                    res_st.warning("Lütfen boş alanları doldurun.")
                    
        elif auth_mode == "Giriş Yap":
            res_st.info("💡 Hazır Hesap: efe@ceyiznet.com / Şifre: 123")
            if res_st.button("Sisteme Giriş Yap", type="primary"):
                if email in res_st.session_state.mock_users_db and check_hashes(password, res_st.session_state.mock_users_db[email]["password"]):
                    res_st.session_state.logged_in = True
                    res_st.session_state.user_email = email
                    res_st.rerun()
                else:
                    res_st.error("Hatalı e-posta veya şifre!")
                    
    with col_auth_right:
        res_st.image("https://img.icons8.com/clouds/300/000000/resume.png")
        res_st.markdown("""
            ### Neden ParserFlow?
            * **Saniyeler İçinde Analiz:** Saatler süren CV okuma sürecini yapay zeka ile sonlandırın.
            * **Akıllı Kategori Yönetimi:** Aday havuzunuzu departmanlara ve şehirlere göre dinamik olarak ayırın.
            * **Tek Tıkla İletişim:** Olumlu veya olumsuz adaylara saniyeler içinde profesyonel geri bildirim mektupları hazırlayın.
        """)

# ----------------------------------------
# 🖥️ ANA SİSTEM (GİRİŞ YAPILDIYSA)
# ----------------------------------------
else:
    u_info = res_st.session_state.mock_users_db[res_st.session_state.user_email]
    
    # 🚪 SOL PANEL (HESAP VE KOTA GÖSTERGESİ)
    with res_st.sidebar:
        res_st.subheader("👤 Hesap Bilgileri")
        res_st.write(f"**Kullanıcı:** {res_st.session_state.user_email}")
        res_st.write(f"**Abonelik:** `{u_info['paket_turu']}`")
        
        # 📊 Gelişmiş Dinamik İlerleme Çubuğu (Kota Kontrolü)
        if u_info['paket_turu'] == "Sınırsız (Kurumsal)":
            res_st.write("**Kalan Hak:** Sınırsız ♾️")
        else:
            kullanilan = u_info['toplam_hak'] - u_info['kalan_hak']
            res_st.write(f"📊 **Kota Kullanımı:** {kullanilan} / {u_info['toplam_hak']} CV")
            res_st.progress(kullanilan / u_info['toplam_hak'])
            if u_info['kalan_hak'] <= 5:
                res_st.error("⚠️ Kotanız bitmek üzere! Paket yükseltin.")
        
        res_st.write("---")
        res_st.subheader("🗺️ Navigasyon")
        sayfa = res_st.radio("Gitmek İstediğiniz Sayfa:", ["🏠 Ana Sayfa (CV Analiz)", "📁 CVler (Yönetim & Kategori)"])
        res_st.write("---")
        if res_st.button("🚪 Güvenli Çıkış"):
            res_st.session_state.logged_in = False
            res_st.session_state.user_email = ""
            res_st.session_state.current_analysis = None
            res_st.rerun()

    # 🏠 SAYFA 1: ANA SAYFA (CV ANALİZ VE GEÇİCİ İNCELEME)
    if sayfa == "🏠 Ana Sayfa (CV Analiz)":
        col_left, col_right = res_st.columns([1, 1.5])

        with col_left:
            res_st.subheader("📁 Özgeçmiş Yükleme")
            uploaded_file = res_st.file_uploader("Bir dosya seçin (PDF, DOCX)", type=["pdf", "docx"])
            
            if uploaded_file is not None:
                res_st.success(f"🔄 {uploaded_file.name} analize hazır.")
                if res_st.button("🚀 Analiz Et", type="primary"):
                    if u_info["paket_turu"] == "Sınırsız (Kurumsal)" or u_info["kalan_hak"] > 0:
                        with res_st.spinner("Yapay Zeka CV'yi parçalıyor..."):
                            res_st.session_state.current_analysis = analyze_cv_mock(uploaded_file.name)
                            res_st.rerun()
                    else:
                        res_st.error("❌ Limitiniz bitti! Lütfen paketinizi yükseltin.")

            # 📥 HAVUZA KAYDETME BÖLÜMÜ (Buradaydı abi, geri geldi)
            if res_st.session_state.current_analysis is not None:
                res_st.write("---")
                res_st.subheader("📥 Havuza Kaydetme Paneli")
                
                ana_secilen_kat = res_st.selectbox("Hangi Kategoriye Kaydedilsin?", u_info["kategoriler"], key="ana_kat_sec")
                ana_secilen_durum = res_st.radio(
                    "🚥 Aday Değerlendirme Durumu Seçin:",
                    ["🔵 Yeni", "🟢 Olumlu", "🟡 Nötr", "🔴 Olumsuz"],
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
                    
                    # Veritabanına ekle
                    res_st.session_state.mock_cvs_db.append(final_cv)
                    
                    # Kota düşür
                    if u_info['paket_turu'] != "Sınırsız (Kurumsal)":
                        res_st.session_state.mock_users_db[res_st.session_state.user_email]["kalan_hak"] -= 1
                    
                    res_st.success(f"💾 {final_cv['Ad Soyad']} havuza başarıyla aktarıldı!")
                    res_st.session_state.current_analysis = None
                    time.sleep(1)
                    res_st.rerun()

        with col_right:
            res_st.subheader("📊 Anlık İnceleme Ekranı")
            if res_st.session_state.current_analysis is not None:
                res = res_st.session_state.current_analysis
                res_st.markdown('<div class="result-card">', unsafe_allow_html=True)
                res_st.markdown(f"### 👤 Ayıklanan Ham Bilgiler")
                res_st.write(f"**Adı Soyadı:** {res.get('Ad Soyad')}")
                res_st.write(f"**📞 Telefon:** {res.get('Telefon')}")
                res_st.write(f"**📧 E-posta:** {res.get('E-posta')}")
                res_st.write(f"**📍 Adres:** {res.get('Adres')}")
                res_st.markdown('</div>', unsafe_allow_html=True)
            else:
                res_st.info("Sol taraftan bir dosya yükleyip 'Analiz Et' butonuna bastığınızda detaylar burada görünecek.")

    # 📁 SAYFA 2: CV'LER (KATEGORİ, RENKLİ DAİRE VE İSTEK ÜZERİNE MEKTUP ÜRETİMİ)
    elif sayfa == "📁 CVler (Yönetim & Kategori)":
        res_st.subheader("📁 Özelleştirilmiş CV Deposu")
        
        # Kategori Oluşturma
        col_kat1, col_kat2 = res_st.columns([2, 1])
        with col_kat1:
            yeni_kategori = res_st.text_input("➕ Yeni Kategori İsmi Girin (Örn: Pazarlama, Muhasebe vb.)").strip()
        with col_kat2:
            res_st.write("##")
            if res_st.button("Kategori Oluştur"):
                if yeni_kategori and yeni_kategori not in u_info["kategoriler"]:
                    res_st.session_state.mock_users_db[res_st.session_state.user_email]["kategoriler"].append(yeni_kategori)
                    res_st.success(f"📂 '{yeni_kategori}' kategorisi oluşturuldu!")
                    res_st.rerun()
                        
        res_st.write("---")
        
        # Filtreler
        col_f1, col_f2 = res_st.columns(2)
        with col_f1:
            filtre_kategori = res_st.selectbox("📂 Kategori Filtresi:", ["Hepsi"] + u_info["kategoriler"])
        with col_f2:
            filtre_durum = res_st.selectbox("🎨 Durum Filtresi:", ["Hepsi", "Yeni", "Olumlu", "Nötr", "Olumsuz"])
        
        # Sadece giriş yapmış kullanıcının CV'lerini getiriyoruz (Güvenlik Duvarı)
        kullanici_kayitlari = [c for c in res_st.session_state.mock_cvs_db if c["owner_email"] == res_st.session_state.user_email]
        
        if filtre_kategori != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["kategori"] == filtre_kategori]
        if filtre_durum != "Hepsi":
            kullanici_kayitlari = [c for c in kullanici_kayitlari if c["durum"] == filtre_durum]
            
        res_st.write(f"### 📄 Aday Havuzu ({len(kullanici_kayitlari)} Aday Listeleniyor)")
        
        if len(kullanici_kayitlari) > 0:
            for kayit in reversed(kullanici_kayitlari):
                emoji_map = {"Yeni": "🔵", "Olumlu": "🟢", "Nötr": "🟡", "Olumsuz": "🔴"}
                current_emoji = emoji_map.get(kayit.get("durum", "Yeni"), "🔵")
                
                # Tam senin istediğin o sade satır ve sonundaki daire yapısı abi
                baslik = f"📄 {kayit.get('Ad Soyad')} | Durum: {kayit.get('durum')} | Tarih: {kayit.get('kayit_tarihi')} {current_emoji}"
                
                with res_st.expander(baslik):
                    res_st.markdown(f'<div class="category-box">📂 Kategori: {kayit.get("kategori")}</div>', unsafe_allow_html=True)
                    res_st.write(f"**📞 Telefon:** {kayit.get('Telefon')}")
                    res_st.write(f"**📧 E-posta:** {kayit.get('E-posta')}")
                    res_st.write(f"**📍 Adres:** {kayit.get('Adres')}")
                    
                    res_st.write("---")
                    res_st.write("**🚥 Durumu Değiştir:**")
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

                    # ✉️ İSTEK ÜZERİNE BİLDİRİM MEKTUBU HAZIRLAMA (Geri geldi abi)
                    res_st.write("---")
                    res_st.write("**✉️ Aday İletişim Yönetimi:**")
                    
                    state_key = f"email_generated_{kayit['id']}"
                    if state_key not in res_st.session_state:
                        res_st.session_state[state_key] = False
                        
                    if res_st.button(f"✨ Bu Aday İçin E-posta Taslağı Üret", key=f"generate_btn_{kayit['id']}"):
                        res_st.session_state[state_key] = True
                    
                    if res_st.session_state[state_key]:
                        sablon_metin = generate_email_template(kayit.get('Ad Soyad'), kayit.get('durum'))
                        res_st.markdown(f'<div class="email-box">{sablon_metin}</div>', unsafe_allow_html=True)
                        
                        if res_st.button("❌ Taslağı Kapat", key=f"close_email_{kayit['id']}"):
                            res_st.session_state[state_key] = False
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
