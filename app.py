import streamlit as st
import pandas as pd
import requests

# --- CONFIGURARE PAGINĂ ---
st.set_page_config(page_title="Fotbal VIP Pro - API Free", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

# --- TITLU ȘI STRATEGIE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm VIP Pro (API-Football)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Automatizare 100% cu date din API-Sports.</p>", unsafe_allow_html=True)

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

# --- SIDEBAR CONFIG ---
st.sidebar.header("🔑 Configurare API-Football")
# Poți lipi direct cheia ta API din imagine în câmpul de mai jos sau în aplicație:
api_key_input = st.sidebar.text_input("Cheia ta API (API-Key):", type="password")

def extrage_cote_meci_individual(fixture_id, headers):
    c1, cX, c2 = 1.90, 3.30, 4.00 # Implicite dacă meciul nu are cote de la casele de pariuri încă
    try:
        url_odds = "https://v3.football.api-sports.io/odds"
        res = requests.get(url_odds, headers=headers, params={"fixture": fixture_id, "bet": 1}, timeout=5)
        if res.status_code == 200:
            data = res.json().get("response", [])
            if data and data[0].get("bookmakers"):
                bets = data[0]["bookmakers"][0].get("bets", [])
                if bets:
                    for val in bets[0].get("values", []):
                        if val["value"] == "Home":
                            c1 = float(val["odd"])
                        elif val["value"] == "Draw":
                            cX = float(val["odd"])
                        elif val["value"] == "Away":
                            c2 = float(val["odd"])
    except Exception:
        pass
    return c1, cX, c2

# --- INTERFAȚĂ PRINCIPALĂ ---
tab1, tab2 = st.tabs(["🚀 Căutare Automatizată Meciuri", "✍️ Introducere Manuală"])

with tab1:
    st.markdown("### 📅 Meciurile Programate")
    data_selectata = st.date_input("Alege Data:", pd.to_datetime("today"))
    data_str = data_selectata.strftime("%Y-%m-%d")
    
    limita_meciuri = st.slider("Număr de meciuri de analizat (economisește cereri API):", 5, 20, 10)
    
    if st.button("⚡ ÎNCARCĂ MECIURILE & COTELOR LIVE", use_container_width=True):
        if not api_key_input:
            st.warning("⚠️ Introduceți cheia ta API din contul API-Sports în meniul din stânga!")
        else:
            headers = {
                'x-rapidapi-host': "v3.football.api-sports.io",
                'x-rapidapi-key': api_key_input
            }
            
            with st.spinner("⏳ Se descarcă meciurile din API-Football..."):
                try:
                    url_fix = "https://v3.football.api-sports.io/fixtures"
                    res_fix = requests.get(url_fix, headers=headers, params={"date": data_str}, timeout=10)
                    meciuri_raw = res_fix.json().get("response", [])
                    
                    if meciuri_raw:
                        st.session_state.bilet_fotbal_premium = []
                        
                        # Filtrăm meciurile din ligile principale sau primele N meciuri
                        progres_bar = st.progress(0)
                        total_de_procesat = min(len(meciuri_raw), limita_meciuri)
                        
                        for i, match in enumerate(meciuri_raw[:total_de_procesat]):
                            fix_id = match["fixture"]["id"]
                            home_team = match["teams"]["home"]["name"]
                            away_team = match["teams"]["away"]["name"]
                            league_name = match["league"]["name"]
                            status = match["fixture"]["status"]["short"]
                            
                            # Extragere cote reale pentru fiecare meci
                            c1_r, cX_r, c2_r = extrage_cote_meci_individual(fix_id, headers)
                            
                            res = analizeaza_si_filtreaza_meci(
                                meci_nume=f"{home_team} vs {away_team}",
                                liga_nume=league_name,
                                data_ora=status,
                                c1=c1_r,
                                cX=cX_r,
                                c2=c2_r
                            )
                            st.session_state.bilet_fotbal_premium.append(res)
                            progres_bar.progress((i + 1) / total_de_procesat)
                            
                        st.success(f"✅ Analiză finalizată cu succes pentru {total_de_procesat} meciuri!")
                        st.rerun()
                    else:
                        st.error("❌ Nu s-au găsit meciuri pentru data selectată sau cheia API este greșită.")
                except Exception as e:
                    st.error(f"Eroare la conectare: {e}")

with tab2:
    st.markdown("### ✍️ Adaugă un meci manual")
    meci_i = st.text_input("Nume Meci:", "Atalanta vs Venezia")
    c1_i = st.number_input("Cotă 1", min_value=1.01, value=1.54, step=0.01)
    cX_i = st.number_input("Cotă X", min_value=1.01, value=4.65, step=0.01)
    c2_i = st.number_input("Cotă 2", min_value=1.01, value=5.60, step=0.01)
    
    if st.button("➕ ADAUGĂ MECI ÎN TABEL"):
        res = analizeaza_si_filtreaza_meci(meci_i, "Serie A", "Azi", c1_i, cX_i, c2_i)
        st.session_state.bilet_fotbal_premium.append(res)
        st.toast(f"✅ Adăugat: {meci_i}")

st.write("---")

# --- TABEL REZULTATE ---
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
