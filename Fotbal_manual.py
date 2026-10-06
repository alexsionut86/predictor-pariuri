import streamlit as st
import pandas as pd
import io

try:
    import plotly.express as px
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

st.set_page_config(page_title="Fotbal VIP Pro", layout="wide", page_icon="⚽")

if "bilet_fotbal_premium" not in st.session_state:
    st.session_state["bilet_fotbal_premium"] = []

st.markdown("<h1 style='text-align: center;'>⚽ Algoritm Fotbal VIP Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Analiză completă: Goluri, GG, Peste 2.5, Cornere și Cartonașe cu procente.</p>", unsafe_allow_html=True)
st.write("---")

def proceseaza_meci(meci_nume, liga_nume, data_ora, c1, cX, c2):
    probabilitate_baza = int((1 / c1) * 100) if c1 > 0 else 0
    prob_x = int((1 / cX) * 100) if cX > 0 else 0
    prob_2 = int((1 / c2) * 100) if c2 > 0 else 0

    if c1 <= 1.65:
        verdict_text, verdict_emoji = "FAVORIT CLAR", "🟩"
        safe, medium, risk = "Șansă dublă 1X", "⚽ Gol în 1R (Peste 0.5 1R)", "1 Solist & Peste 2.5 Goluri"
        p_safe, p_medium, p_risk = min(92, probabilitate_baza + 25), min(85, probabilitate_baza + 15), max(45, probabilitate_baza - 15)
        p_gg, p_peste25 = min(78, max(40, 100 - probabilitate_baza + 15)), min(88, max(45, probabilitate_baza + 10))
        cornere_text = f"🚩 Peste 5.5 Cornere gazde — {min(88, probabilitate_baza + 20)}% șanse"
        cartonase_text = f"🟨 Cele mai multe cartonașe: Oaspeții — {min(82, probabilitate_baza + 15)}% șanse"

    elif 1.65 < c1 <= 2.30:
        verdict_text, verdict_emoji = "MECI ECHILIBRAT", "🟨"
        safe, medium, risk = "Interval Goluri 1-4", "⚽ Gol 1R SAU Ambele marchează (GG)", "X final (Egalitate)"
        p_safe, p_medium, p_risk = 82, 74, prob_x
        p_gg, p_peste25 = 68, 58
        cornere_text = "🚩 Peste 8.5 Cornere în total meci — 76% șanse"
        cartonase_text = "🟨 Peste 4.5 Cartonașe în meci — 84% șanse"

    else:
        verdict_text, verdict_emoji = "OUTSIDER / HAZARD", "🟥"
        safe, medium, risk = "Peste 1.5 Goluri", "Șansă dublă X2", "2 Solist"
        p_safe, p_medium, p_risk = 85, prob_2 + 20, prob_2
        p_gg, p_peste25 = min(75, max(35, prob_2 + 25)), min(80, max(40, prob_2 + 15))
        cornere_text = "🚩 Peste 3.5 Cornere în total — 70% șanse"
        cartonase_text = "🟨 Gazdele primesc primul cartonaș — 78% șanse"

    return {
        "Data / Ora": data_ora,
        "Meci": meci_nume,
        "Ligă": liga_nume,
        "Cota 1": f"{c1:.2f}",
        "Cota X": f"{cX:.2f}",
        "Cota 2": f"{c2:.2f}",
        "Verdict": f"{verdict_emoji} {verdict_text}",
        "Verdict Simple": verdict_text,
        "🛡️ Safe": f"{safe} ({max(1, min(99, p_safe))}%)",
        "⚡ Medium": f"{medium} ({max(1, min(99, p_medium))}%)",
        "🔥 Risk": f"{risk} ({max(1, min(99, p_risk))}%)",
        "⚽ GG (Ambele înscriu)": f"GG ({max(1, min(99, p_gg))}%)",
        "⚽ Peste 2.5 Goluri": f"> 2.5 ({max(1, min(99, p_peste25))}%)",
        "p_safe": max(1, min(99, p_safe)),
        "p_medium": max(1, min(99, p_medium)),
        "p_risk": max(1, min(99, p_risk)),
        "p_gg": max(1, min(99, p_gg)),
        "p_peste25": max(1, min(99, p_peste25)),
        "🚩 Cornere": cornere_text,
        "🟨 Cartonașe": cartonase_text
    }

mod_incarcare = st.radio("Alege modul de introducere date:", ["Manual (Un singur meci)", "Fișier (Meciuri multiple din Excel/CSV)"], horizontal=True)

