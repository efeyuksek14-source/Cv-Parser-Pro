import streamlit as st
import hashlib

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="ParserFlow - ATS", page_icon="🚀", layout="wide")

# --- GÜVENLİK İÇİN ŞİFRE HASHLEME FONKSİYONU ---
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return True
    return False

# --- GEÇİCİ VERİTABANI (SESSION STATE) İLKLENDİRME ---
# Gerçek veritabanına geçmeden önce sistemi ayakta tutan simülasyon yapısı
if 'users_db' not in st.session_state:
    # Örnek hazır kullanıcılar: şifreleri '1234' olarak hashlenmiş
    st.session_state.users_db = {
        "admin": {"password": make_hashes("1234"), "package": "Premium", "quota": 1000, "used_quota": 45},
        "test_ik": {"password": make_hashes("1234"), "package": "Free Trial", "quota": 20, "used_quota": 19}
    }

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

if 'cv_pool' not in st.session_state:
    st.session_state.cv_pool = []

# --- KULLANICI GİRİŞ/KAYIT PANELİ ---
def login_register_page():
    st.title("🚀 ParserFlow - Akıllı ATS Dünyasına Hoş Geldiniz")
    st.subheader("Karmakarışık CV'leri saniyeler içinde profesyonel bir akışa dönüştürün.")
    
    tab1, tab2 = st.tabs(["🔒 Giriş Yap", "📝 Kayıt Ol (Ücretsiz Dene)"])
    
    with tab1:
        st.write("### Hesabınıza Giriş Yapın")
        username = st.text_input("Kullanıcı Adı / E-posta", key="login_user")
        password = st.text_input("Şifre", type="password", key="login_pass")
        
        if st.button("Sisteme Giriş Yap", type="primary"):
            if username in st.session_state.users_db:
                hashed_pass = st.session_state.users_db[username]["password"]
                if check_hashes(password, hashed_pass):
                    st.session_state.logged_in = True
                    st.session_state.current_user = username
                    st.success(f"Başarıyla giriş yapıldı! Hoş geldin {username} 👋")
                    st.rerun()
                else:
                    st.error("Hatalı şifre girdiniz. Lütfen tekrar deneyin.")
            else:
                st.error("Kullanıcı bulunamadı. Lütfen kayıt olun.")
                
    with tab2:
        st.write("### ParserFlow Üyesi Olun")
        new_user = st.text_input("Kullanıcı Adı Belirleyin", key="reg_user")
        new_pass = st.text_input("Güçlü Bir Şifre Belirleyin", type="password", key="reg_pass")
        confirm_pass = st.text_input("Şifreyi Tekrar Girin", type="password", key="reg_confirm")
        
        if st.button("Hesabımı Oluştur ve Başlat"):
            if not new_user or not new_pass:
                st.warning("Lütfen tüm alanları doldurun.")
            elif new_user in st.session_state.users_db:
                st.error("Bu kullanıcı adı zaten alınmış. Başka bir tane deneyin.")
            elif new_pass != confirm_pass:
                st.error("Şifreler birbiriyle uyuşmuyor.")
            else:
                # Yeni kayıt olan kullanıcıya otomatik "Free Trial" paketi ve 20 kota tanımlıyoruz
                st.session_state.users_db[new_user] = {
                    "password": make_hashes(new_pass),
                    "package": "Free Trial",
                    "quota": 20,
                    "used_quota": 0
                }
                st.success("Hesabınız başarıyla oluşturuldu! Şimdi 'Giriş Yap' sekmesinden giriş yapabilirsiniz.")

# --- ANA UYGULAMA PANELİ (GİRİŞ BAŞARILIYSA) ---
def main_app():
    user = st.session_state.current_user
    user_data = st.session_state.users_db[user]
    
    # --- KENAR ÇUBUĞU (SIDEBAR) & KOTA GÖSTERGESİ ---
    with st.sidebar:
        st.image("https://img.icons8.com/clouds/100/000000/resume.png", width=80)
        st.title("ParserFlow")
        st.write(f"👤 **Kullanıcı:** {user}")
        st.write(f"📦 **Paket:** `{user_data['package']}`")
        
        # Kota Durum Çubuğu
        remaining = user_data['quota'] - user_data['used_quota']
        st.write(f"📊 **Kota:** {user_data['used_quota']} / {user_data['quota']} CV")
        st.progress(user_data['used_quota'] / user_data['quota'])
        
        if remaining <= 1:
            st.error("⚠️ Kotanız bitmek üzere! Paket yükseltin.")
            if st.button("🚀 Şimdi Premium'a Geç"):
                st.toast("Ödeme sayfasına yönlendiriliyorsunuz... (Sanal POS Entegrasyonu Yakında)")
        
        st.write("---")
        menu = st.radio("Menü", ["📤 CV Analiz Merkezi", "📂 İK Aday Havuzu", "⚙️ Hesap Ayarları"])
        
        st.write("---")
        if st.button("🚪 Çıkış Yap", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.current_user = None
            st.rerun()

    # --- MENÜ İÇERİKLERİ ---
    if menu == "📤 CV Analiz Merkezi":
        st.header("📤 Yapay Zeka CV Analiz Merkezi")
        
        # Kota Kontrolü
        if user_data['used_quota'] >= user_data['quota']:
            st.error("❌ Aylık CV yükleme kotanız dolmuştur. Yeni analiz yapmak için lütfen paketinizi yükseltin.")
        else:
            uploaded_file = st.file_uploader("Analiz edilecek CV'yi sürükleyin veya seçin (PDF)", type=["pdf"])
            if uploaded_file is not None:
                st.info(f"'{uploaded_file.name}' başarıyla yüklendi.")
                
                if st.button("ParserFlow Yapay Zekası ile Analiz Et", type="primary"):
                    # Kota düşümü simülasyonu
                    st.session_state.users_db[user]['used_quota'] += 1
                    st.success("CV başarıyla analiz edildi ve İK Havuzuna eklendi! (Kota 1 adet düşürüldü)")
                    st.rerun()

    elif menu == "📂 İK Aday Havuzu":
        st.header("📂 İK Aday Havuzu")
        st.write("Burada analiz edilen CV'lerin listesi, durumları ve otomatik e-posta taslakları yer alacak.")
        # Önceki aşamada yazdığımız havuz tablosu kodları buraya gelecek.

    elif menu == "⚙️ Hesap Ayarları":
        st.header("⚙️ Hesap Ayarları & Abonelik Yönetimi")
        st.subheader("Mevcut Abonelik Detayları")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Mevcut Paket", user_data['package'])
        col2.metric("Toplam Kota", f"{user_data['quota']} CV")
        col3.metric("Kalan Kota", f"{user_data['quota'] - user_data['used_quota']} CV")


# --- UYGULAMA AKIŞ KONTROLÜ ---
if not st.session_state.logged_in:
    login_register_page()
else:
    main_app()
