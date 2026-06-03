import streamlit as st
import pandas as pd
import io

# Configurare pagină optimizată pentru mobil
st.set_page_config(page_title="Fotbal VIP Pro", layout="wide", page_icon="⚽")

# --- TITLU ȘI INTRODUCERE ---
st.markdown("<h1 style='text-align: center;'>⚽ Algoritm Fotbal VIP Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analiză completă: Goluri, Cornere și Cartonașe cu procente.</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state.bilet_fotbal_premium = []

# --- INTRODUCERE DATE ---
st.markdown("### ➕ Date Meci")
meci_nume = st.text_input("Nume Meci:", "FCSB vs Rapid")
liga_nume = st.text_input("Competiție / Ligă:", "Superliga")

st.markdown("### 📉 Cote 1X2:")
col1, col2, col3 = st.columns(3)
with col1:
    c1 = st.number_input("Cotă 1", min_value=1.01, value=1.50, step=0.01, format="%.2f")
with col2:
    cX = st.number_input("Cotă X", min_value=1.01, value=3.80, step=0.01, format="%.2f")
with col3:
    c2 = st.number_input("Cotă 2", min_value=1.01, value=5.50, step=0.01, format="%.2f")

st.write("---")

# --- ALGORITM ȘI LOGICĂ PROCENTE (GOLURI + CORNERE + CARTONAȘE) ---
probabilitate_baza = int((1 / c1) * 100) if c1 > 0 else 0

if c1 <= 1.65:
    verdict_text = "FAVORIT CLAR"
    verdict_emoji = "🟩"
    
    # GOLURI
    safe = "Șansă dublă 1X"
    medium = "⚽ Gol în Prima Repriză (Peste 0.5 1R)"
    risk = "1 Solist & Peste 2.5 Goluri"
    p_safe, p_medium, p_risk = min(92, probabilitate_baza + 25), min(85, probabilitate_baza + 15), max(45, probabilitate_baza - 15)
    
    # CORNERE ȘI CARTONAȘE
    cornere_text = f"🚩 Peste 5.5 Cornere echipa gazdă (Presiune continuă) — {min(88, probabilitate_baza + 20)}% șanse"
    cartonase_text = f"🟨 Cele mai multe cartonașe: Oaspeții (Faulturi din frustrare) — {min(82, probabilitate_baza + 15)}% șanse"

elif 1.65 < c1 <= 2.30:
    verdict_text = "MECI ECHILIBRAT"
    verdict_emoji = "🟨"
    
    # GOLURI
    safe = "Interval Goluri 1-4"
    medium = "⚽ Gol în 1R SAU Ambele marchează (GG)"
    risk = "X final (Egalitate)"
    p_safe, p_medium, p_risk = 82, 74, (int((1 / cX) * 100) if cX > 0 else 30)
    
    # CORNERE ȘI CARTONAȘE
    cornere_text = "🚩 Peste 8.5 Cornere în total meci (Luptă deschisă) — 76% șanse"
    cartonase_text = "🟨 Peste 4.5 Cartonașe în meci (Tensiune mare / Derby) — 84% șanse"

else:
    verdict_text = "OUTSIDER / HAZARD"
    verdict_emoji = "🟥"
    
    # GOLURI
    safe = "Peste 1.5 Goluri"
    medium = "Șansă dublă X2"
    risk = "2 Solist"
    p_safe, p_medium, p_risk = 85, (int((1 / c2) * 100) + 20 if c2 > 0 else 65), (int((1 / c2) * 100) if c2 > 0 else 20)
    
    # CORNERE ȘI CARTONAȘE
    cornere_text = "🚩 Peste 3.5 Cornere în total (Meci slab pe aripi) — 70% șanse"
    cartonase_text = "🟨 Gazdele primesc primul cartonaș în meci — 78% șanse"

# Asigurare limite procente
p_safe, p_medium, p_risk = max(1, min(99, p_safe)), max(1, min(99, p_medium)), max(1, min(99, p_risk))

# --- AFIȘARE DESIGN EXTRA-PROFILAT ---
st.markdown("<h3 style='text-align: center;'>📊 Predicții Găsite</h3>", unsafe_allow_html=True)
st.markdown(f"<h4 style='text-align: center;'>Verdict: {verdict_emoji} {verdict_text}</h4>", unsafe_allow_html=True)
st.write("")

# 1. Casetele Standard de Goluri (Stilul tău favorit)
st.info(f"🛡️ **Varianta Safe (Siguranță) — {p_safe}% șanse:**\n\n👉 {safe}")
st.warning(f"⚡ **Varianta Medium (Recomandată) — {p_medium}% șanse:**\n\n👉 {medium}")
st.error(f"🔥 **Varianta Risk (Cotă Mare) — {p_risk}% șanse:**\n\n👉 {risk}")

# 2. Caseta specială pentru Speciale (Maro/Gri închis administrativ)
st.write("")
st.markdown("#### 🎯 Opțiuni Speciale:")
st.markdown(f"""
> {cornere_text}  
>   
> {cartonase_text}
""")

st.write("")

# --- BUTON SALVARE ---
if st.button("📥 SALVEAZĂ TOTUL ÎN EXCEL", use_container_width=True):
    st.session_state.bilet_fotbal_premium.append({
        "Meci": meci_nume,
        "Ligă": liga_nume,
        "Cota 1": f"{c1:.2f}",
        "Cota X": f"{cX:.2f}",
        "Cota 2": f"{c2:.2f}",
        "Verdict": verdict_text,
        "🛡️ Safe": f"{safe} ({p_safe}%)",
        "⚡ Medium": f"{medium} ({p_medium}%)",
        "🔥 Risk": f"{risk} ({p_risk}%)",
        "🚩 Cornere": cornere_text.split("—")[0].strip(),
        "🟨 Cartonașe": cartonase_text.split("—")[0].strip()
    })
    st.toast(f"✅ Salvat complet: {meci_nume}")

st.write("---")

# --- TABEL EXCEL ---
if st.session_state.bilet_fotbal_premium:
    st.markdown("### 📋 Istoric Tabel")
    df = pd.DataFrame(st.session_state.bilet_fotbal_premium)
    st.dataframe(df, use_container_width=True)
    
    if st.button("🗑️ Resetează", use_container_width=False):
        st.session_state.bilet_fotbal_premium = []
        st.rerun()
        
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Fotbal VIP Complet')
    date_excel = buffer.getvalue()
    
    st.download_button(
        label="🟢 DESCARCĂ EXCEL COMPLET (.xlsx)",
        data=date_excel,
        file_name="Bilet_Fotbal_Premium.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
