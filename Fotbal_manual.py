import streamlit as st
import pandas as pd
import io

# Configurare specială pentru ecrane de mobil
st.set_page_config(page_title="Fotbal VIP + Excel", layout="wide", page_icon="⚽")

st.title("⚽ Algoritm Fotbal VIP + Export Excel")
st.write("Introdu meciurile rând pe rând de pe telefon. Acestea se vor salva în lista de mai jos, de unde poți descărca registrul Excel.")

st.write("---")

# Inițializăm lista de meciuri în memoria Streamlit dacă nu există deja
if "lista_meciuri" not in st.session_state:
    st.session_state.lista_meciuri = []

# --- SECȚIUNE ADĂUGARE MECI ---
st.subheader("➕ Adaugă un meci nou")

meci_nume = st.text_input("Nume Meci (ex: FCSB vs Rapid):", "FCSB vs Rapid")
liga_nume = st.text_input("Competiție / Ligă (ex: Superliga):", "Superliga")

col1, col2, col3 = st.columns(3)
with col1:
    c1 = st.number_input("Cotă 1 (Gazde)", min_value=1.01, value=1.50, step=0.01, format="%.2f")
with col2:
    cX = st.number_input("Cotă X (Egal)", min_value=1.01, value=3.80, step=0.01, format="%.2f")
with col3:
    c2 = st.number_input("Cotă 2 (Oaspeți)", min_value=1.01, value=5.50, step=0.01, format="%.2f")

# Buton mare pe mobil pentru a salva meciul în tabel
if st.button("📥 SALVEAZĂ MECIUL ÎN LISTĂ", use_container_width=True):
    # Aplicăm algoritmul pe loc pentru a salva verdictele direct în tabel
    if c1 <= 1.65:
        verdict = "🟩 FAVORIT CLAR"
        safe = "Șansă dublă 1X"
        medium = "⚽ Gol în Prima Repriză (Peste 0.5)"
        risk = "1 & Peste 2.5 Goluri"
    elif 1.65 < c1 <= 2.30:
        verdict = "🟨 MECI ECHILIBRAT"
        safe = "Interval Goluri 1-4"
        medium = "⚽ Gol în 1R SAU Ambele marchează (GG)"
        risk = "X final (Egalitate)"
    else:
        verdict = "🟥 OUTSIDER / HAZARD"
        safe = "Peste 1.5 Goluri"
        medium = "Șansă dublă X2"
        risk = "2 Solist"

    # Adăugăm datele în starea aplicației
    st.session_state.lista_meciuri.append({
        "Meci": meci_nume,
        "Ligă": liga_nume,
        "Cota 1": f"{c1:.2f}",
        "Cota X": f"{cX:.2f}",
        "Cota 2": f"{c2:.2f}",
        "Verdict Risc": verdict,
        "🛡️ Varianta Safe": safe,
        "⚡ Varianta Medium": medium,
        "🔥 Varianta Risk": risk
    })
    st.success(f"✅ Meciul '{meci_nume}' a fost adăugat jos în tabel!")

st.write("---")

# --- SECȚIUNE LISTĂ ȘI EXPORT ---
st.subheader("📊 Meciurile tale salvate")

if st.session_state.lista_meciuri:
    # Transformăm lista în DataFrame pentru afișare și export
    df = pd.DataFrame(st.session_state.lista_meciuri)
    
    # Afișăm tabelul pe ecranul mobilului
    st.dataframe(df, use_container_width=True)
    
    # Buton de ștergere istoric
    if st.button("🗑️ Șterge toate meciurile", use_container_width=False):
        st.session_state.lista_meciuri = []
        st.rerun()
        
    st.write("")
    
    # --- LOGICA DE GENERARE FIȘIER EXCEL DIRECT PE MOBIL ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Predictii VIP')
        
    # Pregătim datele binare pentru descărcare
    date_excel = buffer.getvalue()
    
    # Butonul magic de download Excel (apare colorat și mare pe telefon)
    st.download_button(
        label="🟢 DESCARCĂ FIȘIERUL EXCEL (.xlsx)",
        data=date_excel,
        file_name="Predictii_Fotbal_VIP.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
else:
    st.info("Nu ai adăugat niciun meci încă. Completează cotele de sus și apasă pe butonul de salvare.")