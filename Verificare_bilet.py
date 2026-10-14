import streamlit as st
import pandas as pd
import io
import re
from pypdf import PdfReader

# Configurare interfață Streamlit
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF Superbet sau dă Paste la text mai jos</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

def parseaza_pdf_superbet(text_raw):
    """
    Parser dedicat pentru PDF-urile Superbet ("Pariurile mele.pdf").
    Extrage exact echipele, pronosticurile curate și cotele fiecărui meci.
    """
    # Curățăm caracterele speciale / pictogramele
    text_curat = text_raw.replace('', '').replace('', '').replace('', '')
    linii = [l.strip() for l in text_curat.split('\n') if l.strip()]
    
    # Excludem cuvintele de sistem și denumirile de ligi / reprize
    de_ignorat = [
        "BET BUILDER", "A ctiv", "Activ", "ST A TUS", "Status", 
        "COT Ă TOT A L Ă", "COTĂ TOTALĂ", "B A NI RE A LI", "BANI REALI",
        "CÂȘTIG POTENȚIAL", "Repriza", "International", "UEFA", "Youth League", 
        "Pariurile mele", "https://", "RON", "Sport", "Simplu", "Da", "Nu", "R1", "R2"
    ]
    
    # Căutăm startul meciurilor
    idx_start = 0
    for idx, l in enumerate(linii):
        if "A ctiv" in l or "Activ" in l:
            idx_start = idx + 1
            break
            
    linii_meciuri = linii[idx_start:]
    
    # Împărțim biletul în blocuri per meci
    blocuri_meci = []
    bloc_curent = []
    
    for linie in linii_meciuri:
        bloc_curent.append(linie)
        if "BET BUILDER" in linie or "https://" in linie:
            blocuri_meci.append(list(bloc_curent))
            bloc_curent = []
            
    if bloc_curent:
        blocuri_meci.append(bloc_curent)

    linii_rezultat = []

    for bloc in blocuri_meci:
        echipe = []
        cota = None
        pronosticuri = []
        
        for l in bloc:
            # Extragere cotă meci (ex: 1.45)
            if re.match(r"^\d+\.\d{2}$", l) and not cota:
                if float(l) < 50.0:
                    cota = l
                    continue
            
            este_zgomot = any(z.lower() in l.lower() for z in de_ignorat)
            este_numar = l.isdigit() or (l in ["0", "1", "2"])
            
            if not este_zgomot and not este_numar:
                # Verificăm dacă linia este o opțiune validă de pariu sau numele unei echipe
                if any(p in l for p in ["Interval", "goluri", "GG", "Peste", "Sub", "2-5"]):
                    if l not in pronosticuri:
                        pronosticuri.append(l)
                elif len(echipe) < 2:
                    echipe.append(l)

        if len(echipe) == 2 and cota:
            nume_meci = f"{echipe[0]} - {echipe[1]}"
            prono_text = " & ".join(pronosticuri) if pronosticuri else "GG sau Peste 2.5 & 2-5 goluri"
            linii_rezultat.append(f"{nume_meci} | {prono_text} | {cota}")

    return "\n".join(linii_rezultat)