if mod_incarcare == "Manual (Un singur meci)":
    st.markdown("### ➕ Date Meci")
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        meci_nume = st.text_input("Nume Meci:", "FCSB vs Rapid")
    with col_d2:
        liga_nume = st.text_input("Competiție / Ligă:", "Superliga")

    data_ora_input = st.text_input("Data și Ora (ex: 12.10.2026 21:00 sau Azi 20:30):", "Azi 21:00")

    st.markdown("### 📉 Cote 1X2:")
    col1, col2, col3 = st.columns(3)
    with col1:
        c1 = st.number_input("Cotă 1", min_value=1.01, value=1.50, step=0.01, format="%.2f")
    with col2:
        cX = st.number_input("Cotă X", min_value=1.01, value=3.80, step=0.01, format="%.2f")
    with col3:
        c2 = st.number_input("Cotă 2", min_value=1.01, value=5.50, step=0.01, format="%.2f")

    st.write("---")
    
    rezultat = proceseaza_meci(meci_nume, liga_nume, data_ora_input, c1, cX, c2)
    
    st.markdown("<h3 style='text-align: center;'>📊 Predicții Găsite</h3>", unsafe_allow_html=True)
    st.markdown(f"<h4 style='text-align: center;'>Verdict: {rezultat['Verdict']}</h4>", unsafe_allow_html=True)
    st.write("")

    col_a, col_b = st.columns(2)
    with col_a:
        st.info("🛡️ **Varianta Safe:** " + str(rezultat["🛡️ Safe"]))
        st.warning("⚡ **Varianta Medium:** " + str(rezultat["⚡ Medium"]))
        st.error("🔥 **Varianta Risk:** " + str(rezultat["🔥 Risk"]))
    with col_b:
        st.success("⚽ **Ambele Înscriu (GG):** " + str(rezultat["⚽ GG (Ambele înscriu)"]))
        st.success("⚽ **Total Goluri:** " + str(rezultat["⚽ Peste 2.5 Goluri"]))

    st.write("")
    st.markdown("#### 🎯 Opțiuni Speciale:")
    st.markdown("> " + str(rezultat["🚩 Cornere"]) + "\n\n> " + str(rezultat["🟨 Cartonașe"]))
    st.write("")

    if st.button("📥 SALVEAZĂ MECIUL ÎN TABEL", use_container_width=True):
        st.session_state.bilet_fotbal_premium.append(rezultat)
        st.toast(f"✅ Salvat complet: {meci_nume}")

