import streamlit as st
import pandas as pd
import io
import pypdf
import re

# Configurare interfață mobil premium
st.set_page_config(page_title="Scanner Bilet PDF Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator PDF Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF descărcat din agenție pentru analiză instantă</p>", unsafe_allow_html=True)
st.write("---")

# Inițializare listă meciuri în memoria aplicației
if "bilet_pdf_date" not in st.session_state:
    st.session_state.bilet_pdf_date = []

# --- ZONA DE ÎNCĂRCARE FIȘIER PDF ---
st.markdown("### 📂 Pasul 1: Încarcă fișierul PDF al biletului")
fisier_pdf = st.file_uploader("Trage biletul tău PDF aici (Format salvat din aplicație):", type=["pdf"])

miza_bilet = st.number_input("💰 Miza biletului (RON) - [Dacă nu e extrasă automat]:", min_value=1.0, value=10.0, step=1.0)

if fisier_pdf is not None:
    if st.button("⚡ SCANEAZĂ ȘI EXTRAGE DATELE DIN PDF", use_container_width=True):
        try:
            # Citire text din PDF
            cititor = pypdf.PdfReader(fisier_pdf)
            text_complet = ""
            for pagina in cititor.pages:
                text_complet += pagina.extract_text() + "\n"
            
            # --- ALGORITM INTELIGENT DE PARSARE TEXT (Specific Superbet/Formate Românești) ---
            linii = text_complet.split("\n")
            meciuri_detectate = []
            
            # Căutăm miza automat în text dacă există (ex: "BANI REALI 10.00 RON")
            miza_match = re.search(r"(?:BANI REALI|Miză totală|Miza)\s*([\d.]+)", text_complet, re.IGNORECASE)
            if miza_match:
                miza_bilet = float(miza_match.group(1))
            
            # Identificăm cotele din bilet (toate numerele de tipul 1.71, 1.62 etc.)
            cote_gasite = [float(c) for c in re.findall(r"\b\d\.\d{2}\b", text_complet)]
            
            # Extragere meciuri din structura textului
            # Căutăm linii care conțin echipe sau indicii de tip pariu (ex: Pauză sau Final, Egalitate, Peste/Sub)
            evenimente_text = []
            pronosticuri_text = []
            
            for i, linie in enumerate(linii):
                # Dacă linia conține indicii de tip pariu
                if "Pauză sau Final" in linie or "Peste" in linie or "Sub" in linie or "GG" in linie or "Interval" in linie:
                    pronosticuri_text.append(linie.strip())
                    # De obicei, numele meciului/echipelor se află cu 2-4 linii mai sus în PDF-urile standard
                    nume_meci_estimat = "Meci Detectat"
                    for j in range(1, 5):
                        if i - j >= 0 and len(linii[i-j].strip()) > 3 and not any(x in linii[i-j] for x in ["Astăzi", "Meci", "STATUS", "COTĂ", "RON"]):
                            nume_meci_estimat = linii[i-j].strip()
                            break
                    evenimente_text.append(nume_meci_estimat)

            # Corelăm datele găsite cu cotele extrase în ordine cronologică
            min_length = min(len(evenimente_text), len(cote_gasite))
            
            if min_length == 0:
                # Strategie de rezervă dacă structura PDF-ului e diferită: extragem doar cotele brute detectate
                for idx, cota in enumerate(cote_gasite):
                    # Evităm să luăm cota totală din greșeală (de obicei e mult mai mare)
                    if cota < 10.0:
                        prob_reala = int((1 / cota) * 100 * 0.95)
                        prob_reala = max(1, min(99, prob_reala))
                        meciuri_detectate.append({
                            "Meci / Eveniment": f"Eveniment #{idx + 1}",
                            "Pronostic": "Preluat din PDF",
                            "Cotă": cota,
                            "Probabilitate": f"{prob_reala}%",
                            "Nivel Risc": "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK"),
                            "prob_num": prob_reala
                        })
            else:
                for idx in range(min_length):
                    cota = cote_gasite[idx]
                    prono = pronosticuri_text[idx] if idx < len(pronosticuri_text) else "Pronostic"
                    meci = evenimente_text[idx] if idx < len(evenimente_text) else f"Meci #{idx+1}"
                    
                    prob_reala = int((1 / cota) * 100 * 0.95)
                    prob_reala = max(1, min(99, prob_reala))
                    
                    meciuri_detectate.append({
                        "Meci / Eveniment": meci,
                        "Pronostic": prono,
                        "Cotă": cota,
                        "Probabilitate": f"{prob_reala}%",
                        "Nivel Risc": "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK"),
                        "prob_num": prob_reala
                    })
            
            st.session_state.bilet_pdf_date = meciuri_detectate
            st.success(f"✅ Scanare completă! Am identificat {len(meciuri_detectate)} evenimente în bilet.")
            
        except Exception as e:
            st.error(f"Eroare la procesarea fișierului PDF: {str(e)}. Asigură-te că PDF-ul este cel original generat de aplicația de pariuri.")

# --- AFIȘARE TABEL REZULTATE ȘI PROCENTE COMPUSE ---
if st.session_state.bilet_pdf_date:
    st.write("---")
    st.markdown("### 🔍 Anatomia Matematica a Biletului Scanat:")
    
    df_pdf = pd.DataFrame(st.session_state.bilet_pdf_date)
    st.dataframe(df_pdf.drop(columns=["prob_num"]), use_container_width=True)
    
    # Resetare bilet
    if st.button("🗑️ Șterge datele / Încarcă alt bilet"):
        st.session_state.bilet_pdf_date = []
        st.rerun()

    # Calcul matematic cumulativ
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_pdf_date:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_bilet
    valoare_reala_ponderata = castig_potential * (procent_final / 100)

    # --- PANOU REZULTATE FINALE ---
    st.write("---")
    st.markdown("<h3 style='text-align: center;'>🏆 Rezultate Calcul Matematice (Din PDF)</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ EXTRACTĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ BILET", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL ESTIMAT", value=f"{castig_potential:.2f} RON")
        
    st.write("")
    if procent_final >= 50:
        st.success(f"🟩 **Verdict: Bilet Foarte Solid.** Valoarea reală ponderată a biletului tău este de **{valoare_reala_ponderata:.2f} RON**. Șanse excelente!")
    elif 15 <= procent_final < 50:
        st.warning(f"🟨 **Verdict: Bilet Echilibrat (Combo).** Șanse moderate ({procent_final}%). Valoarea reală ponderată este de **{valoare_reala_ponderata:.2f} RON**. Gestionați miza cu atenție!")
    else:
        st.error(f"🟥 **Verdict: Tip 'Bombă' (Risc Maxim).** Probabilitate mică de doar **{procent_final}%**. Valoarea reală scade la **{valoare_reala_ponderata:.2f} RON**. Recomandat exclusiv pentru distracție pe mize minime.")

    # Export Excel rapid
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_pdf.drop(columns=["prob_num"]).to_excel(writer, index=False, sheet_name='Analiza PDF')
    excel_data = buffer.getvalue()
    
    st.download_button(
        label="🟢 EXPORTĂ ANALIZA PDF ÎN EXCEL",
        data=excel_data,
        file_name="Analiza_VIP_Bilet_PDF.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )