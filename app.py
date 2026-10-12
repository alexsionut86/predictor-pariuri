import streamlit as st
import pandas as pd
import requests
import re

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Fotbal VIP Pro - Anti-Risc", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

# --- TITLU ȘI STRATEGIE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm VIP Pro (Versiune Anti-Risc Mobil)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analiză rapidă și sigură pentru mobil.</p>", unsafe_allow_html=True)

st.info("""
💡 **STRATEGIE ANTI-RISC (MAXIM 2 MECIURI PER BILET):**
* Target: Cota finală **~2.00**.
* Opțiuni permise: **Peste 1.5 Goluri** sau **Șansă Dublă (1X / X2)**.
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

# --- PARSER INTELIGENT DE LINK ---
def extrage_nume_meci(url):
    nume_meci = ""
    match_url_echipe = re.search(r'/fotbal/([a-zA-Z0-9\-]+)/([a-zA-Z0-9\-]+)', url, re.IGNORECASE)
    if match_url_echipe:
        g1 = match_url_echipe.group(1).split('-')[0].capitalize()
        g2 = match_url_echipe.group(2).split('-')[0].capitalize()
        nume_meci = f"{g1} vs {g2}"
    return nume_meci

# --- INTERFAȚĂ PRINCIPALĂ ---
tab1, tab2 = st.tabs(["🚀 Analiză Meci Rapidă", "📁 Încarcă Fișier (Excel/CSV)"])

with tab1:
    st.markdown("### ⚽ Introducere & Analiză Meci")
    
    url_input = st.text_input("🔗 Link Flashscore (Opțional - extrage numele meciului):")
    nume_manual = st.text_input("Nume Meci (dacă nu folosești link):", "Atalanta vs Venezia")
    
    st.markdown("#### 📊 Cotele 1X2 reale din agenția ta de pariuri:")
    col_c1, col_cx, col_c2 = st.columns(3)
    with col_c1:
        c1_m = st.number_input("Cotă 1 (Gazde):", min_value=1.01, value=1.54, step=0.01)
    with col_cx:
        cX_m = st.number_input("Cotă X (Egal):", min_value=1.01, value=4.65, step=0.01)
    with col_c2:
        c2_m = st.number_input("Cotă 2 (Oaspeți):", min_value=1.01, value=5.60, step=0.01)

    if st.button("🚀 ANALIZEAZĂ MECIUL", use_container_width=True):
        meci_final = nume_manual
        if url_input:
            nume_link = extrage_nume_meci(url_input)
            if nume_link:
                meci_final = nume_link
        
        res = analizeaza_si_filtreaza_meci(
            meci_nume=meci_final,
            liga_nume="Analiză Live",
            data_ora="Azi",
            c1=c1_m,
            cX=cX_m,
            c2=c2_m,
            medie_goluri=2.2
        )
        st.session_state.bilet_fotbal_premium.append(res)
        st.success(f"✅ Meci adăugat: **{meci_final}** | Recomandare: **{res['🎯 PREDICȚIE BAZĂ']}**")
        st.rerun()

with tab2:
    st.markdown("### 📁 Încarcă fișier CSV / Excel")
    uploaded_file = st.file_uploader("Alege fișierul Excel sau CSV", type=["xlsx", "csv"])
    if uploaded_file is not None:
        try:
            df_input = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            if st.button("⚙️ PROCESEAZĂ FIȘIERUL", use_container_width=True):
                st.session_state.bilet_fotbal_premium = []
                for _, row in df_input.iterrows():
                    res = analizeaza_si_filtreaza_meci(
                        str(row.get("Meci", "Meci")), str(row.get("Ligă", "Competiție")), str(row.get("Data / Ora", "Azi")),
                        float(str(row.get("Cota 1", 2.0)).replace(",", ".")), float(str(row.get("Cota X", 3.0)).replace(",", ".")), float(str(row.get("Cota 2", 3.0)).replace(",", "."))
                    )
                    st.session_state.bilet_fotbal_premium.append(res)
                st.success("✅ Fișier procesat cu succes!")
                st.rerun()
        except Exception as e:
            st.error(f"Eroare la procesare: {e}")

st.write("---")

# --- TABEL REZULTATE ȘI EXPORT ---
if st.session_state.bilet_fotbal_premium:
    df = pd.DataFrame(st.session_state.bilet_fotbal_premium)
    st.markdown("### 📋 Meciuri Analizate (Bilet Anti-Risc)")
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