else:
    st.markdown("### 📁 Încarcă fișierul cu meciuri")
    st.info("Pentru ca Data/Ora să fie extrasă, fișierul (CSV/Excel) trebuie să aibă o coloană cu denumiri precum: **Data / Ora**, **Data**, **Ora** sau **Date**.")
    
    uploaded_file = st.file_uploader("Alege fișierul Excel sau CSV", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                try:
                    df_input = pd.read_csv(uploaded_file, sep=None, engine='python', encoding='utf-8-sig')
                except Exception:
                    uploaded_file.seek(0)
                    df_input = pd.read_csv(uploaded_file, sep=None, engine='python')
            else:
                df_input = pd.read_excel(uploaded_file)
                
            df_input.columns = df_input.columns.astype(str).str.replace('\ufeff', '').str.strip()
            cols_map = {str(col).lower().strip(): col for col in df_input.columns}

            # Verificare existență coloană Data/Ora
            data_col_found = None
            for candidate in ["data / ora", "data/ora", "data ora", "data_ora", "date", "time", "data", "ora", "dată", "oră", "schedule", "start"]:
                if candidate in cols_map:
                    data_col_found = cols_map[candidate]
                    break

            if data_col_found:
                st.success(f"✅ Am detectat coloana de dată: **'{data_col_found}'**")
            else:
                st.warning("⚠️ Nu am găsit o coloană pentru dată/oră în fișier! Se va folosi valoarea implicită '-'. Adaugă o coloană numită **Data** sau **Data / Ora** în fișier.")

            st.write("Aperçu date încărcate:", df_input.head())
            
            if st.button("🚀 PROCESEAZĂ TOATE MECIURILE", use_container_width=True):
                meciuri_procesate = 0
                
                for _, row in df_input.iterrows():
                    data_ora_val = "-"
                    if data_col_found:
                        val = row.get(data_col_found)
                        if pd.notna(val) and str(val).strip() != "":
                            data_ora_val = str(val).strip()
                    
                    if data_ora_val == "-" and "data" in cols_map and "ora" in cols_map:
                        d_val, o_val = row.get(cols_map["data"]), row.get(cols_map["ora"])
                        if pd.notna(d_val) or pd.notna(o_val):
                            data_ora_val = f"{str(d_val) if pd.notna(d_val) else ''} {str(o_val) if pd.notna(o_val) else ''}".strip()

                    meci_val = "Meci Necunoscut"
                    for candidate in ["meci", "match", "meciuri", "echipe", "event"]:
                        if candidate in cols_map:
                            meci_val = str(row.get(cols_map[candidate]))
                            break
                    if meci_val == "Meci Necunoscut" and len(row) > 0:
                        meci_val = str(list(row.values)[0])

                    liga_val = "Ligă"
                    for candidate in ["liga", "ligă", "competition", "competitie", "league"]:
                        if candidate in cols_map:
                            liga_val = str(row.get(cols_map[candidate]))
                            break

                    c1_key = cols_map.get("cota 1", cols_map.get("cota1", cols_map.get("1", None)))
                    cX_key = cols_map.get("cota x", cols_map.get("cotax", cols_map.get("x", None)))
                    c2_key = cols_map.get("cota 2", cols_map.get("cota2", cols_map.get("2", None)))

                    c1_val = float(str(row.get(c1_key, 1.5) if c1_key else 1.5).replace(",", "."))
                    cX_val = float(str(row.get(cX_key, 3.0) if cX_key else 3.0).replace(",", "."))
                    c2_val = float(str(row.get(c2_key, 3.0) if c2_key else 3.0).replace(",", "."))

                    res = proceseaza_meci(
                        meci_nume=meci_val,
                        liga_nume=liga_val,
                        data_ora=data_ora_val,
                        c1=c1_val,
                        cX=cX_val,
                        c2=c2_val
                    )
                    st.session_state.bilet_fotbal_premium.append(res)
                    meciuri_procesate += 1
                    
                st.success(f"✅ Au fost procesate cu succes {meciuri_procesate} meciuri!")
                st.rerun()
        except Exception as e:
            st.error(f"Eroare la citirea fișierului: {e}")

st.write("---")

if st.session_state.bilet_fotbal_premium:
    df = pd.DataFrame(st.session_state.bilet_fotbal_premium)
    
    st.markdown("### 📋 Istoric Tabel Meciuri")
    
    cols_display = [
        "Data / Ora", "Meci", "Ligă", "Cota 1", "Cota X", "Cota 2", "Verdict", 
        "🛡️ Safe", "⚡ Medium", "🔥 Risk", 
        "⚽ GG (Ambele înscriu)", "⚽ Peste 2.5 Goluri", 
        "🚩 Cornere", "🟨 Cartonașe"
    ]
    st.dataframe(df[cols_display], use_container_width=True)

    if HAS_PLOTLY:
        st.markdown("### 📈 Vizualizare Grafică Date")
        col_g1, col_g2 = st.columns(2)

        with col_g1:
            fig_verdict = px.pie(
                df, names="Verdict Simple", title="Ponderea Verdictelor",
                color="Verdict Simple",
                color_discrete_map={"FAVORIT CLAR": "#2ecc71", "MECI ECHILIBRAT": "#f1c40f", "OUTSIDER / HAZARD": "#e74c3c"},
                hole=0.4
            )
            st.plotly_chart(fig_verdict, use_container_width=True)

        with col_g2:
            df_melted_goals = df.melt(id_vars=["Meci"], value_vars=["p_gg", "p_peste25"], var_name="Tip Goluri", value_name="Procent (%)")
            df_melted_goals["Tip Goluri"] = df_melted_goals["Tip Goluri"].map({"p_gg": "⚽ GG", "p_peste25": "⚽ Peste 2.5"})
            fig_bar_goals = px.bar(df_melted_goals, x="Meci", y="Procent (%)", color="Tip Goluri", barmode="group", title="Șanse GG și Peste 2.5 per Meci")
            st.plotly_chart(fig_bar_goals, use_container_width=True)

    st.write("---")

    if st.button("🗑️ Resetează Tabelul", use_container_width=False):
        st.session_state.bilet_fotbal_premium = []
        st.rerun()
        
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df[cols_display].to_excel(writer, index=False, sheet_name='Fotbal VIP Complet')
    date_excel = buffer.getvalue()
    
    st.download_button(
        label="🟢 DESCARCĂ EXCEL COMPLET (.xlsx)",
        data=date_excel,
        file_name="Bilet_Fotbal_Premium.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
