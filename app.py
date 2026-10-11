import streamlit as st
import pandas as pd
import requests
import re

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

# --- MODURI DE INTRODUCERE A DATELOR ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🔗 Din Link Flashscore (Mobil)", 
    "⚡ Simulare API Live", 
    "📁 Încarcă Fișier (Excel/CSV)", 
    "✍️ Introducere Manuală"
])

# --- TAB 1: FLASHSCORE LINK (CU EXTRAGERE AUTOMATĂ DE NUME) ---
with tab1:
    st.markdown("### 🔗 Analiză rapidă prin Link Flashscore")
    st.write("Apasă **Share (Distribuie)** în aplicația Flashscore de pe telefon și lipește link-ul mai jos:")
    
    url_input = st.text_input("Lipește link-ul meciului (ex: https://www.flashscore.ro/r/?t=1&id=... sau /meci/...):")
    nume_manual = st.text_input("Nume Meci (Opțional - scrie doar dacă dorești să modifici numele):", "")
    
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        c1_link = st.number_input("Cotă 1 (Gazde):", min_value=1.01, value=1.90, step=0.01)
    with col_l2:
        c2_link = st.number_input("Cotă 2 (Oaspeți):", min_value=1.01, value=4.00, step=0.01)

    if st.button("🚀 ANALIZEAZĂ MECIUL DIN LINK", use_container_width=True):
        if url_input:
            match_id_search = re.search(r'(?:/meci/|id=)([a-zA-Z0-9]+)', url_input, re.IGNORECASE)
            
            if match_id_search:
                match_id = match_id_search.group(1)
                nume_meci_final = nume_manual if nume_manual else f"Meci Flashscore ({match_id})"
                
                # Încercăm extragerea automată a titlului din pagina web
                if not nume_manual:
                    try:
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                        req = requests.get(url_input, headers=headers, timeout=3)
                        if req.status_code == 200:
                            titlu_search = re.search(r'<title>(.*?)</title>', req.text, re.IGNORECASE)
                            if titlu_search:
                                raw_titlu = titlu_search.group(1)
                                titlu_curat = raw_titlu.split('|')[0].split('- Flashscore')[0].replace('Flashscore.ro', '').strip()
                                if titlu_curat:
                                    nume_meci_final = titlu_curat
                    except Exception:
                        pass
                
                st.success(f"✅ Meci identificat: **{nume_meci_final}**")
                
                res = analizeaza_si_filtreaza_meci(
                    meci_nume=nume_meci_final,
                    liga_nume="Analiză Live",
                    data_ora="Azi",
                    c1=c1_link,
                    cX=3.30,
                    c2=c2_link,
                    medie_goluri=2.1
                )
                st.session_state.bilet_fotbal_premium.append(res)
                st.toast("✅ Meci adăugat în tabel!")
                st.rerun()
            else:
                st.error("❌ Link invalid. Asigură-te că link-ul conține un ID de meci din Flashscore.")
        else:
            st.warning("Te rugăm să lipești un link mai întâi.")

# --- TAB 2: SIMULARE API LIVE ---
with tab2:
    st.markdown("### 🤖 Preluare Automată a Meciurilor")
    if st.button("🚀 EXTRAGE AUTOMAT MECIURILE ZILEI", use_container_width=True):
        meciuri_demo = [
            {"meci": "Farul Constanța vs Petrolul Ploiești", "liga": "Superliga România", "ora": "Azi 21:00", "c1": 1.90, "cX": 3.30, "c2": 4.20},
            {"meci": "Real Madrid vs Getafe", "liga": "La Liga", "ora": "Azi 22:00", "c1": 1.25, "cX": 6.00, "c2": 11.00}
        ]
        st.session_state.bilet_fotbal_premium = []
        for m in meciuri_demo:
            res = analizeaza_si_filtreaza_meci(m["meci"], m["liga"], m["ora"], m["c1"], m["cX"], m["c2"])
            st.session_state.bilet_fotbal_premium.append(res)
        st.success("✅ Meciuri adăugate!")

# --- TAB 3: ÎNCĂRCARE FIȘIER ---
with tab3:
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

# --- TAB 4: INTRODUCERE MANUALĂ ---
with tab4:
    st.markdown("### ✍️ Adaugă un meci manual")
    meci_i = st.text_input("Nume Meci:", "FCSB vs Rapid")
    c1_i = st.number_input("Cotă 1", min_value=1.01, value=1.90, step=0.01)
    cX_i = st.number_input("Cotă X", min_value=1.01, value=3.40, step=0.01)
    c2_i = st.number_input("Cotă 2", min_value=1.01, value=4.00, step=0.01)
    
    if st.button("➕ ADAUGĂ MECI ÎN TABEL"):
        res = analizeaza_si_filtreaza_meci(meci_i, "Superliga", "Azi", c1_i, cX_i, c2_i)
        st.session_state.bilet_fotbal_premium.append(res)
        st.toast(f"✅ Adăugat: {meci_i}")

st.write("---")

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
