import streamlit as st
import pandas as pd
import io
import re

# Configurare pagină
st.set_page_config(page_title="Verificator & Creator Bilet", layout="wide", page_icon="🎫")

st.markdown("<h1 style='text-align: center;'>🎫 Verificator & Builder Bilet Manual</h1>", unsafe_allow_html=True)
st.write("---")

# Inițializare listă meciuri în session state
if "meciuri_manuale" not in st.session_state:
    st.session_state.meciuri_manuale = []

if "rezultat_calcul" not in st.session_state:
    st.session_state.rezultat_calcul = []

# --- PASUL 1: INTRODUCERE MANUALĂ MECIURI ---
st.markdown("### ✍️ Pasul 1: Adaugă meciurile manual")

tab1, tab2 = st.tabs(["➕ Adăugare Meci cu Meci", "📝 Adăugare Rapidă (Text / Copy-Paste)"])

with tab1:
    col_e1, col_e2, col_prono, col_cota = st.columns([2, 2, 2, 1])
    with col_e1:
        gazda = st.text_input("Echipă Gazdă:", key="gazda_input")
    with col_e2:
        oaspete = st.text_input("Echipă Oaspete:", key="oaspete_input")
    with col_prono:
        pronostic = st.text_input("Pronostic (ex: 2-5, GG, 1):", key="prono_input")
    with col_cota:
        cota_val = st.number_input("Cotă:", min_value=1.01, value=1.35, step=0.01, key="cota_input")

    if st.button("➕ Adaugă Meci pe Bilet", use_container_width=True):
        if gazda and oaspete and pronostic:
            st.session_state.meciuri_manuale.append({
                "Meci": f"{gazda.strip()} - {oaspete.strip()}",
                "Pronostic": pronostic.strip(),
                "Cotă": float(cota_val)
            })
            st.success(f"Adăugat: {gazda} - {oaspete} | {pronostic} | {cota_val}")
        else:
            st.warning("Te rugăm să completezi toate câmpurile pentru meci!")

with tab2:
    text_paste = st.text_area(
        "Introdu meciurile câte unul pe linie în formatul: Echipe | Pronostic | Cotă",
        placeholder="LASK Linz - Liverpool | 2-5 | 1.34\nFeyenoord Rotterdam - Como | 2-5 | 1.34",
        height=150
    )
    if st.button("📥 Incarcă Meciurile din Text", use_container_width=True):
        linii = text_paste.strip().split("\n")
        meciuri_parsate = []
        for l in linii:
            parti = [p.strip() for p in l.split('|') if p.strip()]
            if len(parti) >= 3:
                try:
                    c = float(parti[2].replace(',', '.'))
                except ValueError:
                    c = 1.35
                meciuri_parsate.append({
                    "Meci": parti[0],
                    "Pronostic": parti[1],
                    "Cotă": c
                })
        if meciuri_parsate:
            st.session_state.meciuri_manuale.extend(meciuri_parsate)
            st.success(f"Am adăugat {len(meciuri_parsate)} meciuri din text!")

# --- AFIȘARE MECIURI SALVATE ÎN LISTĂ ---
if st.session_state.meciuri_manuale:
    st.write("---")
    st.markdown("### 📋 Meciurile Selectate:")
    df_lista = pd.DataFrame(st.session_state.meciuri_manuale)
    st.dataframe(df_lista, use_container_width=True)
    
    col_del, col_miza = st.columns([1, 2])
    with col_del:
        if st.button("🗑️ Șterge Toate Meciurile"):
            st.session_state.meciuri_manuale = []
            st.session_state.rezultat_calcul = []
            st.rerun()
    with col_miza:
        miza = st.number_input("💰 Miza Biletului (RON):", min_value=1.0, value=5.00, step=0.50)

    # --- PASUL 2: VERIFICARE ȘI CALCUL ---
    st.write("---")
    if st.button("⚡ VERIFICĂ ȘI ANALIZEAZĂ BILETUL", use_container_width=True):
        rezultate = []
        for item in st.session_state.meciuri_manuale:
            cota = item["Cotă"]
            prob_reala = int((1 / cota) * 100 * 0.95)
            prob_reala = max(1, min(99, prob_reala))
            risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
            
            rezultate.append({
                "Meci / Eveniment": item["Meci"],
                "Pronostic": item["Pronostic"],
                "Cotă": cota,
                "Probabilitate": f"{prob_reala}%",
                "Nivel Risc": risc,
                "prob_num": prob_reala
            })
        st.session_state.rezultat_calcul = rezultate

# --- PASUL 3: AFIȘARE METRICI ȘI BUTON PLASARE BILET ---
if st.session_state.rezultat_calcul:
    st.markdown("### 📊 Rezultate Analiză:")
    df_res = pd.DataFrame(st.session_state.rezultat_calcul)
    st.dataframe(df_res.drop(columns=["prob_num"]), use_container_width=True)
    
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.rezultat_calcul:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
        
    # --- PASUL 4: PLASARE / IMPORT PE SUPERBET ---
    st.write("---")
    st.markdown("### 🚀 Pasul 3: Deschide/Plasează Biletul pe Superbet")
    
    cod_bilet = st.text_input("Introdu sau generază codul de bilet Superbet (ex: 8910-YYHUV7):", value="8910-YYHUV7")
    
    if cod_bilet:
        cod_clean = cod_bilet.strip().upper()
        url_superbet = f"https://superbet.ro/pariurile-mele/deschise?code={cod_clean}"
        
        st.markdown(
            f'''
            <a href="{url_superbet}" target="_blank" style="text-decoration: none;">
                <button style="
                    background-color: #E50914;
                    color: white;
                    padding: 16px 24px;
                    border: none;
                    border-radius: 8px;
                    font-size: 18px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;">
                    🔴 ÎNCARCĂ ȘI PLASEAZĂ BILETUL ({cod_clean}) PE SUPERBET
                </button>
            </a>
            ''',
            unsafe_allow_html=True
        )
