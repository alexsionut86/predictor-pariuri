import streamlit as st
import pandas as pd

st.set_page_config(page_title="Calculator Cota Corectă & Valoare", page_icon="⚖️", layout="wide")

st.title("⚖️ Calculator Medie Cote & Valoare Reală (Fair Odds)")
st.markdown("""
Acest calculator elimină **marja casei de pariuri (Overround-ul)** pentru a afla probabilitate reală 
și îți arată dacă o cotă oferită are valoare sau este subevaluată.
""")
st.write("---")

# Tab-uri pentru cele două piețe principale
tab_1x2, tab_gg = st.tabs(["⚽ Piața 1X2 (Rezultat Final)", "🥅 Piața GG / NG (Ambele Marchează)"])

# --- TAB 1: PIAȚA 1X2 ---
with tab_1x2:
    col_in1, col_in2, col_in3 = st.columns(3)
    with col_in1:
        c1 = st.number_input("Cotă 1 (Gazde):", min_value=1.01, value=1.65, step=0.01, key="c1_1x2")
    with col_in2:
        cX = st.number_input("Cotă X (Egal):", min_value=1.01, value=3.75, step=0.01, key="cx_1x2")
    with col_in3:
        c2 = st.number_input("Cotă 2 (Oaspeți):", min_value=1.01, value=5.25, step=0.01, key="c2_1x2")

    if st.button("🧮 CALCULEAZĂ PENTRU 1X2", use_container_width=True):
        p1_brut = (1 / c1) * 100
        pX_brut = (1 / cX) * 100
        p2_brut = (1 / c2) * 100
        
        suma_prob = p1_brut + pX_brut + p2_brut
        marja = suma_prob - 100
        
        p1_real = (p1_brut / suma_prob) * 100
        pX_real = (pX_brut / suma_prob) * 100
        p2_real = (p2_brut / suma_prob) * 100
        
        c1_fair = 100 / p1_real
        cX_fair = 100 / pX_real
        c2_fair = 100 / p2_real

        st.write("---")
        cm1, cm2 = st.columns(2)
        cm1.metric("Suma Probabilităților", f"{suma_prob:.2f}%")
        cm2.metric("Marja Casei de Pariuri", f"{marja:.2f}%")
        
        df_1x2 = pd.DataFrame({
            "Opțiune": ["1 (Gazde)", "X (Egal)", "2 (Oaspeți)"],
            "Cotă Afișată": [f"{c1:.2f}", f"{cX:.2f}", f"{c2:.2f}"],
            "Probabilitate Reală": [f"{p1_real:.2f}%", f"{pX_real:.2f}%", f"{p2_real:.2f}%"],
            "Cotă Corectă (Fără Marjă)": [f"{c1_fair:.2f}", f"{cX_fair:.2f}", f"{c2_fair:.2f}"],
            "Diferență / Valoare": [
                "🟩 Valoare" if c1 >= c1_fair else "🟥 Sub evaluată",
                "🟩 Valoare" if cX >= cX_fair else "🟥 Sub evaluată",
                "🟩 Valoare" if c2 >= c2_fair else "🟥 Sub evaluată"
            ]
        })
        st.dataframe(df_1x2, use_container_width=True)

# --- TAB 2: PIAȚA GG / NG ---
with tab_gg:
    st.markdown("### 🥅 Analiză Cota Ambele Marchează (GG vs NG)")
    
    col_gg1, col_gg2 = st.columns(2)
    with col_gg1:
        c_gg = st.number_input("Cotă GG (Ambele marchează - DA):", min_value=1.01, value=1.85, step=0.01, key="c_gg")
    with col_gg2:
        c_ng = st.number_input("Cotă NG (Nu marchează ambele - NU):", min_value=1.01, value=1.95, step=0.01, key="c_ng")

    if st.button("🧮 CALCULEAZĂ PENTRU GG / NG", use_container_width=True):
        # Calcul probabilități binar (2 opțiuni)
        p_gg_brut = (1 / c_gg) * 100
        p_ng_brut = (1 / c_ng) * 100
        
        suma_gg = p_gg_brut + p_ng_brut
        marja_gg = suma_gg - 100
        
        p_gg_real = (p_gg_brut / suma_gg) * 100
        p_ng_real = (p_ng_brut / suma_gg) * 100
        
        c_gg_fair = 100 / p_gg_real
        c_ng_fair = 100 / p_ng_real

        st.write("---")
        cg1, cg2 = st.columns(2)
        cg1.metric("Suma Probabilităților", f"{suma_gg:.2f}%")
        cg2.metric("Marja Casei pe GG/NG", f"{marja_gg:.2f}%")
        
        df_gg = pd.DataFrame({
            "Opțiune": ["GG (Ambele Marchează DA)", "NG (Nu Marchează Ambele)"],
            "Cotă Afișată": [f"{c_gg:.2f}", f"{c_ng:.2f}"],
            "Probabilitate Reală": [f"{p_gg_real:.2f}%", f"{p_ng_real:.2f}%"],
            "Cotă Corectă (Fără Marjă)": [f"{c_gg_fair:.2f}", f"{c_ng_fair:.2f}"],
            "Diferență / Valoare": [
                "🟩 Valoare" if c_gg >= c_gg_fair else "🟥 Sub evaluată",
                "🟩 Valoare" if c_ng >= c_ng_fair else "🟥 Sub evaluată"
            ]
        })
        st.dataframe(df_gg, use_container_width=True)

        st.info(f"""
        💡 **Interpretare GG:**
        * Șansa matematică reală ca **ambele echipe să marcheze (GG)** este de **{p_gg_real:.2f}%**.
        * Cota corectă fără marjă este **{c_gg_fair:.2f}**.
        * Dacă găsești la o casă de pariuri o cotă mai mare sau egală cu **{c_gg_fair:.2f}**, opțiunea **GG** este un **Value Bet**.
        """)