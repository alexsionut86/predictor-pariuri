import streamlit as st
import pandas as pd
import io
import re
import pdfplumber

# Configurare interfață Streamlit
st.set_page_config(page_title="Scanner Probabilități Pro", layout="wide", page_icon="📊")

st.markdown("<h1 style='text-align: center;'>📊 Verificator Automat Bilet VIP</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #4CAF50;'>Încarcă biletul PDF Superbet sau dă Paste la text mai jos</p>", unsafe_allow_html=True)
st.write("---")

if "bilet_automat" not in st.session_state:
    st.session_state.bilet_automat = []

if "cod_bilet_detecat" not in st.session_state:
    st.session_state.cod_bilet_detecat = ""

def curata_text_parazit(text):
    """ Elimină textele de sistem/sumă/coduri parazite ce apar în PDF. """
    text = re.sub(r"CÂȘTIG\s+POTENȚIAL.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"COTA\s+TOTALA.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"BANI\s+REALI.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"SUPERBONUS.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+\.\d{2}\s*RON", "", text)
    return text.strip()

def extrage_meciuri_pdfplumber_perfect(uploaded_file):
    """
    Extragere exactă: ignoră codul biletului din meciuri, extrage codul biletului separat
    și asociază cele 9 meciuri reale cu cotele lor exacte.
    """
    with pdfplumber.open(uploaded_file) as pdf:
        text_fara_layout = ""
        text_cu_layout = ""
        for page in pdf.pages:
            text_fara_layout += (page.extract_text() or "") + "\n"
            text_cu_layout += (page.extract_text(layout=True) or "") + "\n"

    # Căutare cod bilet Superbet (ex: 8910-YYHUV7)
    cod_match = re.search(r"\b([0-9A-Z]{4,5}-[0-9A-Z]{4,7})\b", text_fara_layout)
    if cod_match:
        st.session_state.cod_bilet_detecat = cod_match.group(1)

    # 1. Extragere cote reale (numere de tip 1.xx)
    linii_raw = [l.strip() for l in text_fara_layout.split('\n') if l.strip()]
    cote_reale = []
    for l in linii_raw:
        if re.match(r"^1\.\d{2}$", l):
            cote_reale.append(float(l))

    # 2. Extragere meciuri și eliminare zgomot/coduri de bilet
    linii_layout = [l.strip() for l in text_cu_layout.split('\n') if l.strip()]
    
    zgomot = [
        "International", "UEFA", "Liga", "Campioni", "Astazi", "Atazi", "Astan", "Aziz",
        "STATUS", "Activ", "Pariurile mele", "https", "COTA TOTALA", "BANI REALI",
        "SUPERBONUS", "CASTIG POTENTIAL", "RON", "Sport", "Simplu", "10/14/", "1/1", "Atzi"
    ]

    linii_curate = []
    for l in linii_layout:
        l_sanitizat = curata_text_parazit(l)
        este_cod_bilet = bool(re.match(r"^[0-9A-Z]{4,5}-[0-9A-Z]{4,7}$", l_sanitizat))
        
        if l_sanitizat and not este_cod_bilet and not any(z.lower() in l_sanitizat.lower() for z in zgomot) and not re.match(r"^1\.\d{2}$", l_sanitizat):
            linii_curate.append(l_sanitizat)

    # 3. Reconstruire meciuri
    i = 0
    n = len(linii_curate)
    echipe_prono_gasite = []

    while i < n:
        l = linii_curate[i]
        
        if "-" in l and len(l.split("-")) == 2 and not re.match(r"^\d+-\d+$", l):
            meci_nume = l.strip()
            prono_detaliu = "2-5"
            
            if i + 1 < n and (re.match(r"^\d+-\d+$", linii_curate[i+1]) or "Interval" in linii_curate[i+1]):
                prono_detaliu = linii_curate[i+1]
                i += 1
                
            echipe_prono_gasite.append((meci_nume, prono_detaliu))
        elif i + 2 < n:
            e1 = linii_curate[i]
            e2 = linii_curate[i+1]
            p = linii_curate[i+2]
            
            if (re.match(r"^\d+-\d+$", p) or "Interval" in p or "GG" in p) and not re.match(r"^\d+-\d+$", e1):
                echipe_prono_gasite.append((f"{e1} - {e2}", p))
                i += 2
        i += 1

    # 4. Potrivire 1-la-1 între meciuri și cote
    rezultat = []
    for idx, (meci_nume, prono_text) in enumerate(echipe_prono_gasite):
        cota_val = cote_reale[idx] if idx < len(cote_reale) else 1.35
        meci_nume = re.sub(r"\s+", " ", meci_nume)
        prono_text = re.sub(r"\s+", " ", prono_text)
        rezultat.append(f"{meci_nume} | {prono_text} | {cota_val:.2f}")

    return "\n".join(rezultat)

# --- PASUL 1: ÎNCĂRCARE PDF SAU TEXT ---
st.markdown("### 📋 Pasul 1: Încarcă biletul PDF sau lipeste textul")

uploaded_file = st.file_uploader("📄 Încarcă biletul în format PDF (Superbet)", type=["pdf"])

text_initial = ""

if uploaded_file is not None:
    try:
        text_curatat = extrage_meciuri_pdfplumber_perfect(uploaded_file)
        
        if text_curatat:
            text_initial = text_curatat
            st.success("✅ PDF procesat cu succes! Meciurile și cotele au fost asociate.")
        else:
            st.warning("⚠️ Verifică/completează datele în caseta de text de mai jos.")
            
    except Exception as e:
        st.error(f"Eroare la citirea PDF-ului: {e}")

text_bilet = st.text_area(
    "Text formatat automat (verifică datele extrase):",
    value=text_initial if text_initial else "LASK Linz - Liverpool | 2-5 | 1.34\nFeyenoord Rotterdam - Como | 2-5 | 1.34",
    height=220
)

col_miza, col_btn = st.columns([1, 2])
with col_miza:
    miza_simulata = st.number_input("💰 Introdu miza biletului (RON):", min_value=1.0, value=5.00, step=0.50)

# --- PASUL 2: PROCESARE ȘI CALCUL ---
if st.button("⚡ SCANEAZĂ BILETUL ȘI CALCULEAZĂ PROCENTELE", use_container_width=True):
    linii = text_bilet.strip().split("\n")
    lista_meciuri_temporara = []
    
    for linie in linii:
        if not linie.strip():
            continue
        
        parti = [p.strip() for p in linie.split('|') if p.strip()]
        
        if len(parti) >= 3:
            nume = parti[0]
            prono = parti[1]
            try:
                cota = float(parti[2].replace(',', '.'))
            except ValueError:
                cota = 1.35
        elif len(parti) == 2:
            nume = parti[0]
            prono = parti[1]
            cota = 1.35
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

    # --- METODA 1: GENERARE LINK DIRECT SUPERBET ---
    st.write("---")
    st.markdown("### 🎟️ Deschide Biletul Direct pe Superbet")
    
    cod_input = st.text_input(
        "Cod bilet Superbet:",
        value=st.session_state.cod_bilet_detecat if st.session_state.cod_bilet_detecat else "8910-YYHUV7"
    )
    
    if cod_input:
        cod_curat = cod_input.strip().upper()
        url_superbet = f"https://superbet.ro/pariurile-mele/deschise?code={cod_curat}"
        
        st.markdown(
            f'''
            <a href="{url_superbet}" target="_blank" style="text-decoration: none;">
                <button style="
                    background-color: #E50914;
                    color: white;
                    padding: 14px 20px;
                    border: none;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    cursor: pointer;
                    width: 100%;">
                    🚀 DESCHIDE BILETUL ({cod_curat}) DIRECT ÎN SUPERBET
                </button>
            </a>
            ''',
            unsafe_allow_html=True
        )

    # --- EXPORT EXCEL ---
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
