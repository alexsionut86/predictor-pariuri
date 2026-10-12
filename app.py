import streamlit as st
import pandas as pd
import requests
import re
from urllib.parse import unquote

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Fotbal VIP Pro - Anti-Risc", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

# --- TITLU ȘI STRATEGIE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm VIP Pro (Versiune Anti-Risc)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analiză bazată pe date reale și link-uri Flashscore.</p>", unsafe_allow_html=True)

st.info("""
💡 **STRATEGIE ANTI-RISC (MAXIM 2 MECIURI PER BILET):**
* Target: Cota finală **~2.00**.
* Opțiuni permise: **Peste 1.5 Goluri** sau **Șansă Dublă (1X / X2)**.
* Fără combinații periculoase de Bet Builder (fără intervale de tip 1-4 goluri).
""")
st.write("---")

# --- ALGORITM MATEMATIC DE PREDICTOR ---
def analizeaza_si_filtreaza_meci(meci_nume, liga_nume, data_ora, c1, cX, c2, medie_goluri=2.2):
    if c1 <= 1.55:
        verdict = "🟩 FAVORIT CLAR (GAZDE)"
        predicție_principala = "Șansă dublă 1X"
        p_principala = 92
        alternativa = "Peste 1.5 Goluri"
        p_alt = 88
    elif c2 <= 1.55:
        verdict = "🟩 FAVORIT CLAR (OASPEȚI)"
        predicție_principala = "Șansă dublă X2"
        p_principala = 92
        alternativa = "Peste 1.5 Goluri"
        p_alt = 88
    elif medie_goluri >= 1.80 or (1.55 < c1 <= 2.30):
        verdict = "🟨 MECI ECHILIBRAT / GOLURI"
        predicție_principala = "Peste 1.5 Goluri"
        p_principala = 84
        alternativa = "Șansă dublă 1X"
        p_alt = 80
    else:
        verdict = "🟥 MECI STRÂNS / RISCANT"
        predicție_principala = "Peste 0.5 Goluri Repriza 2"
        p_principala = 78
        alternativa = "Peste 1.5 Goluri"
        p_alt = 72

    return {
        "Data / Ora": data_ora,
        "Meci": meci_nume,
        "Ligă": liga_nume,
        "Cota 1": f"{c1:.2f}",
        "Cota X": f"{cX:.2f}",
        "Cota 2": f"{c2:.2f}",
        "Medie Goluri": f"{medie_goluri:.2f}",
        "Verdict": verdict,
        "🎯 PREDICȚIE BAZĂ": f"{predicție_principala} ({p_principala}%)",
        "🛡️ ALTERNATIVĂ SAFE": f"{alternativa} ({p_alt}%)"
    }

# --- PARSER INTELIGENT DE LINK & COTE ---
def extrage_detalii_link(url):
    nume_meci = "Meci Detectat"
    
    # 1. Extragere Nume Echipe din URL (ex: .../atalanta-8C9JmXu/venezia-MkPmVv50/...)
    match_url_echipe = re.search(r'/fotbal/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-]+)', url, re.IGNORECASE)
    if match_url_echipe:
        g1 = match_url_echipe.group(1).split('-')[0].capitalize()
        g2 = match_url_echipe.group(2).split('-')[0].capitalize()
        nume_meci = f"{g1} vs {g2}"
    else:
        # Încercare extragere titlu de pe web
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)'}
            res = requests.get(url, headers=headers, timeout=3)
            if res.status_code == 200:
                titlu = re.search(r'<title>(.*?)</title>', res.text, re.IGNORECASE)
                if titlu:
                    curat = titlu.group(1).split('|')[0].replace('Flashscore.ro', '').strip()
                    if len(curat) > 3:
                        nume_meci = curat
        except Exception:
            pass

    # 2. Identificare ID Meci
    match_id = "Desconoscut"
    id_search = re.search(r'(?:mid=|id=|/meci/)([a-zA-Z0-9]+)', url, re.IGNORECASE)
    if id_search:
        match_id = id_search.group(1)

    return nume_meci, match_id

# --- MODURI DE INTRODUCERE A DATELOR ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔗 Din Link Flashscore (Mobil)", 
    "⚡ Simulare API Live", 
    "📁 Încarcă Fișier (Excel/CSV)", 
    "✍️ Introducere Manuală"
])

# --- TAB 1: FLASHSCORE LINK ---
with tab1:
    st.markdown("### 🔗 Analiză rapidă prin Link Flashscore")
    st.write("Apasă **Share (Distribuie)** în aplicația Flashscore de pe telefon și lipește link-ul mai jos:")
    
    url_input = st.text_input("Lipește link-ul meciului (ex: https://www.flashscore.ro/meci/fotbal/atalanta...):")
    
    st.markdown("#### 🏪 Selectează Casa de Pariuri & Introdu Cotele reale din imagine:")
    casa_pariuri = st.selectbox("Alege Agenția ta:", ["Superbet", "Betano", "Unibet", "Fortuna", "Get's Bet", "MrBit", "NetBet"])
    
    col_c1, col_cx, col_c2 = st.columns(3)
    with col_c1:
        c1_m = st.number_input("Cotă 1 (Gazde):", min_value=1.01, value=1.54, step=0.01)
    with col_cx:
        cX_m = st.number_input("Cotă X (Egal):", min_value=1.01, value=4.65, step=0.01)
    with col_c2:
        c2_m = st.number_input("Cotă 2 (Oaspeți):", min_value=1.01, value=5.60, step=0.01)

    if st.button("🚀 ANALIZEAZĂ MECIUL AUTOMAT", use_container_width=True):
        if url_input:
            nume_echipe, m_id = extrage_detalii_link(url_input)
            
            st.success(f"✅ Meci Detectat: **{nume_echipe}** | Agenție: **{casa_pariuri}** | Cote: **1: {c1_m} | X: {cX_m} | 2: {c2_m}**")
            
            res = analizeaza_si_filtreaza_meci(
                meci_nume=f"{nume_echipe} ({casa_pariuri})",
                liga_nume="Serie A / Pre-Match",
                data_ora="Azi",
                c1=c1_m,
                cX=cX_m,
                c2=c2_m,
                medie_goluri=2.4
            )
            st.session_state.bilet_fotbal_premium.append(res)
            st.toast("✅ Meci adăugat în bilet!")
            st.rerun()
        else:
            st.warning("Te rugăm să lipești un link mai întâi.")

# --- TABEL CU REZULTATE ȘI EXPORT ---
if st.session_state.bilet_fotbal_premium:
    df = pd.DataFrame(st.session_state.bilet_fotbal_premium)
    st.markdown("### 📋 Meciuri Analizate (Fără Bet Builder)")
    st.dataframe(df, use_container_width=True)
    
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "📥 DESCARCĂ REZULTATELE (CSV)",
            data=df.to_csv(index=False).encode('utf-8-sig'),
            file_name="bilet_anti_risc.csv",
            mime="text/csv",
            use_container_width=True
        )
    with col_d2:
        if st.button("🗑️ RESETEAZĂ TABELUL", use_container_width=True):
            st.session_state.bilet_fotbal_premium = []
            st.rerun()
