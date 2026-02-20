import streamlit as st
import time
import random
from datetime import datetime
import streamlit.components.v1 as components

# =========================
# SETUP (mobile-friendly)
# =========================
st.set_page_config(
    page_title="Comfort Zone",
    page_icon="☁️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
.main{
  background: radial-gradient(circle at 15% 15%, #ffe3ea 0%, #fff7fb 35%, #f7fbff 100%);
}
.block-container{
  padding-top: 1.0rem;
  padding-bottom: 2.2rem;
  max-width: 720px;
}
.card{
  background: rgba(255,255,255,0.88);
  border: 1px solid rgba(255,75,75,0.14);
  border-radius: 16px;
  padding: 14px 14px;
  box-shadow: 0 10px 22px rgba(0,0,0,0.06);
  margin-bottom: 12px;
}
.hr{ height:1px; background: rgba(0,0,0,0.06); margin: 12px 0; }
.muted{ color: rgba(43,43,43,0.65); }

button[kind="primary"], button[kind="secondary"], .stButton button{
  border-radius: 14px !important;
  padding: 0.68rem 0.9rem !important;
  font-size: 1.02rem !important;
}
.stTextInput input, .stTextArea textarea{
  font-size: 1.02rem !important;
}
@media (max-width: 640px){
  .block-container{ padding-left: 0.9rem; padding-right: 0.9rem; }
  h1{ font-size: 1.55rem !important; }
  h2{ font-size: 1.20rem !important; }
  h3{ font-size: 1.05rem !important; }
}
</style>
""", unsafe_allow_html=True)

# =========================
# STATE
# =========================
if "authed" not in st.session_state:
    st.session_state.authed = False
if "nama" not in st.session_state:
    st.session_state.nama = ""

# draft + flash message (biar auto-clear tanpa error)
if "draft" not in st.session_state:
    st.session_state.draft = ""
if "flash_ok" not in st.session_state:
    st.session_state.flash_ok = ""

# ✅ 2-step login ketat + auto pindah halaman (no klik ke-3)
if "login_stage" not in st.session_state:
    st.session_state.login_stage = 0      # 0=belum, 1=nunggu klik kedua
if "login_token" not in st.session_state:
    st.session_state.login_token = None
if "login_ts" not in st.session_state:
    st.session_state.login_ts = 0.0

SECRET = "nadaaa"

# =========================
# COPY
# =========================
KALIMAT_TENANG = [
    "Pelan-pelan aja ya. Kalau capek, istirahat dulu juga gapapa.",
    "Kalau hari ini berat, kamu nggak perlu maksa keliatan kuat.",
    "Kamu udah berusaha. Itu aja udah berarti.",
    "Kalau pikiran rame, lagi ada pasar malam ya wkwk.",
    "Dunia tetap berputar walau kamu berhenti sejenak untuk rehat.",
    "Malam ini, biarkan dunia berjalan tanpa campur tanganmu.",
    "Bukan kamu yang kurang berusaha, melainkan kamu yang kurang berserah padanya."
]

GOMBAL_LUCU = [
    "Cuka, cuka apa yang paling manis? Cuka sama kamu.",
    "Kipas, kipas apa yang paling ditunggu cewek? Kipastian dari kamu.",
    "Kamu tahu nggak bedanya kamu sama modem? Kalau modem terhubung ke internet, kalau kamu terhubung ke… ya pokoknya.",
    "Sate, sate apa yang paling enak? Saterusnya ama Nada.",
    "Kamu tahu bedanya kamu sama nasi? Kalau nasi itu kebutuhan pokok, kalau kamu itu pokoknya harus ada.",
    "Kenapa donat tengahnya bolong? Karena yang utuh cumaaa… ya pokoknya wkwk.",
    "Kamu tahu kenapa air laut asin? Karena manisnya udah diambil semua sama kamu.",
    "Kalau kangen itu dosa, mungkin aku udah masuk daftar paling dicari sekarang."
]

GROUNDING = [
    "5–4–3–2–1: sebutin 5 yang kamu lihat, 4 yang kamu sentuh, 3 yang kamu dengar, 2 yang kamu cium, 1 yang kamu rasain di mulut.",
    "Tangan di dada: tarik napas 4 hitungan, tahan 2, hembus 6. Ulang 5 kali.",
    "Minum air pelan-pelan. Fokus ke sensasinya sebentar. Cukup 3 teguk."
]

SYUKUR_PROMPTS = [
    "Hari ini… ada satu hal kecil yang kamu syukuri nggak? boleh sederhana banget.",
    "Kalau kamu mau, sebutin satu hal yang bikin kamu ngerasa ‘oh… masih ada yang baik’.",
    "Ada satu hal yang pengen kamu ucapin ‘makasih’ hari ini? sekecil apa pun itu.",
    "Coba sebutin satu hal yang bikin kamu bertahan hari ini. itu juga layak disyukuri."
]

PLAYLISTS = [
    "https://www.youtube.com/watch?v=im99Picx79Q&list=RDim99Picx79Q&start_radio=1",
    "https://www.youtube.com/watch?v=mJE0ROBWPvY&list=RDmJE0ROBWPvY&start_radio=1",
    "https://www.youtube.com/watch?v=yNcGtKAacts&list=RDyNcGtKAacts&start_radio=1",
    "https://www.youtube.com/watch?v=cR8mSOz0eyI&list=RDcR8mSOz0eyI&start_radio=1",
]

def extract_youtube_id(url: str) -> str | None:
    try:
        if "v=" not in url:
            return None
        part = url.split("v=", 1)[1]
        vid = part.split("&", 1)[0]
        return vid.strip() if vid else None
    except Exception:
        return None

# =========================
# CALLBACK (buang aja)
# =========================
def throw_draft():
    st.session_state.draft = ""       # aman (callback)
    st.session_state.flash_ok = "Oke. Yang tadi kita buang aja ya."

# =========================
# LOGIN PAGE (separate)
# =========================
if not st.session_state.authed:
    st.markdown(
        '<div class="card">'
        '<h1 style="margin:0;">akal akalan teknik ☁️</h1>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="card"><b>Login duluuuu</b><div class="hr"></div></div>', unsafe_allow_html=True)

    nama = st.text_input("Masukin namanya (kutengg?? wkwkw)", value=st.session_state.nama)
    code = st.text_input("password : (nada a nya 3)", type="password")

    st.session_state.nama = nama
    current_token = f"{nama.strip()}|{code}"

    if st.button("Masuk", use_container_width=True):
        if code != SECRET:
            st.session_state.login_stage = 0
            st.session_state.login_token = None
            st.session_state.login_ts = 0.0
            st.error("Passwordnya salah.")
            st.stop()

        now = time.time()

        # Klik pertama / input beda / kelamaan -> ARM
        if (
            st.session_state.login_stage == 0
            or st.session_state.login_token != current_token
            or (now - st.session_state.login_ts) > 20
        ):
            st.session_state.login_stage = 1
            st.session_state.login_token = current_token
            st.session_state.login_ts = now
            st.info("Oke… tekan **Masuk** sekali lagi ya.")
            st.stop()

        # Klik kedua -> login + pindah tanpa klik ke-3
        st.session_state.authed = True
        st.session_state.login_stage = 0
        st.session_state.login_token = None
        st.session_state.login_ts = 0.0
        st.success("Masuk.")
        st.rerun()

    # Kalau user ubah input setelah klik pertama -> reset
    if st.session_state.login_stage == 1 and st.session_state.login_token != current_token:
        st.session_state.login_stage = 0
        st.session_state.login_token = None
        st.session_state.login_ts = 0.0
        st.caption("Input berubah, jadi ulang dari klik pertama ya.")

    st.stop()

# =========================
# MAIN APP
# =========================
st.markdown(
    '<div class="card">'
    '<h2 style="margin:0;">Dunia mungkin lagi berisik, tapi di sini tenang kok. Take your time ya, Nadaaa. ☁️🍃</h2>'
    '</div>',
    unsafe_allow_html=True
)

# ====== KOTAK RAHASIA (tanpa simpan) ======
st.markdown(
    '<div class="card"><b>Ecek eceknya ini kotak rahasia ya wkwk</b>'
    '<div class="hr"></div>'
    '<div class="muted">Kalau ada yang ganjel dan pengen dibuang, tulis di sini ya. Satu kata juga gapapa, yang penting jangan dipendem sendiri</div>'
    '</div>',
    unsafe_allow_html=True
)

st.text_area("", placeholder="tulis di sini…", label_visibility="collapsed", key="draft", height=140)

b1, b2 = st.columns(2)
with b1:
    st.button("Buang aja", use_container_width=True, on_click=throw_draft)
with b2:
    if st.button("Kalimat tenang", use_container_width=True):
        st.info(random.choice(KALIMAT_TENANG))

if st.session_state.flash_ok:
    st.success(st.session_state.flash_ok)
    st.session_state.flash_ok = ""

# ====== SELF-CARE PACKAGE ======
st.markdown(
    '<div class="card"><b>Self-Care Package 🎁</b>'
    '<div class="hr"></div><div class="muted">Pilih satu yang paling kamu butuhin sekarang:</div></div>',
    unsafe_allow_html=True
)

choice = st.selectbox("Aku butuh...", ["Virtual Hug", "KIW KIW"])

if st.button("Aktifkan Protokol", use_container_width=True):
    if choice == "Virtual Hug":
        st.snow()
        st.write("🫂 ututututututuuu teng tengggg wkwkwkwk.")
    else:
        st.write(f"✨ {random.choice(GOMBAL_LUCU)}")

# ====== SYUKUR PROMPT ======
st.markdown('<div class="card"><b>Satu hal kecil</b><div class="hr"></div></div>', unsafe_allow_html=True)
if st.button("Pertanyaan", use_container_width=True):
    st.info(random.choice(SYUKUR_PROMPTS))

# ====== PLAYLIST (dropdown + embed) ======
st.markdown('<div class="card"><b>Playlist tenang</b><div class="hr"></div></div>', unsafe_allow_html=True)

pick = st.selectbox("Pilih playlist:", [f"Playlist {i}" for i in range(1, len(PLAYLISTS) + 1)])
selected_url = PLAYLISTS[int(pick.split()[-1]) - 1]
vid_id = extract_youtube_id(selected_url)

if vid_id:
    components.iframe(
        src=f"https://www.youtube.com/embed/{vid_id}?rel=0&modestbranding=1",
        height=260
    )
else:
    st.info("Playlist-nya nggak kebaca buat embed, tapi harusnya tetap bisa dibuka dari link aslinya.")

# ====== GROUNDING + NAPAS ======
st.markdown('<div class="card"><b>Biar lebih tenang</b><div class="hr"></div></div>', unsafe_allow_html=True)

tab_napas, tab_ground = st.tabs(["🫁 Napas", "🧠 Grounding"])

with tab_napas:
    st.markdown(
        '<div class="card"><b>Napas 4–2–6</b>'
        '<div class="hr"></div><div class="muted">tarik 4 • tahan 2 • hembus 6</div></div>',
        unsafe_allow_html=True
    )
    dur = st.select_slider("Durasi", options=[30, 60, 90, 120], value=60)

    if st.button("Mulai", use_container_width=True):
        st.info("Pelan-pelan ya. Kalau pusing, berhenti dulu gapapa.")
        prog = st.progress(0)
        status = st.empty()

        pattern = [("Tarik napas", 4), ("Tahan", 2), ("Hembus", 6)]
        t = 0
        while t < int(dur):
            for fase, sec in pattern:
                for _ in range(sec):
                    t += 1
                    if t > int(dur):
                        break
                    status.success(f"{fase} • {t}/{int(dur)} detik")
                    prog.progress(int(t / int(dur) * 100))
                    time.sleep(1)
                if t > int(dur):
                    break

        status.success("Selesai. Bagus.")
        st.balloons()

with tab_ground:
    g = st.radio("", ["5–4–3–2–1", "Tangan di dada", "Minum air pelan-pelan"], label_visibility="collapsed")
    if st.button("Tampilin caranya", use_container_width=True):
        if g == "5–4–3–2–1":
            st.warning(GROUNDING[0])
        elif g == "Tangan di dada":
            st.warning(GROUNDING[1])
        else:
            st.warning(GROUNDING[2])

st.caption("akal akalan teknik ")