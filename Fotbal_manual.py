import streamlit as st

# Configurare pagină optimizată special pentru ecranele de mobil
st.set_page_config(page_title="Calculator Fotbal VIP", layout="wide", page_icon="⚽")

st.title("⚽ Algoritm Fotbal VIP")
st.write("Modifică cotele și vezi instant pronosticurile, direct pe telefon.")

st.write("---")

# --- INTRODUCERE DATE DIRECTĂ (FĂRĂ BUTON BLOCK) ---
meci_nume = st.text_input("Nume Meci (ex: FCSB vs Rapid):", "FCSB vs Rapid")
liga_nume = st.text_input("Competiție / Ligă (ex: Superliga):", "Superliga")

st.write("### 📉 Introduceți Cotele:")
col1, col2, col3 = st.columns(3)
with col1:
    c1 = st.number_input("Cotă 1 (Gazde)", min_value=1.01, value=1.50, step=0.01, format="%.2f")
with col2:
    cX = st.number_input("Cotă X (Egal)", min_value=1.01, value=3.80, step=0.01, format="%.2f")
with col3:
    c2 = st.number_input("Cotă 2 (Oaspeți)", min_value=1.01, value=5.50, step=0.01, format="%.2f")
    
st.write("---")

# --- REZULTATELE SE AFIȘEAZĂ INSTANT AICI ---
st.markdown(f"### 📊 Rezultat Analiză Live: **{meci_nume}** ({liga_nume})")

# Algoritmul matematic de filtrare pe baza Cotei 1
if c1 <= 1.65:
    st.success("🟩 **VERDICT: FAVORIT CLAR**")
    st.info("🛡️ **Varianta Safe (Siguranță):**\n\n👉 **Șansă dublă 1X** (Asigurat în caz de egalitate)")
    st.warning("⚡ **Varianta Medium (Recomandată):**\n\n👉 **⚽ Gol în Prima Repriză (Peste 0.5 goluri în 1R)**")
    st.error("🔥 **Varianta Risk (Cotă Mare):**\n\n👉 **1 Solist & Peste 2.5 Goluri în meci**")
    
elif 1.65 < c1 <= 2.30:
    st.success("🟨 **VERDICT: MECI ECHILIBRAT**")
    st.info("🛡️ **Varianta Safe (Siguranță):**\n\n👉 **Interval Goluri 1-4 în tot meciul**")
    st.warning("⚡ **Varianta Medium (Recomandată):**\n\n👉 **⚽ Gol în Prima Repriză (Peste 0.5 în 1R) SAU Ambele marchează (GG)**")
    st.error("🔥 **Varianta Risk (Cotă Mare):**\n\n👉 **X final (Egalitate la sfârșitul celor 90 de minute)**")
    
else:
    st.success("🟥 **VERDICT: OUTSIDER / HAZARD**")
    st.info("🛡️ **Varianta Safe (Siguranță):**\n\n👉 **Peste 1.5 Goluri în tot meciul**")
    st.warning("⚡ **Varianta Medium (Recomandată):**\n\n👉 **Șansă dublă X2** (Oaspeții nu pierd meciul)")
    st.error("🔥 **Varianta Risk (Cotă Mare):**\n\n👉 **2 Solist** (Victorie curată a echipei oaspete)")