# --- PASUL 1: INCĂRCARE PDF SAU INTRODUCERE TEXT ---
st.markdown("### 📋 Pasul 1: Încarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        reader = PdfReader(uploaded_file)
        pdf_text = ""
        for page in reader.pages:
            pdf_text += page.extract_text() + "\n"
        
        text_curatat = parseaza_pdf_superbet(pdf_text)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ PDF extras și formatat cu succes!")
        else:
            text_initial = pdf_text
            st.warning("⚠️ Am citit PDF-ul, dar te rugăm să verifici/editezi textul mai jos.")
            
    except Exception as e:
        st.error(f"Eroare la citirea fișierului PDF: {e}")

text_bilet = st.text_area(
    "Text formatat (verifică datele extrase mai jos):",
    value=text_initial if text_initial else "Slovan Bratislava U19 - Stuttgart U19 | GG sau Peste 2.5 & 2-5 goluri | 1.45\nAS Roma U19 - Real Madrid U19 | GG sau Peste 2.5 & 2-5 goluri | 1.45",
    height=150
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=8.50, step=0.50)

# --- PASUL 2: PROCESARE ȘI CALCUL ---
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        parti = [p.strip() for p in re.split(r'[|]', linie) if p.strip()]
        
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                cota = 1.50
        elif len(parti) == 2:
            nume = parti[0]
            prono = "Nespecificat"
            try:
                cota = float(parti[1].replace(',', '.'))
            except ValueError:
                cota = 1.50
        else:
            cota_match = re.search(r"[-+]?\d*[.,]\d+|\d+", linie)
            if cota_match:
                cota_str = cota_match.group().replace(',', '.')
                cota = float(cota_str)
                nume = linie.replace(cota_match.group(), "").strip()
                prono = "Eveniment"
            else:
                continue
                
        prob_reala = int((1 / cota) * 100 * 0.95)
        prob_reala = max(1, min(99, prob_reala))
        
        risc = "🟩 SAFE" if prob_reala >= 65 else ("🟨 MEDIUM" if prob_reala >= 40 else "🟥 RISK")
        
        lista_meciuri_temporara.append({
            "Meci / Eveniment": nume,
            "Pronostic": prono,
            "Cotă": cota,
            "Probabilitate": f"{prob_reala}%",
            "Nivel Risc": risc,
            "prob_num": prob_reala
        })
        
    st.session_state.bilet_automat = lista_meciuri_temporara
    st.success(f"✅ Am identificat și procesat {len(lista_meciuri_temporara)} meciuri de pe bilet!")

# --- PASUL 3: AFIȘARE REZULTATE ---
if st.session_state.bilet_automat:
    st.write("---")
    st.markdown("### 🔍 Anatomia Biletului Tău:")
    
    df_afisare = pd.DataFrame(st.session_state.bilet_automat)
    st.dataframe(df_afisare.drop(columns=["prob_num"]), use_container_width=True)
    
    cota_totala = 1.0
    prob_compusa = 1.0
    for m in st.session_state.bilet_automat:
        cota_totala *= m["Cotă"]
        prob_compusa *= (m["prob_num"] / 100)
        
    procent_final = round(prob_compusa * 100, 2)
    castig_potential = cota_totala * miza_simulata
    valoare_matematica = castig_potential * (procent_final / 100)

    st.write("---")
    st.markdown("<h3 style='text-align: center;'>🏆 Rezultate Calcul Matematice</h3>", unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric(label="📈 COTĂ TOTALĂ", value=f"{cota_totala:.2f}")
    with c2:
        st.metric(label="🎯 PROBABILITATE REUȘITĂ", value=f"{procent_final}%")
    with c3:
        st.metric(label="💰 CÂȘTIG POTENȚIAL", value=f"{castig_potential:.2f} RON")
        
    st.write("")
    if procent_final >= 50:
        st.success(f"🟩 **Verdict: Bilet Foarte Solid.** Din punct de vedere matematic, valoarea reală estimată este de **{valoare_matematica:.2f} RON**.")
    elif 15 <= procent_final < 50:
        st.warning(f"🟨 **Verdict: Bilet Echilibrat (Combo).** Șanse moderate ({procent_final}%). Valoarea reală ponderată este de **{valoare_matematica:.2f} RON**.")
    else:
        st.error(f"🟥 **Verdict: Tip 'Bombă' (Risc Maxim).** Probabilitate mică de **{procent_final}%**.")

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df_afisare.drop(columns=["prob_num"]).to_excel(writer, index=False, sheet_name='Analiza Procente')
    excel_data = buffer.getvalue()
    
    st.write("")
    st.download_button(
        label="🟢 EXPORTĂ BILETUL ÎN EXCEL",
        data=excel_data,
        file_name="Analiza_VIP_Bilet.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
